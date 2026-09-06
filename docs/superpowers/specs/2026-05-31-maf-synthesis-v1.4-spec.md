# Design Specification: MAF Synthesis — Security Patches & Pattern Adoption v1.4

**Revised:** 2026-05-31 (post document review — API corrections applied)  
**Predecessor:** v1.3 spec (`docs/superpowers/specs/2026-05-30-hardened-control-plane-design.md`)  
**Decision authority:** ADR-007 (`docs/ADRs/007_maf_adapter_runtime_decision.md`)

---

## Implementation Compatibility Notes

Five independent document reviewers (GPT-5.5, Grok, Opus, Gemini, GPT-4o) found that the original plan described idealized future APIs rather than the actual current code. These notes document every mismatch so implementation is grounded in reality.

| Issue | Original Spec Said | Reality |
|-------|--------------------|---------|
| Task 1 path traversal | Replace existing `startswith()` check | `sandbox_runner.py` has NO path validation — `_assert_under_root()` is a new addition |
| Task 2 auth gate args | `args.db_path`, `args.approval_id`, etc. | `build_parser()` has none of these args — Step 2.0 must add them first |
| Task 2 auth signature | Keyword-arg form | Real signature: `check_dispatch_authorization(conn, approval_id, action, target_path, spec_path, envelope, key, nonce_cache) -> tuple[bool, str]` |
| Task 3 API | `create_task()`, `lease_task(conn, sid, agent)` returning task object | Real API: `add_task(conn, task_id, session_id, ...)`, `lease_task(conn, task_id, subagent_id) -> bool` |
| Task 3 premium | No `is_premium` / `requires_premium` column | `tasks` table has no premium column — design decision required |
| Task 4 WAL | `PRAGMA wal_checkpoint(PASSIVE)` to check size | PASSIVE is itself a checkpoint op — just call TRUNCATE directly after transaction |
| AGT import | `from agent_os.integrations.python_adapter import PythonDispatchGovernance` | Unverified — treat Task 7 as evaluation-first |

---

## 1. Executive Summary

**Phase 0 — Security Patches (v1.4):** Five critical/high defects found by the red team in the v1.3 control plane, plus one missed defect (`run_hygienic()` missing `cwd`). These are not optional.

**Phase 1 — MAF Pattern Adoption (v1.4/v1.5 boundary):** Four MAF-validated patterns ported to Python without adopting MAF as a dependency. Alias index and handoff envelope (Tasks 8–9) ship in v1.4. Skill scoping and OpenTelemetry/AGT (Tasks 10–11) target v1.5.

**Phase 2 — MAF Adapter Evaluation (v1.5):** Time-boxed HarnessAgent prototype.

---

## 2. Phase 0: Security Patches

### 2.1 Add Path Traversal Enforcement — `sandbox_runner.py` (CRITICAL)

**Context:** The current `sandbox_runner.py` has NO path validation on file I/O operations. The v1.3 design assumed path enforcement existed; it was not implemented. The vulnerability class (sibling-prefix bypass) was identified by comparing against the C# `WorkspaceTools` reference:

```
Allowed root: /tmp/work
Resolved path: /tmp/work_evil/file.txt
startswith("/tmp/work") → True   ← would be bypassed if check existed
```

**Fix:** Add `_assert_under_root()` as a new module-level helper. This is not replacing an existing check — it is new enforcement that must be called at every file-access boundary added in future work:

```python
def _assert_under_root(full: Path, root: Path, label: str = "path") -> None:
    """Fail-closed path boundary check. resolve() both paths before calling."""
    try:
        full.resolve().relative_to(root.resolve())
    except ValueError:
        raise PermissionError(
            f"Path traversal rejected: {full} is outside {root} ({label})"
        )
```

**Critical:** Always call `full.resolve()` and `root.resolve()` before `relative_to()`. Without `resolve()`, symlinks can escape the boundary — a symlink inside the allowed root can point outside it.

**Files:** `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`  
**Test:** New `test_path_traversal_sibling_prefix.py` — tests `_assert_under_root()` directly.

---

### 2.2 Wire Authorization Gate into `dispatch.py main()` (CRITICAL)

**Context:** `check_dispatch_authorization()` exists at line 195 of `dispatch.py` and is fully implemented. `main()` at line 267 never calls it. The gate is defined but not enforced.

**Real function signature (must match):**
```python
def check_dispatch_authorization(
    conn: sqlite3.Connection,
    approval_id: str,
    action: str,
    target_path: str | None,
    spec_path: str | None,
    envelope: dict,
    key: bytes,
    nonce_cache: OrderedDict,
) -> tuple[bool, str]:
```

Returns `(True, "")` on success, `(False, reason)` on failure. Does not raise — caller must handle the bool.

**Step 2.0 prerequisite — extend `build_parser()`:** Before the gate can be wired into `main()`, the parser needs the authorization arguments. Add to `build_parser()`:

