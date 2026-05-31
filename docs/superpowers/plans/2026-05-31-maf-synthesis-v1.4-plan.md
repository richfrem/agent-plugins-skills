# MAF Synthesis v1.4 Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or `superpowers:executing-plans`. Every task has an explicit verify step — mark complete only after running it.

**Goal:** Patch six security defects in the v1.3 control plane, port two MAF-validated patterns to the Python dispatch layer.

**Spec:** `docs/superpowers/specs/2026-05-31-maf-synthesis-v1.4-spec.md`  
**ADR:** `ADRs/007_maf_adapter_runtime_decision.md`  
**v1.5 scope (deferred):** OpenTelemetry, AGT adoption, per-agent skill scoping, HarnessAgent evaluation

---

## ⚠️ API Reality Check (Read Before Starting)

Document reviewers found five places the original plan described non-existent APIs. The plan below uses the **real current API** throughout.

| Task | What was wrong | What's correct |
|------|---------------|----------------|
| 1 | Test used `HygienicRunner` class | No such class exists — test `_assert_under_root()` directly |
| 2 | Used `args.db_path`, `args.approval_id`, etc. | `build_parser()` has none of these — Step 2.0 adds them first |
| 2 | Used keyword-arg form of `check_dispatch_authorization()` | Real signature: `(conn, approval_id, action, target_path, spec_path, envelope, key, nonce_cache) -> tuple[bool, str]` |
| 3 | Used `create_task()`, `lease_task(conn, sid, agent)` returning object | Real: `add_task(conn, task_id, session_id, ...)`, `lease_task(conn, task_id, subagent_id) -> bool` |
| 4 | Used `PRAGMA wal_checkpoint(PASSIVE)` to check size | PASSIVE is itself a checkpoint — call TRUNCATE directly |

---

## Task 0: Plan Reconciliation (Run First)

Before writing any code, verify the baseline:

- [ ] **Step 0.1:** Confirm `HygienicRunner` does not exist in `sandbox_runner.py`
  ```bash
  grep -n "HygienicRunner\|class Hygienic" plugins/exploration-cycle-plugin/scripts/sandbox_runner.py
  # Expected: no output
  ```

- [ ] **Step 0.2:** Confirm `build_parser()` has no `--db-path` or `--approval-id`
  ```bash
  grep -n "db.path\|approval.id\|envelope" plugins/exploration-cycle-plugin/scripts/dispatch.py
  # Expected: lines in check_dispatch_authorization only, not in build_parser
  ```

- [ ] **Step 0.3:** Confirm `lease_task()` returns bool, takes `task_id` (not session_id)
  ```bash
  grep -n "def lease_task\|def add_task\|def create_task" plugins/exploration-cycle-plugin/scripts/state_engine.py
  # Expected: add_task and lease_task — no create_task
  ```

- [ ] **Step 0.4:** Confirm no WAL checkpoint call anywhere
  ```bash
  grep -rn "wal_checkpoint" plugins/exploration-cycle-plugin/scripts/
  # Expected: no output
  ```

- [ ] **Step 0.5:** Run existing test suite — baseline must be green before any changes
  ```bash
  cd plugins/exploration-cycle-plugin && python -m pytest tests/ -v --tb=short 2>&1 | tail -20
  ```

---

## Phase 0: Security Patches

### Task 1: Add `_assert_under_root()` Path Enforcement — `sandbox_runner.py`

**What:** Add new path boundary enforcement. This is not replacing an existing check — `sandbox_runner.py` currently has no file path validation at all. The function enforces the boundary at every future file-access site.

**Files:** `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`, new `plugins/exploration-cycle-plugin/tests/test_path_traversal.py`

- [ ] **Step 1.1: Write the failing test**