```python
parser.add_argument("--db-path", required=True,
    help="Path to active_session.sqlite")
parser.add_argument("--approval-id", required=True,
    help="UUID of the active approval record")
parser.add_argument("--action", required=True,
    help="Action being dispatched (e.g. 'write_file', 'run_agent')")
parser.add_argument("--target-path", default=None,
    help="File path target for path allowlist check")
parser.add_argument("--spec-path", default=None,
    help="Path to the spec document for hash integrity check")
parser.add_argument("--envelope-json", required=True,
    help="JSON-serialized HMAC envelope from sandbox_runner")
parser.add_argument("--hmac-key-path", required=True,
    help="Path to the session HMAC key file (.key)")
```

**Step 2.1 — wire gate as first statement in `main()`:**

```python
def main() -> None:
    args = build_parser().parse_args()

    # Authorization gate — fail-closed. No dispatch without valid approval + HMAC.
    conn = init_db(args.db_path)
    key = load_session_key(Path(args.hmac_key_path))
    envelope = json.loads(args.envelope_json)
    nonce_cache: OrderedDict = OrderedDict()

    ok, reason = check_dispatch_authorization(
        conn=conn,
        approval_id=args.approval_id,
        action=args.action,
        target_path=args.target_path,
        spec_path=args.spec_path,
        envelope=envelope,
        key=key,
        nonce_cache=nonce_cache,
    )
    if not ok:
        print(f"Error: dispatch authorization failed: {reason}", file=sys.stderr)
        sys.exit(1)

    # Only reached if authorization passes
    ...
```

**Files:** `plugins/exploration-cycle-plugin/scripts/dispatch.py`  
**Tests:** Four tests must verify the CLI invocation subprocess is never reached on auth failure (use monkeypatch, not just exit code check).

---

### 2.3 Fix Per-Phase Premium Call Counter (HIGH)

**Context:** `lease_task()` gates on `sessions.premium_calls_used` (session-level). `record_premium_call(conn, session_id)` increments the same session counter. The variable `MAX_PREMIUM_CALLS_PER_PHASE` implies per-phase tracking but the implementation is per-session.

**Design decision:** The `tasks` table has no `requires_premium` column. Two options:

**Option A (recommended):** Add `requires_premium BOOLEAN DEFAULT 0` to tasks table. `lease_task()` only checks the premium gate when the task has `requires_premium = 1`. `record_premium_call()` accepts `phase_ordinal` and gates into a new `phase_metrics` table.

**Option B (simpler):** Rename `MAX_PREMIUM_CALLS_PER_PHASE` → `MAX_PREMIUM_CALLS_PER_SESSION` and document the per-session behavior. No schema change needed.

**Recommended schema addition (Option A):**

```sql
-- Add to SCHEMA_SQL (tasks table)
requires_premium BOOLEAN DEFAULT 0,

-- New table
CREATE TABLE IF NOT EXISTS phase_metrics (
    session_id TEXT NOT NULL,
    phase_ordinal INTEGER NOT NULL,
    premium_calls_used INTEGER DEFAULT 0,
    PRIMARY KEY (session_id, phase_ordinal),
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
```

**Migration note:** Any existing `active_session.sqlite` databases need the `requires_premium` column added. Add to `init_db()` after schema creation:

```python
try:
    conn.execute("ALTER TABLE tasks ADD COLUMN requires_premium BOOLEAN DEFAULT 0")
except sqlite3.OperationalError:
    pass  # Column already exists — migration already ran
```

**Updated `record_premium_call()` signature:**
```python
def record_premium_call(conn: sqlite3.Connection, session_id: str, phase_ordinal: int) -> None:
```

**Files:** `plugins/exploration-cycle-plugin/scripts/state_engine.py`

---

### 2.4 WAL Checkpoint Management (HIGH)

**Context:** `init_db()` enables WAL mode and verifies it. No checkpoint is ever called. On long sessions with many writes, the WAL file grows unbounded.

**Correct implementation:** Do not use `PRAGMA wal_checkpoint(PASSIVE)` to check size — PASSIVE is itself a checkpoint operation. Instead call TRUNCATE unconditionally after each session-complete boundary, outside any active transaction:

```python
def checkpoint_wal(conn: sqlite3.Connection) -> None:
    """Flush WAL to main DB. Must be called outside any active transaction."""
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
```

Call `checkpoint_wal(conn)` from:
- `commit_task_complete()` — after `_immediate_transaction` exits, not inside it
- `close_session()` — on graceful shutdown

**Files:** `plugins/exploration-cycle-plugin/scripts/state_engine.py`

---

### 2.5 Container Runs as Root (MEDIUM)

**Fix:**
```python
def _container_user_flag() -> list[str]:
    try:
        uid, gid = os.getuid(), os.getgid()
    except AttributeError:
        return ["--user", "65534:65534"]  # nobody:nogroup fallback for envs without getuid
    return ["--user", f"{uid}:{gid}"]
```

Insert `*_container_user_flag()` into `run_containerized()` command list.

**Files:** `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`

---

### 2.6 `run_hygienic()` Missing `cwd` Isolation (MEDIUM — new, not in v1 spec)

**Context:** `run_hygienic()` at line 51 builds a clean environment but inherits the parent process `cwd`. The parent's working directory may contain `.env` files, credentials, or source code outside the intended scope.

**Fix:**
```python
import tempfile

def run_hygienic(cmd: list, timeout: int = TIMEOUT_SECONDS,
                 extra_vars: dict | None = None) -> subprocess.CompletedProcess:
    env = _build_clean_env(extra_vars)
    cwd = tempfile.mkdtemp(prefix="agentic_sandbox_")
    try:
        proc = subprocess.Popen(cmd, shell=False, env=env, cwd=cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ...
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
```

**Files:** `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`

---

## 3. Phase 1: MAF Pattern Adoption (v1.4 boundary: Tasks 8–9 only)

### 3.1 Three-Way Alias Index for Agent Resolution (v1.4)

Adds `build_agent_index(agents_dir: Path) -> dict[str, Path]` to `dispatch.py`. No class needed.

```python
def build_agent_index(agents_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for md_file in sorted(agents_dir.glob("*.md")):
        stem = md_file.stem
        index[stem] = md_file
        if stem.endswith("-agent"):
            index.setdefault(stem[:-6], md_file)
        content = md_file.read_text(encoding="utf-8")
        m = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if m:
            index.setdefault(m.group(1).strip(), md_file)
    return index
```

---

### 3.2 Handoff Envelope Standardization (v1.4)

Empirically validated: 8-turn window, 300 chars/turn.

```python
def build_handoff_envelope(
    from_agent: str, to_agent: str, reason: str,
    user_message: str, transcript: list[tuple[str, str]],
    turns: int = 8, chars_per_turn: int = 300,
) -> str:
    context = "\n".join(
        f"{role}: {text[:chars_per_turn]}"
        for role, text in transcript[-turns:]
    )
    return (
        f"You are receiving a handoff from {from_agent}.\n"
        f"Reason: {reason}\n\n"
        f"Recent conversation:\n{context}\n\n"
        f"User's latest message: \"{user_message}\"\n\n"
        f"Continue according to your own agent manifest. "
        f"Do not repeat {from_agent}'s intake questions."
    )
```

---

### 3.3 OpenTelemetry Instrumentation (v1.5)

Deferred to v1.5. Reason: adding an external dependency after security patches are validated reduces blast radius if something goes wrong.

---

### 3.4 AGT Governance Adoption (v1.5 — evaluation-first)

**Critical note from document reviewers:** The AGT import path (`from agent_os.integrations.python_adapter import PythonDispatchGovernance`) has not been verified. It may not exist or may have a different path.

**Approach:** v1.5 Task begins with an evaluation spike (install, import, smoke test) before any production code is modified. If the adapter is not available, create a local `governance_adapter.py` façade that preserves the current deterministic checks and defers full AGT wiring to a separate ADR.

---

### 3.5 Per-Agent Skill Scoping with Budget Cap (v1.5)

Deferred to v1.5 alongside OpenTelemetry.

---

## 4. Phase 2: MAF 1.7.0 HarnessAgent Evaluation (v1.5)

**Time-box:** One session maximum. Output is a written report, not production code.

**Concrete metrics to capture:**

| Metric | Measurement method |
|--------|-------------------|
| Lines of code per dispatch | Count LOC in C# HarnessAgent path vs `dispatch.py main()` |
| Token usage per turn | Log input/output token counts from both approaches |
| Latency per dispatch | Wall-clock time from invocation to first token |
| Gemini compat | Does HarnessAgent work on Gemini free-tier without `thought_signature` workaround? |
| Provider swap failure modes | What breaks (silently vs. loudly) when switching Azure → Gemini |

**Threshold for opening new ADR:** HarnessAgent reduces dispatch LOC by >50% AND token overhead is <15% above current baseline.

---

## 5. Non-Goals (v1.4)

- Migrating primary runtime from Claude Code CLI to MAF
- Rewriting `exploration-workflow/SKILL.md` to use MAF workflow primitives  
- Adopting `AgentSession` as replacement for `state_engine.py`
- Any changes to the `.md` agent manifest format
- OpenTelemetry, AGT, skill scoping — these are v1.5

---

## 6. File Change Summary (v1.4 only)

**Modified:**
- `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py` — add `_assert_under_root()`, `_container_user_flag()`, `cwd` in `run_hygienic()`
- `plugins/exploration-cycle-plugin/scripts/dispatch.py` — extend `build_parser()` (Step 2.0), wire auth gate in `main()`, add `build_agent_index()`, add `build_handoff_envelope()`
- `plugins/exploration-cycle-plugin/scripts/state_engine.py` — add `requires_premium` column + migration, add `phase_metrics` table, update `record_premium_call()` signature, add `checkpoint_wal()`

**Created:**
- `plugins/exploration-cycle-plugin/tests/test_path_traversal.py`
- `plugins/exploration-cycle-plugin/tests/test_dispatch_authorization_gate.py`
- `plugins/exploration-cycle-plugin/tests/test_phase_premium_counter.py`
- `plugins/exploration-cycle-plugin/policies/dispatch.yaml` (placeholder for v1.5 AGT)