```python
# plugins/exploration-cycle-plugin/tests/test_path_traversal.py
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from sandbox_runner import _assert_under_root

def test_valid_path_passes(tmp_path):
    allowed = tmp_path / "work"
    allowed.mkdir()
    f = allowed / "file.txt"
    f.touch()
    _assert_under_root(f, allowed)  # must not raise

def test_sibling_prefix_rejected(tmp_path):
    """The classic bypass: /tmp/work_evil passes a naive startswith('/tmp/work') check."""
    allowed = tmp_path / "work"
    allowed.mkdir()
    evil = tmp_path / "work_evil"
    evil.mkdir()
    evil_file = evil / "secret.txt"
    evil_file.touch()
    with pytest.raises(PermissionError, match="Path traversal rejected"):
        _assert_under_root(evil_file, allowed)

def test_parent_escape_rejected(tmp_path):
    allowed = tmp_path / "work"
    allowed.mkdir()
    with pytest.raises(PermissionError):
        _assert_under_root(tmp_path / "outside.txt", allowed)

def test_symlink_escape_rejected(tmp_path):
    allowed = tmp_path / "work"
    allowed.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    link = allowed / "escape_link"
    link.symlink_to(outside)
    with pytest.raises(PermissionError):
        _assert_under_root(link, allowed)
```

- [ ] **Step 1.2: Add `_assert_under_root()` to `sandbox_runner.py`**

Add after the constants block (after line ~26):

```python
def _assert_under_root(full: Path, root: Path, label: str = "path") -> None:
    """Fail-closed descendant path check. resolve() eliminates symlink escapes."""
    try:
        full.resolve().relative_to(root.resolve())
    except ValueError:
        raise PermissionError(
            f"Path traversal rejected: {full} is outside {root} ({label})"
        )
```

- [ ] **Step 1.3: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/test_path_traversal.py -v
```
Expected: 4 tests PASSED. No existing tests broken.

---

### Task 2: Wire Authorization Gate into `dispatch.py main()`

**What:** `check_dispatch_authorization()` exists (line 195) and is implemented. `main()` (line 267) never calls it. This task adds the missing CLI args and wires the gate.

**Files:** `plugins/exploration-cycle-plugin/scripts/dispatch.py`, `plugins/exploration-cycle-plugin/tests/test_dispatch_authorization_gate.py`

- [ ] **Step 2.0: Extend `build_parser()` with security arguments**

In `build_parser()`, append after the existing `--tier` argument:

```python
# Authorization gate arguments (required for secure dispatch)
parser.add_argument("--db-path", required=True,
    help="Path to active_session.sqlite")
parser.add_argument("--approval-id", required=True,
    help="UUID of the active approval record in the DB")
parser.add_argument("--dispatch-action", default="run_agent",
    help="Action being dispatched for allowlist check (default: run_agent)")
parser.add_argument("--target-path", default=None,
    help="File path target for path allowlist check (optional)")
parser.add_argument("--spec-path", default=None,
    help="Path to spec document for hash integrity check (optional)")
parser.add_argument("--envelope-json", required=True,
    help="JSON-serialized HMAC envelope from sandbox_runner.make_envelope()")
parser.add_argument("--hmac-key-path", required=True,
    help="Path to the session HMAC key file")
```

- [ ] **Step 2.1: Write the failing tests**

```python
# plugins/exploration-cycle-plugin/tests/test_dispatch_authorization_gate.py
import json, subprocess, sys, unittest.mock
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

DISPATCH = Path(__file__).parent.parent / "scripts" / "dispatch.py"
MINIMAL_ARGS = [
    "--agent", "agents/intake-agent.md",
    "--instruction", "run",
    "--output", "/tmp/test_out.md",
]

def _base_cmd(extra: list) -> list:
    return [sys.executable, str(DISPATCH)] + MINIMAL_ARGS + extra

def test_dispatch_blocks_without_approval(tmp_path):
    """Gate must fire before CLI subprocess — even with otherwise valid args."""
    # Provide valid-looking but nonexistent db and key so the gate fires, not arg parsing
    db = tmp_path / "test.sqlite"
    db.touch()
    key = tmp_path / "test.key"
    key.write_bytes(b"\x00" * 32)
    envelope = json.dumps({"payload": "x", "hmac": "bad", "nonce": "n1"})
    result = subprocess.run(
        _base_cmd([
            "--db-path", str(db),
            "--approval-id", "nonexistent-id",
            "--dispatch-action", "run_agent",
            "--envelope-json", envelope,
            "--hmac-key-path", str(key),
        ]),
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "authorization" in result.stderr.lower() or "approval" in result.stderr.lower()

def test_dispatch_gate_fires_before_subprocess(tmp_path):
    """Verify the CLI subprocess is never called on auth failure."""
    import importlib.util, types

    spec = importlib.util.spec_from_file_location("dispatch", DISPATCH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    db = tmp_path / "test.sqlite"
    db.touch()

    with unittest.mock.patch("subprocess.run") as mock_run, \
         unittest.mock.patch.object(mod, "check_dispatch_authorization",
                                    return_value=(False, "mock rejection")) as mock_auth:
        with pytest.raises(SystemExit) as exc:
            mod.main.__wrapped__ if hasattr(mod.main, "__wrapped__") else None
        # Authorization must be checked; subprocess must NOT be called
        mock_auth.assert_called_once()
        mock_run.assert_not_called()
```

- [ ] **Step 2.2: Wire the gate as the first action in `main()`**

At the top of `main()`, before the existing `read_file(args.agent)` call, insert:

```python
# Authorization gate — fail-closed. No dispatch without valid approval + HMAC.
from state_engine import init_db
from sandbox_runner import load_session_key, verify_envelope

conn = init_db(args.db_path)
key = load_session_key(Path(args.hmac_key_path))
envelope = json.loads(args.envelope_json)
nonce_cache: OrderedDict = OrderedDict()

ok, reason = check_dispatch_authorization(
    conn=conn,
    approval_id=args.approval_id,
    action=args.dispatch_action,
    target_path=args.target_path,
    spec_path=args.spec_path,
    envelope=envelope,
    key=key,
    nonce_cache=nonce_cache,
)
if not ok:
    print(f"Error: dispatch authorization failed: {reason}", file=sys.stderr)
    sys.exit(1)
```

- [ ] **Step 2.3: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/test_dispatch_authorization_gate.py -v
```
Expected: tests PASSED. No existing tests broken.

---

### Task 3: Fix Per-Phase Premium Call Counter

**What:** `lease_task()` checks `sessions.premium_calls_used` (session-level). Add per-phase tracking via `phase_metrics` table and `requires_premium` column. This requires a schema migration.

**Files:** `plugins/exploration-cycle-plugin/scripts/state_engine.py`, `plugins/exploration-cycle-plugin/tests/test_phase_premium_counter.py`

- [ ] **Step 3.1: Write the failing test (uses real API)**

```python
# plugins/exploration-cycle-plugin/tests/test_phase_premium_counter.py
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from state_engine import init_db, create_session, add_task, lease_task, record_premium_call

def test_premium_calls_are_tracked_per_phase(tmp_path):
    """Phase 2 premium tasks must not be blocked by phase 1's counter."""
    db = tmp_path / "test.sqlite"
    conn = init_db(str(db))
    sid = "session-1"
    create_session(conn, sid, "test")

    # Phase 1: add a premium task, lease it, record the premium call
    add_task(conn, "t1", sid, 1, "phase-1", "comp-a", requires_premium=True)
    assert lease_task(conn, "t1", "agent-a") is True
    record_premium_call(conn, sid, phase_ordinal=1)

    # Phase 2: should have a fresh budget — not blocked by phase 1
    add_task(conn, "t2", sid, 2, "phase-2", "comp-b", requires_premium=True)
    assert lease_task(conn, "t2", "agent-b") is True, \
        "Phase 2 premium task blocked by phase 1 counter — per-phase tracking broken"

def test_non_premium_task_not_gated(tmp_path):
    """Tasks without requires_premium=True must ignore the premium call counter."""
    db = tmp_path / "test.sqlite"
    conn = init_db(str(db))
    sid = "session-2"
    create_session(conn, sid, "test")

    # Saturate phase 1 premium counter
    add_task(conn, "tp1", sid, 1, "phase-1", "premium-comp", requires_premium=True)
    assert lease_task(conn, "tp1", "agent-x") is True
    record_premium_call(conn, sid, phase_ordinal=1)

    # A normal task in phase 1 should still lease fine
    add_task(conn, "tn1", sid, 1, "phase-1", "normal-comp", requires_premium=False)
    assert lease_task(conn, "tn1", "agent-y") is True
```

- [ ] **Step 3.2: Add `requires_premium` column to `tasks` schema**

In `SCHEMA_SQL`, add to the `tasks` table definition:
```sql
    requires_premium BOOLEAN DEFAULT 0,
```

Add `phase_metrics` table:
```sql
CREATE TABLE IF NOT EXISTS phase_metrics (
    session_id TEXT NOT NULL,
    phase_ordinal INTEGER NOT NULL,
    premium_calls_used INTEGER DEFAULT 0,
    PRIMARY KEY (session_id, phase_ordinal),
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
```

- [ ] **Step 3.3: Add migration to `init_db()`**

After `conn.executescript(SCHEMA_SQL)`, add:
```python
# Migration: add requires_premium column if upgrading from v1.3
try:
    conn.execute("ALTER TABLE tasks ADD COLUMN requires_premium BOOLEAN DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists
```

- [ ] **Step 3.4: Update `add_task()` signature**

```python
def add_task(conn: sqlite3.Connection, task_id: str, session_id: str,
             phase_ordinal: int, phase_name: str, component_name: str,
             requires_premium: bool = False) -> None:
    with _immediate_transaction(conn) as c:
        c.execute(
            "INSERT INTO tasks (id, session_id, phase_ordinal, phase_name, "
            "component_name, requires_premium) VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, session_id, phase_ordinal, phase_name,
             component_name, int(requires_premium)),
        )
```

- [ ] **Step 3.5: Update `lease_task()` to gate per-phase**

Replace the current `premium_calls_used >= MAX_PREMIUM_CALLS_PER_PHASE` check with:

```python
# Only gate premium if the task requires it
if row and row["requires_premium"]:
    phase_row = c.execute(
        "SELECT premium_calls_used FROM phase_metrics "
        "WHERE session_id = (SELECT session_id FROM tasks WHERE id = ?) "
        "AND phase_ordinal = (SELECT phase_ordinal FROM tasks WHERE id = ?)",
        (task_id, task_id)
    ).fetchone()
    phase_premium = phase_row["premium_calls_used"] if phase_row else 0
    if phase_premium >= MAX_PREMIUM_CALLS_PER_PHASE:
        raise RuntimeError(
            f"premium_calls_used per phase limit ({MAX_PREMIUM_CALLS_PER_PHASE}) exceeded"
        )
```

- [ ] **Step 3.6: Update `record_premium_call()` to accept `phase_ordinal`**

```python
def record_premium_call(conn: sqlite3.Connection,
                        session_id: str, phase_ordinal: int) -> None:
    """Increment per-phase premium call counter."""
    with _immediate_transaction(conn) as c:
        c.execute(
            "INSERT INTO phase_metrics (session_id, phase_ordinal, premium_calls_used) "
            "VALUES (?, ?, 1) "
            "ON CONFLICT(session_id, phase_ordinal) DO UPDATE SET "
            "premium_calls_used = premium_calls_used + 1",
            (session_id, phase_ordinal),
        )
```

- [ ] **Step 3.7: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/test_phase_premium_counter.py -v
```
Expected: Both tests PASSED. Existing `test_state_engine.py` tests still pass (migration is backwards compatible).

---

### Task 4: WAL Checkpoint Management

**What:** Add `checkpoint_wal()` and call it after `commit_task_complete()` exits its transaction. Do not use `PRAGMA wal_checkpoint(PASSIVE)` — it is itself a checkpoint, not a size check.

**Files:** `plugins/exploration-cycle-plugin/scripts/state_engine.py`

- [ ] **Step 4.1: Add `checkpoint_wal()`**

```python
def checkpoint_wal(conn: sqlite3.Connection) -> None:
    """Flush WAL pages to main DB. Call outside any active transaction."""
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
```

- [ ] **Step 4.2: Call after `commit_task_complete()` (outside the transaction)**

After the `with _immediate_transaction(conn)` block in `commit_task_complete()`, add:

```python
def commit_task_complete(conn, task_id, subagent_id, version, payload_hash) -> bool:
    with _immediate_transaction(conn) as c:
        # ... existing CAS logic ...
        if result.rowcount == 1:
            # ... existing parallel_agents_running decrement ...
            completed = True
        else:
            completed = False
    # checkpoint AFTER the transaction closes — not inside it
    if completed:
        checkpoint_wal(conn)
    return completed
```

- [ ] **Step 4.3: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/test_state_engine.py -v
```
Expected: No regressions.

---

### Task 5: Container `--user` Flag

**Files:** `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`

- [ ] **Step 5.1: Add `_container_user_flag()`**

```python
def _container_user_flag() -> list[str]:
    """Return --user uid:gid for the current process. Falls back to nobody on envs without getuid."""
    try:
        return ["--user", f"{os.getuid()}:{os.getgid()}"]
    except AttributeError:
        return ["--user", "65534:65534"]  # nobody:nogroup
```

- [ ] **Step 5.2: Insert into `run_containerized()` command list**

Find the `[runtime, "run", "--rm", ...]` command construction and add `*_container_user_flag()` before the mount flags.

- [ ] **Step 5.3: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/test_sandbox_runner.py -v
```
Expected: No regressions.

---

### Task 6: `run_hygienic()` `cwd` Isolation

**What:** `run_hygienic()` inherits parent `cwd`. Subprocess should start in a fresh temp directory with no ambient access to source files or credentials.

**Files:** `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`

- [ ] **Step 6.1: Add `import tempfile` to imports** (already imported via `shutil` chain — verify)

```bash
grep "import tempfile\|import shutil" plugins/exploration-cycle-plugin/scripts/sandbox_runner.py
```

- [ ] **Step 6.2: Update `run_hygienic()` to create and clean up an isolated `cwd`**

```python
def run_hygienic(cmd: list, timeout: int = TIMEOUT_SECONDS,
                 extra_vars: dict | None = None) -> subprocess.CompletedProcess:
    env = _build_clean_env(extra_vars)
    cwd = tempfile.mkdtemp(prefix="agentic_sandbox_")
    try:
        proc = subprocess.Popen(cmd, shell=False, env=env, cwd=cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return subprocess.CompletedProcess(
                args=cmd, returncode=proc.returncode,
                stdout=stdout, stderr=stderr,
            )
        except subprocess.TimeoutExpired:
            _terminate_with_grace(proc)
            proc.wait()
            raise
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
```

- [ ] **Step 6.3: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/test_sandbox_runner.py -v
```
Expected: No regressions.

---

## Phase 1: MAF Pattern Ports (v1.4 scope)

### Task 7: Three-Way Alias Index

**Files:** `plugins/exploration-cycle-plugin/scripts/dispatch.py`, `tests/test_dispatch_authorization_gate.py` (extend)

- [ ] **Step 7.1: Add `build_agent_index()` to `dispatch.py`**

```python
def build_agent_index(agents_dir: Path) -> dict[str, Path]:
    """Build alias index: stem, stem-without-agent, frontmatter name: — all → same file."""
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

- [ ] **Step 7.2: Write test**

```python
def test_alias_index_three_way_resolution(tmp_path):
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "intake-agent.md").write_text("---\nname: Intake Agent\n---\nBody")
    from dispatch import build_agent_index
    idx = build_agent_index(agents)
    assert "intake-agent" in idx          # stem
    assert "intake" in idx                # stem-without-agent
    assert "Intake Agent" in idx          # frontmatter name
    # All three resolve to the same file
    assert idx["intake-agent"] == idx["intake"] == idx["Intake Agent"]
```

- [ ] **Step 7.3: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/ -k "alias" -v
```

---

### Task 8: Handoff Envelope Standardization

**Files:** `plugins/exploration-cycle-plugin/scripts/dispatch.py`

- [ ] **Step 8.1: Add `build_handoff_envelope()` to `dispatch.py`**

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

- [ ] **Step 8.2: Write test**

```python
def test_handoff_envelope_caps_turns_and_chars():
    transcript = [("user", "x" * 500), ("agent", "y" * 500)] * 10
    from dispatch import build_handoff_envelope
    env = build_handoff_envelope("intake-agent", "vibe-orchestrator",
                                  "prototype detected", "I have code", transcript)
    lines = [l for l in env.split("\n")
             if l.startswith("user:") or l.startswith("agent:")]
    assert len(lines) <= 8
    for line in lines:
        payload = line.split(": ", 1)[1] if ": " in line else line
        assert len(payload) <= 300
```

- [ ] **Step 8.3: Verify**
```bash
cd plugins/exploration-cycle-plugin && python -m pytest tests/ -k "handoff" -v
```

---

## Run Order

```
Task 0 (reconcile) → must pass before writing any code
Task 1 (path enforcement) → standalone, no deps
Task 2, Step 2.0 (parser args) → prerequisite for Task 2 Steps 2.1–2.3
Task 2, Steps 2.1–2.3 (auth gate) → depends on 2.0
Task 3 (premium counter) → standalone, modifies state_engine only
Task 4 (WAL checkpoint) → standalone, small addition to state_engine
Task 5 (container --user) → standalone
Task 6 (cwd isolation) → standalone
Task 7 (alias index) → standalone, adds to dispatch.py
Task 8 (handoff envelope) → standalone, adds to dispatch.py
```

Tasks 1, 3, 4, 5, 6 can run in parallel (different files). Tasks 7 and 8 both modify `dispatch.py` — run sequentially.

---

## v1.4 Completion Criteria

- [ ] `test_path_traversal.py` — 4 tests PASSED (including symlink escape)
- [ ] `test_dispatch_authorization_gate.py` — gate fires before subprocess on auth failure
- [ ] `test_phase_premium_counter.py` — phase 2 not blocked by phase 1 counter
- [ ] `run_hygienic()` creates and cleans up temp `cwd`
- [ ] Container command includes `--user` flag
- [ ] `checkpoint_wal()` called after `commit_task_complete()` exits its transaction
- [ ] `build_agent_index()` — 3-way alias resolution test PASSED
- [ ] `build_handoff_envelope()` — turn and char cap test PASSED
- [ ] All v1.3 tests still pass: `test_kernel_security.py`, `test_evaluate_security.py`, `test_update_memory_security.py`, `test_dispatch_security.py`, `test_state_engine.py`, `test_sandbox_runner.py`, `test_integration.py`

---

## v1.5 Scope (Not In This Plan)

- Task A: OpenTelemetry instrumentation (`dispatch.py`, `state_engine.py`, `kernel.py`)
- Task B: AGT evaluation spike + adoption (evaluation-first, import path must be verified)
- Task C: Per-agent skill scoping with budget cap
- Task D: MAF 1.7.0 HarnessAgent evaluation (concrete metrics: LOC, tokens, latency, Gemini compat, provider-swap failure modes)
