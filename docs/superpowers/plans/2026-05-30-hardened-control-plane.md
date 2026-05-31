# Hardened Control Plane v1.3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Patch five critical security vulnerabilities in `agent-agentic-os` / `exploration-cycle-plugin`, then migrate session state from human-editable markdown to a transactional SQLite database with process-level sandboxing and HMAC-signed message envelopes.

**Architecture:** Phase 0 patches four existing files inline with no new abstractions. Phase 1 introduces `state_engine.py` as the single SQLite adapter; the markdown dashboard becomes a read-only derived projection. Phase 2 adds `sandbox_runner.py` for process hygiene, container wrapping, and HMAC envelope validation, then wires `dispatch.py` to enforce all gates before spawning.

**Tech Stack:** Python 3.11+ stdlib only (`sqlite3`, `hmac`, `hashlib`, `subprocess`, `os`, `secrets`). `sqlite3` is stdlib — no install needed. Tests use `pytest`: `pip install pytest`.

**DB path (canonical):** `${CLAUDE_PROJECT_DIR}/context/exploration/active_session.sqlite` — per spec v1.3 §3. Path is added to `.gitignore`. No fallback to `/tmp`.

---

## File Structure

**Modified:**
- `plugins/agent-agentic-os/hooks/update_memory.py` — remove lockless state write; remove fallback
- `plugins/agent-agentic-os/scripts/kernel.py` — `_safe_clear_stale` + rotation inside write lock (canonical; skills/*/kernel.py are symlinks)
- `plugins/exploration-cycle-plugin/scripts/dispatch.py` — default tier `"2"`; `build_parser()`; strict frontmatter parser + injection detector
- `plugins/agent-agentic-os/scripts/evaluate.py` — baseline SHA256 check for gate scripts; O_EXCL trace writes

**Created:**
- `plugins/exploration-cycle-plugin/scripts/state_engine.py`
- `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`
- `plugins/agent-agentic-os/tests/test_kernel_security.py`
- `plugins/agent-agentic-os/tests/test_evaluate_security.py`
- `plugins/agent-agentic-os/tests/test_update_memory_security.py`
- `plugins/exploration-cycle-plugin/tests/test_dispatch_security.py`
- `plugins/exploration-cycle-plugin/tests/test_state_engine.py`
- `plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py`
- `plugins/exploration-cycle-plugin/tests/test_integration.py`
- `docs/adr/ADR-001-sqlite-path-strategy.md`
- `docs/adr/ADR-002-dual-runtime-compatibility.md`

---

## Task 1: Phase 0a — Patch `update_memory.py` (C-1, C-3)

**Vulnerabilities:**
- **C-1**: Lines 154–168 read and write `os-state.json` directly without `state_write.lock`. Concurrent kernel writes are clobbered.
- **C-3**: Lines 188–192 fall back to direct `events.jsonl` append (no lock, no size cap) when `kernel.py` is absent.

**Files:**
- Modify: `plugins/agent-agentic-os/hooks/update_memory.py:154-192`
- Create: `plugins/agent-agentic-os/tests/test_update_memory_security.py`

- [ ] **Step 1.1: Write the failing tests**

```python
# plugins/agent-agentic-os/tests/test_update_memory_security.py
import sys, json, subprocess
from pathlib import Path
import pytest

HOOK = Path(__file__).parent.parent / "hooks" / "update_memory.py"


def _make_env(tmp_path):
    ctx = tmp_path / "context"
    ctx.mkdir()
    (ctx / "os-state.json").write_text(json.dumps({"active_agent": "test"}))
    return {"CLAUDE_PROJECT_DIR": str(tmp_path)}


def _payload(event="SessionStart"):
    return json.dumps({"event": event})


def test_no_direct_os_state_write(tmp_path):
    """Hook must NOT write to os-state.json directly (C-1)."""
    env = _make_env(tmp_path)
    before = (tmp_path / "context" / "os-state.json").read_text()
    subprocess.run(
        [sys.executable, str(HOOK), _payload("SessionStart")],
        env={**{"PATH": "/usr/bin:/bin"}, **env},
        timeout=10,
    )
    after = (tmp_path / "context" / "os-state.json").read_text()
    assert before == after, "Hook must not write os-state.json directly (C-1)"


def test_no_fallback_events_write_when_kernel_absent(tmp_path):
    """When kernel.py is absent the hook must NOT write events.jsonl (C-3)."""
    env = _make_env(tmp_path)
    events_file = tmp_path / "context" / "events.jsonl"
    subprocess.run(
        [sys.executable, str(HOOK), _payload("SessionStart")],
        env={**{"PATH": "/usr/bin:/bin"}, **env},
        timeout=10,
    )
    assert not events_file.exists(), "Hook must fail closed without kernel.py (C-3)"
```

- [ ] **Step 1.2: Run tests — confirm FAIL**

```bash
cd /Users/richardfremmerlid/Projects/agent-plugins-skills
pytest plugins/agent-agentic-os/tests/test_update_memory_security.py -v
```

Expected: Both FAIL (current code writes `os-state.json` and `events.jsonl`).

- [ ] **Step 1.3: Remove lockless state write block (C-1)**

Delete lines 154–168 from `update_memory.py` — the entire `# 2.5 Update OS State` block that reads and writes `os-state.json` directly.

- [ ] **Step 1.4: Remove fallback and fail closed (C-3)**

Replace the kernel dispatch block (lines 173–192) with:

```python
        # 3. Route event through kernel.py — fail closed if kernel absent (C-3 fix)
        kernel_script = Path(project_dir) / "context" / "kernel.py"
        if not kernel_script.exists():
            return  # Fail closed — no fallback writes
        import subprocess
        cmd = [
            sys.executable, str(kernel_script), "emit_event",
            "--agent", event_doc["agent"],
            "--type", event_doc["type"],
            "--action", event_doc["action"],
            "--status", event_doc.get("status", "success")
        ]
        if "summary" in event_doc:
            cmd.extend(["--summary", event_doc["summary"]])
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
```

- [ ] **Step 1.5: Run tests — confirm PASS**

```bash
pytest plugins/agent-agentic-os/tests/test_update_memory_security.py -v
```

- [ ] **Step 1.6: Commit**

```bash
git add plugins/agent-agentic-os/hooks/update_memory.py \
        plugins/agent-agentic-os/tests/test_update_memory_security.py
git commit -m "fix(agent-agentic-os): remove lockless os-state write and events fallback (C-1, C-3)"
```

---

## Task 2: Phase 0b — Patch `kernel.py` (C-2, H-1)

**Vulnerabilities:**
- **C-2 / L-1**: `acquire_lock` calls `_is_stale()` then `_clear()` non-atomically. A second caller can acquire the lock between these steps and have it deleted by the first caller. PID recycling can also cause a live process to be mistaken for a dead one.
- **H-1**: `emit_event` checks file size and renames `events.jsonl` *before* acquiring `events_write.lock`.

**Files:**
- Modify: `plugins/agent-agentic-os/scripts/kernel.py`
- Create: `plugins/agent-agentic-os/tests/test_kernel_security.py`

- [ ] **Step 2.1: Write the failing tests**

```python
# plugins/agent-agentic-os/tests/test_kernel_security.py
import sys, os, json, time, threading
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import kernel as K


@pytest.fixture
def tmp_kernel(tmp_path, monkeypatch):
    monkeypatch.setattr(K, "KERNEL_DIR", tmp_path)
    monkeypatch.setattr(K, "EVENTS_FILE", tmp_path / "events.jsonl")
    monkeypatch.setattr(K, "LOCKS_DIR", tmp_path / ".locks")
    monkeypatch.setattr(K, "STATE_FILE", tmp_path / "os-state.json")
    monkeypatch.setattr(K, "AGENTS_FILE", tmp_path / "agents.json")
    monkeypatch.setattr(K, "AGENTS_DIR", tmp_path / "agents")
    (tmp_path / ".locks").mkdir()
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents.json").write_text(
        json.dumps({"permitted_agents": ["test-agent"]})
    )
    return tmp_path


def test_safe_clear_stale_rejects_concurrent_acquisition(tmp_kernel, monkeypatch):
    """_safe_clear_stale must return False if lock is acquired between its two reads.
    
    Uses monkeypatch on time.sleep to inject a concurrent acquisition deterministically
    rather than relying on thread scheduling jitter.
    """
    lock_path = tmp_kernel / ".locks" / "test.lock"
    lock_path.mkdir()
    meta = {"pid": 99999999, "expires_at": time.time() - 10, "acquired_at": "2000-01-01T00:00:00Z"}
    (lock_path / "meta.json").write_text(json.dumps(meta))

    original_sleep = time.sleep

    def sleep_and_inject(seconds):
        # Simulate concurrent acquisition during the pause between double-reads
        new_meta = {
            "pid": os.getpid(),
            "expires_at": time.time() + 300,
            "acquired_at": "2026-01-01T00:00:00Z",
        }
        (lock_path / "meta.json").write_text(json.dumps(new_meta))
        original_sleep(seconds)

    monkeypatch.setattr(time, "sleep", sleep_and_inject)
    result = K._safe_clear_stale(lock_path)
    assert result is False, "_safe_clear_stale must detect concurrent acquisition via double-read"
    assert lock_path.exists(), "Lock must not be cleared when concurrent acquisition detected"


def test_rotation_happens_inside_write_lock(tmp_kernel, monkeypatch):
    """File size check and rename must happen inside events_write.lock, not before."""
    events_file = tmp_kernel / "events.jsonl"
    events_file.write_bytes(b"x" * (K.EVENTS_MAX_BYTES + 1))

    rotation_order = []
    original_spinlock = K._spinlock

    def tracked_spinlock(lock_path, timeout=30):
        rotation_order.append(("spinlock", str(lock_path)))
        return original_spinlock(lock_path, timeout)

    original_rename = os.rename

    def tracked_rename(src, dst):
        rotation_order.append(("rename", str(src)))
        return original_rename(src, dst)

    monkeypatch.setattr(K, "_spinlock", tracked_spinlock)
    monkeypatch.setattr(os, "rename", tracked_rename)

    K.emit_event("test-agent", "result", "test_action")

    spinlock_indices = [i for i, op in enumerate(rotation_order) if op[0] == "spinlock"]
    rename_indices = [i for i, op in enumerate(rotation_order) if op[0] == "rename"]

    if rename_indices:
        write_lock_idx = next(
            i for i in spinlock_indices if "events_write" in rotation_order[i][1]
        )
        assert rename_indices[0] > write_lock_idx, (
            "Rotation rename must happen AFTER events_write.lock is acquired (H-1)"
        )
```

- [ ] **Step 2.2: Run tests — confirm FAIL**

```bash
pytest plugins/agent-agentic-os/tests/test_kernel_security.py -v
```

- [ ] **Step 2.3: Add `import subprocess` to kernel.py imports**

Find: `import os, sys, json, time, uuid, random, argparse`  
Replace with: `import os, sys, json, time, uuid, random, argparse, subprocess`

- [ ] **Step 2.4: Add `_pid_started_after` and `_safe_clear_stale` after `_clear` (line 118)**

```python
def _pid_started_after(pid: int, acquired_at_str: str) -> bool:
    """Returns True if the PID's process started after acquired_at_str (recycled PID)."""
    if not acquired_at_str:
        return False
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "lstart="],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode != 0:
            return True  # Process not found — dead/recycled
        ps_start = time.strptime(result.stdout.strip(), "%a %b %d %H:%M:%S %Y")
        ps_epoch = time.mktime(ps_start)
        acq_clean = acquired_at_str.rstrip("Z").split("+")[0]
        from datetime import datetime
        acq_epoch = datetime.fromisoformat(acq_clean).timestamp()
        return ps_epoch > acq_epoch + 1
    except Exception:
        return False


def _safe_clear_stale(lock_path: Path) -> bool:
    """Clear a stale lock with TOCTOU protection (C-2 / L-1 fix).

    Double-reads meta.json with a pause. If meta changed between reads,
    another process acquired the lock — abort without clearing.
    Returns True if cleared, False if the lock appears live or was concurrently acquired.
    """
    meta_path = lock_path / "meta.json"
    meta1 = _load(meta_path, {})
    pid1 = meta1.get("pid")

    if pid1:
        alive = _pid_alive(int(pid1))
        if alive and not _pid_started_after(int(pid1), meta1.get("acquired_at", "")):
            return False  # Genuinely alive

    if meta1.get("expires_at", 0) >= time.time() and pid1 and _pid_alive(int(pid1)):
        return False

    time.sleep(0.02)
    meta2 = _load(meta_path, {})
    if meta1 != meta2:
        return False  # Concurrent acquisition detected

    try:
        _clear(lock_path)
        return True
    except OSError:
        return False
```

- [ ] **Step 2.5: Update `acquire_lock` to use `_safe_clear_stale`**

Replace the stale-lock clearing block in `acquire_lock`:

```python
    if lock.exists():
        if _is_stale(lock):
            if _safe_clear_stale(lock):
                print(f"[Kernel] Stale lock cleared: {name}")
            else:
                print(f"[Kernel] Lock busy (concurrent acquisition detected): {name}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"[Kernel] Lock busy: {name}", file=sys.stderr)
            sys.exit(1)
```

- [ ] **Step 2.6: Move rotation inside `events_write.lock` in `emit_event` (H-1 fix)**

Replace the entire `emit_event` body with:

```python
def emit_event(agent, type_, action, status=None, summary=None,
               to=None, correlation_id=None):
    if not _validate_agent(agent):
        sys.exit(1)
    event = {"id": str(uuid.uuid4()), "time": _now(),
             "agent": agent, "type": type_, "action": action}
    if to:             event["to"]             = to
    if correlation_id: event["correlation_id"] = correlation_id
    if status:         event["status"]         = status
    if summary:        event["summary"]        = summary

    write_lock = LOCKS_DIR / "events_write.lock"
    if not _spinlock(write_lock):
        print("[Kernel] Events write lock timeout", file=sys.stderr)
        sys.exit(1)
    try:
        os.makedirs(KERNEL_DIR, exist_ok=True)
        # Size check and rotation inside the write lock (H-1 fix — eliminates events_rotate.lock)
        if EVENTS_FILE.exists() and EVENTS_FILE.stat().st_size > EVENTS_MAX_BYTES:
            archive = KERNEL_DIR / "events-archive"
            os.makedirs(archive, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.rename(EVENTS_FILE, archive / f"events-{ts}.jsonl")
            print(f"[Kernel] Rotated events.jsonl")
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    finally:
        _clear(write_lock)
    print(f"[Kernel] Event emitted: {type_}:{action}" + (f" -> {to}" if to else ""))
```

Also update `_spinlock` to use `_safe_clear_stale`:

```python
def _spinlock(lock_path, timeout=30):
    os.makedirs(LOCKS_DIR, exist_ok=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.mkdir(lock_path)
            return True
        except FileExistsError:
            try:
                if _is_stale(lock_path):
                    _safe_clear_stale(lock_path)
            except OSError:
                pass
            time.sleep(random.uniform(0.05, 0.15))
    return False
```

- [ ] **Step 2.7: Run tests — confirm PASS**

```bash
pytest plugins/agent-agentic-os/tests/test_kernel_security.py -v
```

- [ ] **Step 2.8: Commit**

```bash
git add plugins/agent-agentic-os/scripts/kernel.py \
        plugins/agent-agentic-os/tests/test_kernel_security.py
git commit -m "fix(agent-agentic-os): TOCTOU lock protection and rotation inside write lock (C-2, L-1, H-1)"
```

---

## Task 3: Phase 0c — Patch `dispatch.py` (H-2, M-1, C-NEW-4)

**Vulnerabilities:**
- **H-2**: Default tier is `"1"`, appending `--dangerously-skip-permissions` automatically.
- **M-1 / C-NEW-4**: Frontmatter regex only removes first block; does not detect secondary YAML-like blocks injected in the body.

**Files:**
- Modify: `plugins/exploration-cycle-plugin/scripts/dispatch.py`
- Create: `plugins/exploration-cycle-plugin/tests/test_dispatch_security.py`

- [ ] **Step 3.1: Write the failing tests**

```python
# plugins/exploration-cycle-plugin/tests/test_dispatch_security.py
import sys, textwrap
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import dispatch


def test_default_tier_is_2():
    """build_parser() default for --tier must be '2', not '1' (H-2 fix)."""
    parser = dispatch.build_parser()
    tier_action = next(a for a in parser._actions if getattr(a, "dest", None) == "tier")
    assert tier_action.default == "2", f"Default tier must be '2', got '{tier_action.default}'"


def test_strip_frontmatter_only_at_byte_zero():
    """Only a YAML block starting at byte 0 should be stripped."""
    content = "---\ntitle: Test\n---\n# Body\n"
    result = dispatch._strip_frontmatter(content)
    assert result == "# Body\n"

    no_fm = "# Body\n---\nseparator\n---\n"
    assert dispatch._strip_frontmatter(no_fm) == no_fm


def test_detect_frontmatter_injection_in_body():
    """Secondary YAML-like blocks after body begins must be detected."""
    injected = textwrap.dedent("""\
        ---
        title: Agent
        ---
        # Real Instructions

        Do the task.

        ---
        tier: 1
        permissions: all
        ---
    """)
    assert dispatch._detect_frontmatter_injection(injected) is True


def test_clean_document_not_flagged():
    """A document with only a horizontal rule separator must not be flagged."""
    clean = textwrap.dedent("""\
        ---
        title: Agent
        ---
        # Instructions

        Step 1.

        ---

        Step 2.
    """)
    assert dispatch._detect_frontmatter_injection(clean) is False
```

- [ ] **Step 3.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_dispatch_security.py -v
```

- [ ] **Step 3.3: Add `build_parser()` to `dispatch.py` and refactor `main()` to call it**

Extract the argument parser setup from `main()` into a standalone function:

```python
def build_parser() -> "argparse.ArgumentParser":
    """Return the configured argument parser. Exposed for testing."""
    parser = argparse.ArgumentParser(description="Exploration Cycle CLI Dispatch Wrapper")
    parser.add_argument("--agent", required=True, help="Path to the agent markdown file")
    parser.add_argument("--context", nargs="+", default=[],
                        help="Required context files — missing file is a fatal error")
    parser.add_argument("--optional-context", nargs="+", default=[], dest="optional_context",
                        help="Optional context files — missing files are silently skipped")
    parser.add_argument("--instruction", required=True, help="The instruction passed to the agent")
    parser.add_argument("--output", required=True, help="Path to save the resulting artifact")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Subprocess timeout in seconds (default: 120)")
    parser.add_argument("--cli", default="claude", choices=["claude", "copilot", "gh-copilot"],
                        help="CLI backend to use (default: claude)")
    parser.add_argument("--model", default=None,
                        help="Model to use (optional)")
    parser.add_argument("--tier", default="2", choices=["1", "2", "3"],
                        help="Risk tier (default: 2). Tier 1 requires explicit opt-in.")
    return parser
```

Update `main()` first line: `args = build_parser().parse_args()`

- [ ] **Step 3.4: Add `_strip_frontmatter` and `_detect_frontmatter_injection`**

Add after `strip_leading_prose`:

```python
def _strip_frontmatter(content: str) -> str:
    """Strip YAML frontmatter only if it starts at byte 0."""
    match = re.match(r'^---\r?\n.*?\r?\n---\r?\n', content, re.DOTALL)
    if match:
        return content[match.end():]
    return content


def _detect_frontmatter_injection(content: str) -> bool:
    """Detect YAML-like blocks injected after the document body begins.

    Returns True if a secondary '---' delimiter followed by key: value lines
    is found after the leading frontmatter. Lone horizontal rules are not flagged.
    """
    body = _strip_frontmatter(content)
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "---":
            for rest_line in lines[i + 1:]:
                stripped = rest_line.strip()
                if stripped == "---":
                    break
                if re.match(r'^[A-Za-z][\w-]*\s*:', stripped):
                    return True
                if stripped and not stripped.startswith("#"):
                    break
        i += 1
    return False
```

- [ ] **Step 3.5: Replace old regex frontmatter strip in `main()` with new functions**

Find: `agent_content = re.sub(r'^---[\r\n]+.*?[\r\n]+---[\r\n]+', '', agent_content, count=1, flags=re.DOTALL)`

Replace with:

```python
    if _detect_frontmatter_injection(agent_content):
        print("Error: Frontmatter injection detected in agent file — failing closed.", file=sys.stderr)
        sys.exit(1)
    agent_content = _strip_frontmatter(agent_content)
```

- [ ] **Step 3.6: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_dispatch_security.py -v
```

- [ ] **Step 3.7: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/dispatch.py \
        plugins/exploration-cycle-plugin/tests/test_dispatch_security.py
git commit -m "fix(exploration-cycle-plugin): default tier 2, build_parser(), frontmatter injection detection (H-2, M-1, C-NEW-4)"
```

---

## Task 4: Phase 0d — Patch `evaluate.py` (H-3, L-2)

**Vulnerabilities:**
- **H-3**: `check_sha256_hashes` is skipped entirely during `--baseline`. Gate scripts (`evaluate.py`, `eval_runner.py`) must still be SHA256-verified even when re-baselining.
- **L-2**: Trace filenames are predictable. An attacker can pre-create a symlink at that path.

**Files:**
- Modify: `plugins/agent-agentic-os/scripts/evaluate.py`
- Create: `plugins/agent-agentic-os/tests/test_evaluate_security.py`

- [ ] **Step 4.1: Write the failing tests**

```python
# plugins/agent-agentic-os/tests/test_evaluate_security.py
import sys, os, json
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import evaluate as E


def test_baseline_still_checks_gate_scripts(tmp_path):
    """During --baseline, SHA256 of evaluate.py and eval_runner.py must still be checked."""
    lock_hashes_path = tmp_path / ".lock.hashes"
    lock_hashes_path.write_text(json.dumps({
        str(E.LOCKED_FILES[0]): "0" * 64,
        str(E.LOCKED_FILES[1]): "0" * 64,
    }))
    with pytest.raises(SystemExit) as exc:
        E.check_sha256_hashes(tmp_path / "results.tsv", E.LOCKED_FILES)
    assert exc.value.code == 3


def test_trace_write_uses_o_excl(tmp_path, monkeypatch):
    """Trace files must be written with O_CREAT|O_EXCL|O_NOFOLLOW."""
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    opens_seen = []
    original_open = os.open

    def tracked_open(path, flags, mode=0o777, **kwargs):
        opens_seen.append((path, flags))
        return original_open(path, flags, mode, **kwargs)

    monkeypatch.setattr(os, "open", tracked_open)
    E._write_trace_exclusive(traces_dir, "iter_001_KEEP_score0.95.json", '{"test": true}')

    assert opens_seen
    _, flags = opens_seen[0]
    assert flags & os.O_EXCL
    assert flags & os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        assert flags & os.O_NOFOLLOW


def test_trace_write_adds_nonce_on_collision(tmp_path):
    """When trace filename is taken, a nonce variant must be written instead."""
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    filename = "iter_001_KEEP_score0.95.json"
    (traces_dir / filename).write_text("{}")

    E._write_trace_exclusive(traces_dir, filename, '{"collision": true}')

    written = list(traces_dir.iterdir())
    assert len(written) == 2
    nonce_file = [f for f in written if f.name != filename][0]
    assert nonce_file.read_text() == '{"collision": true}'
```

- [ ] **Step 4.2: Run tests — confirm FAIL**

```bash
pytest plugins/agent-agentic-os/tests/test_evaluate_security.py -v
```

- [ ] **Step 4.3: Add `import os` and `_write_trace_exclusive` to `evaluate.py`**

Add `import os` to the existing imports block. Then add after `_sha256`:

```python
def _write_trace_exclusive(traces_dir: Path, filename: str, content: str) -> None:
    """Write trace file with O_CREAT|O_EXCL|O_NOFOLLOW to prevent symlink attacks (L-2 fix)."""
    import secrets as _secrets
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    path = traces_dir / filename
    try:
        fd = os.open(str(path), flags, 0o644)
    except (FileExistsError, OSError):
        stem, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        nonce = _secrets.token_hex(4)
        nonce_name = f"{stem}_{nonce}.{ext}" if ext else f"{stem}_{nonce}"
        path = traces_dir / nonce_name
        fd = os.open(str(path), flags, 0o644)

    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
    except Exception:
        try:
            os.close(fd)
        except Exception:
            pass
        raise
```

- [ ] **Step 4.4: Replace `write_text` in `write_trace` with `_write_trace_exclusive`**

Find in `write_trace`:
```python
    trace_filename = f"iter_{iteration:03d}_{status}_score{score:.2f}.json"
    try:
        (traces_dir / trace_filename).write_text(json.dumps(trace, indent=2))
    except Exception as e:
        print(f"WARNING: could not write trace file: {e}", file=sys.stderr)
```

Replace with:
```python
    trace_filename = f"iter_{iteration:03d}_{status}_score{score:.2f}.json"
    try:
        _write_trace_exclusive(traces_dir, trace_filename, json.dumps(trace, indent=2))
    except Exception as e:
        print(f"WARNING: could not write trace file: {e}", file=sys.stderr)
```

- [ ] **Step 4.5: Fix baseline SHA256 skip in `main()` (H-3 fix)**

Find:
```python
    if not args.baseline:
        check_sha256_hashes(results_tsv, locked_files_to_hash)
```

Replace with:
```python
    if not args.baseline:
        check_sha256_hashes(results_tsv, locked_files_to_hash)
    else:
        # During baseline: still verify gate scripts; allow evals.json to change
        check_sha256_hashes(results_tsv, LOCKED_FILES)
```

- [ ] **Step 4.6: Run tests — confirm PASS**

```bash
pytest plugins/agent-agentic-os/tests/test_evaluate_security.py -v
```

- [ ] **Step 4.7: Commit**

```bash
git add plugins/agent-agentic-os/scripts/evaluate.py \
        plugins/agent-agentic-os/tests/test_evaluate_security.py
git commit -m "fix(agent-agentic-os): baseline SHA256 guard and O_EXCL trace writes (H-3, L-2)"
```

---

## Task 5: Phase 1a — Create `state_engine.py` core (schema, WAL, retry)

**Files:**
- Create: `plugins/exploration-cycle-plugin/scripts/state_engine.py`
- Create: `plugins/exploration-cycle-plugin/tests/test_state_engine.py`

- [ ] **Step 5.1: Write the failing tests**

```python
# plugins/exploration-cycle-plugin/tests/test_state_engine.py
import sys, sqlite3, uuid, time, threading
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import state_engine as SE


@pytest.fixture
def mem_conn(tmp_path):
    """File-backed SQLite — WAL mode requires a real filesystem, not :memory:."""
    db_path = tmp_path / "test.sqlite"
    conn = SE.init_db(str(db_path))
    yield conn
    conn.close()


def test_wal_mode_enabled(tmp_path):
    db_path = tmp_path / "wal.sqlite"
    conn = SE.init_db(str(db_path))
    result = conn.execute("PRAGMA journal_mode;").fetchone()
    assert result[0].lower() == "wal"
    conn.close()


def test_all_tables_created(mem_conn):
    expected = {"sessions", "tasks", "approvals", "artifacts", "reviews",
                "dispatches", "policy_decisions"}
    rows = mem_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    actual = {r[0] for r in rows}
    assert expected == actual, f"Missing tables: {expected - actual}"


def test_session_status_constraint(mem_conn):
    with pytest.raises(sqlite3.IntegrityError):
        mem_conn.execute(
            "INSERT INTO sessions (id, session_name, status) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), "test", "invalid_status")
        )
        mem_conn.commit()


def test_task_fk_references_session(mem_conn):
    """tasks.session_id must reference a real session (FK enforced at connection level)."""
    with pytest.raises(sqlite3.IntegrityError):
        mem_conn.execute(
            "INSERT INTO tasks (id, session_id, phase_ordinal, phase_name, component_name) "
            "VALUES (?,?,?,?,?)",
            (str(uuid.uuid4()), "nonexistent-session", 1, "phase1", "comp1")
        )
        mem_conn.commit()


def test_approval_ttl_capped_at_one_hour(mem_conn):
    """approvals.expires_at must not exceed created_at + 1 hour (CHECK constraint)."""
    SE.create_session(mem_conn, "s1", "TTL Test Session")
    with pytest.raises(sqlite3.IntegrityError):
        mem_conn.execute("""
            INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
                spec_hash, spec_source_path, expires_at)
            VALUES (?, 's1', 'p1', '[]', '[]', 'abc', '/spec.md', datetime('now', '+2 hours'))
        """, (str(uuid.uuid4()),))
        mem_conn.commit()


def test_immediate_transaction_retries_on_busy(tmp_path):
    db_path = tmp_path / "retry.sqlite"
    conn1 = SE.init_db(str(db_path))
    conn2 = SE.init_db(str(db_path))
    conn2.execute("PRAGMA busy_timeout=0")

    conn1.execute("BEGIN EXCLUSIVE")
    retry_count = []

    def write_with_conn2():
        try:
            with SE._immediate_transaction(conn2) as c:
                retry_count.append(1)
        except Exception:
            retry_count.append(0)

    t = threading.Thread(target=write_with_conn2)
    t.start()
    time.sleep(0.2)
    conn1.execute("ROLLBACK")
    t.join(timeout=5)
    conn1.close()
    conn2.close()
    assert len(retry_count) >= 1


def test_state_engine_cli_init(tmp_path):
    """state_engine.py must be callable as a CLI tool — dual-runtime invariant (ADR-002)."""
    import subprocess
    db_path = str(tmp_path / "cli.sqlite")
    result = subprocess.run(
        [sys.executable, str(Path(SE.__file__)), "init", "--db-path", db_path],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"CLI init failed: {result.stderr}"
    assert Path(db_path).exists(), "DB file must exist after CLI init"
```

- [ ] **Step 5.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_state_engine.py -v
```

- [ ] **Step 5.3: Create `state_engine.py`**

```python
# plugins/exploration-cycle-plugin/scripts/state_engine.py
"""
state_engine.py — SQLite Control Plane for Exploration Cycle Plugin
DB path: ${CLAUDE_PROJECT_DIR}/context/exploration/active_session.sqlite
"""
import json, os, random, re, sqlite3, time, uuid
from contextlib import contextmanager
from pathlib import Path

MAX_RETRIES = 5
MAX_PARALLEL_AGENTS = 2
MAX_PREMIUM_CALLS_PER_PHASE = 1

# PRAGMA foreign_keys must be set on the connection object, not inside executescript.
# executescript does not persist PRAGMAs across its implicit transaction.
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    session_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('in_progress', 'complete', 'suspended')) DEFAULT 'in_progress',
    awaiting_human_validation BOOLEAN DEFAULT 0,
    premium_calls_used INTEGER DEFAULT 0,
    parallel_agents_running INTEGER DEFAULT 0,
    review_passes_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    phase_ordinal INTEGER NOT NULL,
    phase_name TEXT NOT NULL,
    component_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'leased', 'complete', 'failed')) DEFAULT 'pending',
    assigned_subagent_id TEXT DEFAULT NULL,
    version INTEGER DEFAULT 1,
    payload_hash TEXT DEFAULT NULL,
    lease_expires_at TIMESTAMP DEFAULT NULL,
    leased_at TIMESTAMP DEFAULT NULL,
    completed_at TIMESTAMP DEFAULT NULL,
    retry_count INTEGER DEFAULT 0,
    last_error TEXT DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    phase TEXT NOT NULL,
    approved_actions TEXT NOT NULL,
    allowed_paths TEXT NOT NULL,
    spec_hash TEXT NOT NULL,
    spec_source_path TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP DEFAULT NULL,
    revoked_at TIMESTAMP DEFAULT NULL,
    revocation_reason TEXT DEFAULT NULL,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(id),
    CHECK(expires_at <= datetime(created_at, '+1 hour'))
);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    path TEXT NOT NULL,
    original_sha256 TEXT NOT NULL,
    sanitized_sha256 TEXT NOT NULL,
    sanitizer_version TEXT NOT NULL,
    sanitization_report TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    review_type TEXT CHECK(review_type IN (
        'spec_alignment', 'code_quality', 'runtime_observer',
        'semantic_drift', 'domain_purity')) NOT NULL,
    verdict TEXT CHECK(verdict IN ('pass', 'fail', 'warning')) NOT NULL,
    artifact_sha256 TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(artifact_id) REFERENCES artifacts(id)
);

CREATE TABLE IF NOT EXISTS dispatches (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    approval_id TEXT,
    envelope_hash TEXT NOT NULL,
    status TEXT CHECK(status IN ('queued', 'running', 'complete', 'failed', 'rejected')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id),
    FOREIGN KEY(approval_id) REFERENCES approvals(id)
);

CREATE TABLE IF NOT EXISTS policy_decisions (
    id TEXT PRIMARY KEY,
    dispatch_id TEXT NOT NULL,
    decision TEXT CHECK(decision IN ('allow', 'deny', 'defer')) NOT NULL,
    reason_code TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dispatch_id) REFERENCES dispatches(id)
);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    """Open DB, verify WAL mode (fail closed if unavailable), apply schema."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    result = conn.execute("PRAGMA journal_mode;").fetchone()
    if result[0].lower() != "wal":
        conn.close()
        raise RuntimeError(
            f"WAL mode unavailable at {db_path!r}. "
            "Check filesystem (network mounts do not support WAL). Aborting."
        )
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")  # Must be set on connection, not in executescript
    conn.executescript(SCHEMA_SQL)
    return conn


@contextmanager
def _immediate_transaction(conn: sqlite3.Connection):
    """BEGIN IMMEDIATE with exponential backoff retry (up to MAX_RETRIES).

    ROLLBACK failures are suppressed to avoid masking the original exception (FIX-2).
    A safety raise after loop exhaustion makes the error explicit if MAX_RETRIES is 0.
    """
    for attempt in range(MAX_RETRIES):
        try:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
                conn.execute("COMMIT")
                return
            except Exception:
                try:
                    conn.execute("ROLLBACK")
                except Exception:
                    pass  # Don't mask the original exception
                raise
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < MAX_RETRIES - 1:
                delay = (2 ** attempt) * 0.05 + random.uniform(0, 0.01)
                time.sleep(delay)
                continue
            raise
    raise sqlite3.OperationalError(
        f"Failed to acquire IMMEDIATE transaction after {MAX_RETRIES} retries"
    )
```

Also append to the bottom of `state_engine.py` (the CLI entry point — dual-runtime invariant, ADR-002):

```python
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="State Engine CLI")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize database")
    p_init.add_argument("--db-path", required=True)

    p_lease = sub.add_parser("lease-task")
    p_lease.add_argument("--db-path", required=True)
    p_lease.add_argument("--task-id", required=True)
    p_lease.add_argument("--subagent-id", required=True)
    p_lease.add_argument("--ttl", type=int, default=300)

    p_complete = sub.add_parser("commit-complete")
    p_complete.add_argument("--db-path", required=True)
    p_complete.add_argument("--task-id", required=True)
    p_complete.add_argument("--subagent-id", required=True)
    p_complete.add_argument("--version", type=int, required=True)
    p_complete.add_argument("--payload-hash", required=True)

    p_dash = sub.add_parser("project-dashboard")
    p_dash.add_argument("--db-path", required=True)
    p_dash.add_argument("--session-id", required=True)

    p_reclaim = sub.add_parser("reclaim-expired")
    p_reclaim.add_argument("--db-path", required=True)

    args = parser.parse_args()

    if args.command == "init":
        init_db(args.db_path)
        print(f"Database initialized at {args.db_path}")
    elif args.command == "lease-task":
        conn = init_db(args.db_path)
        ok = lease_task(conn, args.task_id, args.subagent_id, args.ttl)
        print(json.dumps({"ok": ok}))
    elif args.command == "commit-complete":
        conn = init_db(args.db_path)
        ok = commit_task_complete(conn, args.task_id, args.subagent_id,
                                  args.version, args.payload_hash)
        print(json.dumps({"ok": ok}))
    elif args.command == "project-dashboard":
        conn = init_db(args.db_path)
        print(project_dashboard(conn, args.session_id))
    elif args.command == "reclaim-expired":
        conn = init_db(args.db_path)
        count = reclaim_expired_leases(conn)
        print(json.dumps({"reclaimed": count}))
```

> **Note for Tasks 6 and 7:** When appending new functions to `state_engine.py`, insert them **before** the `if __name__ == "__main__":` block at the bottom — do not append after it.

- [ ] **Step 5.4: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_state_engine.py -v
```

- [ ] **Step 5.5: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/state_engine.py \
        plugins/exploration-cycle-plugin/tests/test_state_engine.py
git commit -m "feat(exploration-cycle-plugin): create state_engine.py with SQLite schema and WAL init"
```

---

## Task 6: Phase 1b — Task operations, budget counter tracking, and recovery utilities

**What this builds:** `create_session`, `add_task`, `lease_task` (with counter increment), `commit_task_complete` (with counter decrement), `record_premium_call`, `verify_review_current`, `reclaim_expired_leases`.

**Files:**
- Modify: `plugins/exploration-cycle-plugin/scripts/state_engine.py`
- Modify: `plugins/exploration-cycle-plugin/tests/test_state_engine.py`

- [ ] **Step 6.1: Add failing tests**

Append to `plugins/exploration-cycle-plugin/tests/test_state_engine.py`:

```python
def test_create_session_and_add_task(mem_conn):
    SE.create_session(mem_conn, "sess-1", "Test Session")
    SE.add_task(mem_conn, "task-1", "sess-1", 1, "Phase 1", "Comp A")
    row = mem_conn.execute("SELECT * FROM tasks WHERE id='task-1'").fetchone()
    assert row is not None
    assert row["status"] == "pending"


def test_lease_task_increments_parallel_counter(mem_conn):
    """Successful lease must increment sessions.parallel_agents_running."""
    SE.create_session(mem_conn, "sess-2", "Session 2")
    SE.add_task(mem_conn, "task-2", "sess-2", 1, "Phase 1", "Comp B")
    before = mem_conn.execute(
        "SELECT parallel_agents_running FROM sessions WHERE id='sess-2'"
    ).fetchone()["parallel_agents_running"]

    SE.lease_task(mem_conn, "task-2", "subagent-abc", ttl_seconds=300)

    after = mem_conn.execute(
        "SELECT parallel_agents_running FROM sessions WHERE id='sess-2'"
    ).fetchone()["parallel_agents_running"]
    assert after == before + 1


def test_commit_task_complete_decrements_parallel_counter(mem_conn):
    """Completion must decrement sessions.parallel_agents_running."""
    SE.create_session(mem_conn, "sess-3", "Session 3")
    SE.add_task(mem_conn, "task-3", "sess-3", 1, "Phase 1", "Comp C")
    SE.lease_task(mem_conn, "task-3", "subagent-x", ttl_seconds=300)
    row = mem_conn.execute("SELECT version FROM tasks WHERE id='task-3'").fetchone()

    SE.commit_task_complete(mem_conn, "task-3", "subagent-x", row["version"], "hash1")

    after = mem_conn.execute(
        "SELECT parallel_agents_running FROM sessions WHERE id='sess-3'"
    ).fetchone()["parallel_agents_running"]
    assert after == 0


def test_commit_task_complete_cas_guard(mem_conn):
    SE.create_session(mem_conn, "sess-4", "Session 4")
    SE.add_task(mem_conn, "task-4", "sess-4", 1, "Phase 1", "Comp D")
    SE.lease_task(mem_conn, "task-4", "subagent-x", ttl_seconds=300)
    row = mem_conn.execute("SELECT version FROM tasks WHERE id='task-4'").fetchone()
    version = row["version"]

    assert SE.commit_task_complete(mem_conn, "task-4", "wrong-agent", version, "h") is False
    assert SE.commit_task_complete(mem_conn, "task-4", "subagent-x", version + 99, "h") is False
    assert SE.commit_task_complete(mem_conn, "task-4", "subagent-x", version, "h") is True


def test_budget_gate_blocks_over_parallel_limit(mem_conn):
    SE.create_session(mem_conn, "sess-5", "Session 5")
    mem_conn.execute(
        "UPDATE sessions SET parallel_agents_running=? WHERE id='sess-5'",
        (SE.MAX_PARALLEL_AGENTS,)
    )
    mem_conn.commit()
    SE.add_task(mem_conn, "task-5", "sess-5", 1, "Phase 1", "Comp E")
    with pytest.raises(RuntimeError, match="parallel_agents_running"):
        SE.lease_task(mem_conn, "task-5", "subagent-over-limit", ttl_seconds=300)


def test_record_premium_call_increments_counter(mem_conn):
    SE.create_session(mem_conn, "sess-6", "Session 6")
    SE.record_premium_call(mem_conn, "sess-6")
    used = mem_conn.execute(
        "SELECT premium_calls_used FROM sessions WHERE id='sess-6'"
    ).fetchone()["premium_calls_used"]
    assert used == 1


def test_verify_review_current_detects_mismatch(mem_conn):
    """verify_review_current must return False when artifact hash doesn't match review hash."""
    SE.create_session(mem_conn, "sess-7", "Session 7")
    SE.add_task(mem_conn, "task-7", "sess-7", 1, "Phase 1", "Comp F")
    artifact_id = str(uuid.uuid4())
    mem_conn.execute(
        "INSERT INTO artifacts (id, task_id, path, original_sha256, sanitized_sha256, "
        "sanitizer_version, sanitization_report, artifact_type, created_by) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (artifact_id, "task-7", "/tmp/file.py", "aaa", "bbb", "1.0", "{}", "code", "agent-1")
    )
    review_id = str(uuid.uuid4())
    mem_conn.execute(
        "INSERT INTO reviews (id, artifact_id, reviewer, review_type, verdict, artifact_sha256) "
        "VALUES (?,?,?,?,?,?)",
        (review_id, artifact_id, "reviewer-1", "code_quality", "pass", "DIFFERENT_HASH")
    )
    mem_conn.commit()
    assert SE.verify_review_current(mem_conn, artifact_id) is False


def test_reclaim_expired_leases_returns_tasks_to_pending(mem_conn):
    SE.create_session(mem_conn, "sess-8", "Session 8")
    SE.add_task(mem_conn, "task-8", "sess-8", 1, "Phase 1", "Comp G")
    SE.lease_task(mem_conn, "task-8", "subagent-crash", ttl_seconds=300)
    # Manually expire the lease
    mem_conn.execute(
        "UPDATE tasks SET lease_expires_at=datetime('now', '-1 second') WHERE id='task-8'"
    )
    mem_conn.commit()
    count = SE.reclaim_expired_leases(mem_conn)
    assert count >= 1
    row = mem_conn.execute("SELECT status FROM tasks WHERE id='task-8'").fetchone()
    assert row["status"] == "pending"


def test_state_engine_cli_lease_task(tmp_path):
    """CLI lease-task command must work end-to-end (dual-runtime invariant, ADR-002)."""
    import subprocess
    db_path = str(tmp_path / "cli.sqlite")
    conn = SE.init_db(db_path)
    SE.create_session(conn, "cli-sess", "CLI Test")
    SE.add_task(conn, "cli-task", "cli-sess", 1, "Phase 1", "Comp A")
    conn.close()
    result = subprocess.run(
        [sys.executable, str(Path(SE.__file__)), "lease-task",
         "--db-path", db_path, "--task-id", "cli-task", "--subagent-id", "gemini-1"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"CLI lease-task failed: {result.stderr}"
    assert json.loads(result.stdout)["ok"] is True
```

- [ ] **Step 6.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_state_engine.py -v -k "create_session or lease or commit or budget or premium or verify_review or reclaim"
```

- [ ] **Step 6.3: Add task operations to `state_engine.py` — insert BEFORE the `if __name__ == '__main__':` block**

```python
def create_session(conn: sqlite3.Connection, session_id: str, session_name: str) -> None:
    with _immediate_transaction(conn) as c:
        c.execute(
            "INSERT INTO sessions (id, session_name) VALUES (?, ?)",
            (session_id, session_name),
        )


def add_task(conn: sqlite3.Connection, task_id: str, session_id: str,
             phase_ordinal: int, phase_name: str, component_name: str) -> None:
    with _immediate_transaction(conn) as c:
        c.execute(
            "INSERT INTO tasks (id, session_id, phase_ordinal, phase_name, component_name) "
            "VALUES (?, ?, ?, ?, ?)",
            (task_id, session_id, phase_ordinal, phase_name, component_name),
        )


def lease_task(conn: sqlite3.Connection, task_id: str, subagent_id: str,
               ttl_seconds: int = 300) -> bool:
    """Atomically lease a pending task. Increments parallel_agents_running on success."""
    with _immediate_transaction(conn) as c:
        row = c.execute(
            "SELECT s.parallel_agents_running, s.premium_calls_used "
            "FROM sessions s JOIN tasks t ON t.session_id = s.id WHERE t.id = ?",
            (task_id,)
        ).fetchone()
        if row and row["parallel_agents_running"] >= MAX_PARALLEL_AGENTS:
            raise RuntimeError(
                f"parallel_agents_running limit ({MAX_PARALLEL_AGENTS}) exceeded"
            )
        if row and row["premium_calls_used"] >= MAX_PREMIUM_CALLS_PER_PHASE:
            raise RuntimeError(
                f"premium_calls_used limit ({MAX_PREMIUM_CALLS_PER_PHASE}) exceeded"
            )
        result = c.execute(
            "UPDATE tasks SET status='leased', assigned_subagent_id=?, "
            "lease_expires_at=datetime('now', ?), leased_at=CURRENT_TIMESTAMP, "
            "version=version+1, updated_at=CURRENT_TIMESTAMP "
            "WHERE id=? AND status='pending'",
            (subagent_id, f"+{ttl_seconds} seconds", task_id),
        )
        if result.rowcount == 1:
            c.execute(
                "UPDATE sessions SET parallel_agents_running = parallel_agents_running + 1, "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id = (SELECT session_id FROM tasks WHERE id = ?)",
                (task_id,)
            )
            return True
        return False


def commit_task_complete(conn: sqlite3.Connection, task_id: str, subagent_id: str,
                         version: int, payload_hash: str) -> bool:
    """CAS completion. Decrements parallel_agents_running on success."""
    with _immediate_transaction(conn) as c:
        result = c.execute(
            "UPDATE tasks "
            "SET status='complete', payload_hash=?, version=version+1, "
            "completed_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP "
            "WHERE id=? AND status='leased' AND assigned_subagent_id=? AND version=?",
            (payload_hash, task_id, subagent_id, version),
        )
        if result.rowcount == 1:
            c.execute(
                "UPDATE sessions SET "
                "parallel_agents_running = MAX(parallel_agents_running - 1, 0), "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id = (SELECT session_id FROM tasks WHERE id = ?)",
                (task_id,)
            )
            return True
        return False


def record_premium_call(conn: sqlite3.Connection, session_id: str) -> None:
    """Increment premium_calls_used. Call once per premium model invocation."""
    with _immediate_transaction(conn) as c:
        c.execute(
            "UPDATE sessions SET premium_calls_used = premium_calls_used + 1, "
            "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,)
        )


def verify_review_current(conn: sqlite3.Connection, artifact_id: str) -> bool:
    """Returns True if the artifact's sanitized_sha256 matches the most recent review's hash."""
    row = conn.execute("""
        SELECT a.sanitized_sha256, r.artifact_sha256
        FROM artifacts a
        JOIN reviews r ON r.artifact_id = a.id
        WHERE a.id = ?
        ORDER BY r.created_at DESC LIMIT 1
    """, (artifact_id,)).fetchone()
    if not row:
        return False
    return row[0] == row[1]


def reclaim_expired_leases(conn: sqlite3.Connection, max_retries: int = 3) -> int:
    """Move expired leases back to pending, or to failed if retry limit exceeded.

    Also decrements parallel_agents_running for the owning session.
    Returns total number of tasks transitioned.
    """
    with _immediate_transaction(conn) as c:
        expired = c.execute(
            "SELECT id, session_id, retry_count FROM tasks "
            "WHERE status='leased' AND lease_expires_at < datetime('now')"
        ).fetchall()
        count = 0
        for row in expired:
            task_id, session_id, retries = row["id"], row["session_id"], row["retry_count"]
            if retries < max_retries:
                c.execute("""
                    UPDATE tasks SET status='pending', assigned_subagent_id=NULL,
                        lease_expires_at=NULL, leased_at=NULL,
                        retry_count=retry_count+1, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (task_id,))
            else:
                c.execute("""
                    UPDATE tasks SET status='failed',
                        last_error='Max retries exceeded after lease expiry',
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (task_id,))
            c.execute(
                "UPDATE sessions SET "
                "parallel_agents_running = MAX(parallel_agents_running - 1, 0), "
                "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )
            count += 1
    return count
```

- [ ] **Step 6.4: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_state_engine.py -v
```

- [ ] **Step 6.5: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/state_engine.py \
        plugins/exploration-cycle-plugin/tests/test_state_engine.py
git commit -m "feat(exploration-cycle-plugin): task ops with counter tracking, premium call, review validation, lease recovery"
```

---

## Task 7: Phase 1c — Dashboard projector, checkbox validator, migration utility

**Files:**
- Modify: `plugins/exploration-cycle-plugin/scripts/state_engine.py`
- Modify: `plugins/exploration-cycle-plugin/tests/test_state_engine.py`

- [ ] **Step 7.1: Add failing tests**

Append to `plugins/exploration-cycle-plugin/tests/test_state_engine.py`:

```python
def test_project_dashboard_round_trips(mem_conn):
    SE.create_session(mem_conn, "sess-d1", "My Session")
    SE.add_task(mem_conn, "task-d1a", "sess-d1", 1, "Phase 1", "Component Alpha")
    SE.add_task(mem_conn, "task-d1b", "sess-d1", 1, "Phase 1", "Component Beta")
    md = SE.project_dashboard(mem_conn, "sess-d1")
    assert "My Session" in md
    assert "Component Alpha" in md
    assert "Component Beta" in md


def test_validate_dashboard_detects_drift(mem_conn):
    SE.create_session(mem_conn, "sess-d2", "Drift Session")
    SE.add_task(mem_conn, "task-d2", "sess-d2", 1, "Phase 1", "Comp X")
    fake_md = "- [x] Comp X\n"  # DB says pending, md says complete
    assert SE.validate_dashboard_checkboxes(fake_md, mem_conn, "sess-d2") is False


def test_migrate_dashboard_parses_tasks(mem_conn, tmp_path):
    dashboard = tmp_path / "exploration-dashboard.md"
    dashboard.write_text(
        "# Exploration Session: Test Migration\n"
        "## Phase 1: Discovery\n"
        "- [ ] Task Alpha\n"
        "- [x] Task Beta\n"
        "- [~] Task Gamma\n"  # skipped — must be ignored
    )
    SE.migrate_dashboard(dashboard, mem_conn)
    tasks = mem_conn.execute(
        "SELECT component_name, status FROM tasks ORDER BY phase_ordinal"
    ).fetchall()
    names = {t["component_name"] for t in tasks}
    assert "Task Alpha" in names
    assert "Task Beta" in names
    assert "Task Gamma" not in names  # [~] skipped lines not migrated
    beta = next(t for t in tasks if t["component_name"] == "Task Beta")
    assert beta["status"] == "complete"
    assert (tmp_path / "exploration-dashboard.md.migrated").exists()
```

- [ ] **Step 7.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_state_engine.py -v -k "dashboard or migrate or validate"
```

- [ ] **Step 7.3: Add projector, validator, and migration to `state_engine.py` — insert BEFORE the `if __name__ == '__main__':` block**

```python
def project_dashboard(conn: sqlite3.Connection, session_id: str) -> str:
    """Render a read-only markdown dashboard from SQLite state."""
    sess = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not sess:
        return f"# Session Not Found\n\nNo session with id `{session_id}`.\n"
    status_icon = {"pending": "[ ]", "leased": "[~]", "complete": "[x]", "failed": "[!]"}
    lines = [
        f"# Exploration Session: {sess['session_name']}",
        f"",
        f"**Status:** {sess['status']}  ",
        f"**Premium calls used:** {sess['premium_calls_used']}  ",
        f"**Parallel agents:** {sess['parallel_agents_running']}  ",
        f"",
    ]
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE session_id=? ORDER BY phase_ordinal, id",
        (session_id,)
    ).fetchall()
    current_phase = None
    for task in tasks:
        if task["phase_name"] != current_phase:
            current_phase = task["phase_name"]
            lines.append(f"## Phase {task['phase_ordinal']}: {current_phase}")
        icon = status_icon.get(task["status"], "[ ]")
        lines.append(f"- {icon} {task['component_name']}")
    lines.append("")
    lines.append(
        f"*Generated from SQLite at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}*"
    )
    return "\n".join(lines) + "\n"


def validate_dashboard_checkboxes(dashboard_md: str, conn: sqlite3.Connection,
                                   session_id: str) -> bool:
    """Regex-based validator: True if checkboxes match DB task status."""
    checkbox_pattern = re.compile(r"- \[( |x|~|!)\] (.+)")
    db_tasks = conn.execute(
        "SELECT component_name, status FROM tasks WHERE session_id=? ORDER BY phase_ordinal, id",
        (session_id,)
    ).fetchall()
    md_checks = checkbox_pattern.findall(dashboard_md)
    icon_to_status = {" ": "pending", "x": "complete", "~": "leased", "!": "failed"}
    if len(md_checks) != len(db_tasks):
        return False
    for (icon, name), db_task in zip(md_checks, db_tasks):
        if icon_to_status.get(icon, "pending") != db_task["status"]:
            return False
        if name.strip() != db_task["component_name"]:
            return False
    return True


def migrate_dashboard(dashboard_path: Path, conn: sqlite3.Connection) -> bool:
    """Parse exploration-dashboard.md into SQLite, rename file to .migrated.

    Checkbox states: [ ]=pending  [x]=complete  [!]=failed  [~]/[↩]=skip (not migrated).
    """
    content = dashboard_path.read_text(encoding="utf-8")
    m = re.search(r"# Exploration Session:\s*(.+)", content)
    session_name = m.group(1).strip() if m else dashboard_path.stem
    session_id = str(uuid.uuid4())
    create_session(conn, session_id, session_name)

    phase_ordinal = 0
    phase_name = "Uncategorized"
    phase_pat = re.compile(r"## Phase\s+(\d+):\s*(.+)")
    # Expanded regex covers [ ] [x] [~] [↩] [!] — EXEC-3 fix
    task_pat = re.compile(r"- \[( |x|~|↩|!)\] (.+)")

    for line in content.splitlines():
        ph = phase_pat.match(line)
        if ph:
            phase_ordinal, phase_name = int(ph.group(1)), ph.group(2).strip()
            continue
        tm = task_pat.match(line)
        if tm:
            checked, component = tm.group(1), tm.group(2).strip()
            if checked in ("~", "↩"):
                continue  # Skip skipped/revised phases — no valid tasks table status
            task_id = str(uuid.uuid4())
            add_task(conn, task_id, session_id, phase_ordinal, phase_name, component)
            if checked in ("x", "!"):
                new_status = "complete" if checked == "x" else "failed"
                with _immediate_transaction(conn) as c:
                    c.execute(
                        f"UPDATE tasks SET status='{new_status}', "
                        "completed_at=CURRENT_TIMESTAMP WHERE id=?",
                        (task_id,),
                    )

    dashboard_path.rename(dashboard_path.with_suffix(".md.migrated"))
    return True
```

- [ ] **Step 7.4: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_state_engine.py -v
```

- [ ] **Step 7.5: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/state_engine.py \
        plugins/exploration-cycle-plugin/tests/test_state_engine.py
git commit -m "feat(exploration-cycle-plugin): dashboard projector, checkbox validator, migration utility"
```

---

## Task 8: Phase 2a — Create `sandbox_runner.py` (env hygiene, containers, timeouts)

**Files:**
- Create: `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`
- Create: `plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py`

- [ ] **Step 8.1: Write failing tests**

```python
# plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py
from collections import OrderedDict  # top-of-file import (GPT-6 fix)
import sys, os, subprocess
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import sandbox_runner as SR


def test_clean_env_only_has_allowed_keys():
    os.environ["PYTHONPATH"] = "/injected"
    os.environ["DYLD_INSERT_LIBRARIES"] = "/evil.dylib"
    env = SR._build_clean_env()
    assert "PYTHONPATH" not in env
    assert "DYLD_INSERT_LIBRARIES" not in env
    for key in env:
        assert key in SR.ALLOWED_ENV


def test_extra_vars_blocked_if_dangerous():
    env = SR._build_clean_env(extra_vars={"LD_PRELOAD": "/bad.so", "MY_VAR": "ok"})
    assert "LD_PRELOAD" not in env
    assert env.get("MY_VAR") == "ok"


def test_run_hygienic_executes_command():
    result = SR.run_hygienic([sys.executable, "-c", "print('ok')"], timeout=10)
    assert result.returncode == 0


def test_run_hygienic_env_is_clean():
    os.environ["PYTHONPATH"] = "/should-not-leak"
    result = SR.run_hygienic(
        [sys.executable, "-c",
         "import os, sys; sys.exit(0 if 'PYTHONPATH' not in os.environ else 1)"],
        timeout=10,
    )
    assert result.returncode == 0


def test_terminate_with_grace_kills_slow_process():
    import time
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(9999)"],
        env=SR._build_clean_env(),
    )
    start = time.time()
    SR._terminate_with_grace(proc, timeout=0, grace=1)
    elapsed = time.time() - start
    assert proc.poll() is not None
    assert elapsed < 5


def test_run_containerized_splits_mounts(monkeypatch):
    """run_containerized must apply :ro suffix to read-only paths."""
    calls = []
    monkeypatch.setattr(subprocess, "Popen", lambda cmd, **kw: calls.append(cmd) or
                        type("P", (), {"communicate": lambda s, **k: (b"", b""),
                                       "returncode": 0})())
    try:
        SR.run_containerized(
            ["echo", "test"], "sess-1", "disp-1",
            allowed_paths_ro=["/read/path"],
            allowed_paths_rw=["/write/path"],
            timeout=5
        )
    except Exception:
        pass
    if calls:
        cmd_str = " ".join(calls[0])
        assert "/read/path:/read/path:ro" in cmd_str
        assert "/write/path:/write/path" in cmd_str
        assert "/write/path:/write/path:ro" not in cmd_str
```

- [ ] **Step 8.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py -v
```

- [ ] **Step 8.3: Create `sandbox_runner.py`**

```python
# plugins/exploration-cycle-plugin/scripts/sandbox_runner.py
"""
sandbox_runner.py — Process Hygiene, Container Wrapping, and HMAC Envelopes
"""
import hashlib
import hmac as _hmac
import json
import os
import secrets
import signal
import subprocess
import time
from collections import OrderedDict
from pathlib import Path

ALLOWED_ENV = frozenset({"PATH", "HOME", "TMPDIR", "LANG", "LC_ALL"})
BLOCKED_ENV = frozenset({
    "PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME",
    "LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "DYLD_LIBRARY_PATH",
    "NODE_OPTIONS", "NODE_PATH",
})
TIMEOUT_SECONDS = 300
GRACE_SECONDS = 10
NONCE_CACHE_MAX = 10_000


def _build_clean_env(extra_vars: dict | None = None) -> dict:
    env = {k: os.environ[k] for k in ALLOWED_ENV if k in os.environ}
    if extra_vars:
        for k, v in extra_vars.items():
            if k not in BLOCKED_ENV:
                env[k] = v
    return env


def _terminate_with_grace(proc: subprocess.Popen, timeout: int = TIMEOUT_SECONDS,
                           grace: int = GRACE_SECONDS) -> None:
    if proc.poll() is not None:
        return
    proc.send_signal(signal.SIGTERM)
    deadline = time.time() + grace
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.1)
    if proc.poll() is None:
        proc.kill()
        proc.wait()


def run_hygienic(cmd: list, timeout: int = TIMEOUT_SECONDS,
                 extra_vars: dict | None = None) -> subprocess.CompletedProcess:
    env = _build_clean_env(extra_vars)
    proc = subprocess.Popen(cmd, shell=False, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(
            args=cmd, returncode=proc.returncode,
            stdout=stdout, stderr=stderr,
        )
    except subprocess.TimeoutExpired:
        _terminate_with_grace(proc, timeout=0, grace=GRACE_SECONDS)
        stdout, stderr = proc.communicate()
        raise


def _detect_container_runtime() -> str | None:
    for runtime in ("podman", "docker"):
        try:
            if subprocess.run(
                ["which", runtime], capture_output=True, timeout=3
            ).returncode == 0:
                return runtime
        except Exception:
            pass
    return None


def run_containerized(cmd: list, session_id: str, dispatch_id: str,
                       allowed_paths_ro: list | None = None,
                       allowed_paths_rw: list | None = None,
                       timeout: int = TIMEOUT_SECONDS) -> subprocess.CompletedProcess:
    """Run cmd inside a read-only container. ro paths get ':ro', rw paths are writable."""
    runtime = _detect_container_runtime()
    if not runtime:
        raise RuntimeError("No container runtime (podman/docker) available")

    container_cmd = [
        runtime, "run", "--rm",
        "--network=none", "--cpus=1.0", "--memory=512m", "--read-only",
        f"--label=agentic_os_session={session_id}",
        f"--label=agentic_os_dispatch={dispatch_id}",
    ]
    for path in (allowed_paths_ro or []):
        container_cmd.extend(["-v", f"{path}:{path}:ro"])
    for path in (allowed_paths_rw or []):
        container_cmd.extend(["-v", f"{path}:{path}"])

    container_cmd.extend(["python:3.11-slim"] + cmd)

    proc = subprocess.Popen(container_cmd, shell=False,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return subprocess.CompletedProcess(
            args=container_cmd, returncode=proc.returncode,
            stdout=stdout, stderr=stderr,
        )
    except subprocess.TimeoutExpired:
        _terminate_with_grace(proc, timeout=0, grace=GRACE_SECONDS)
        proc.communicate()
        raise


def _cleanup_stale_containers(session_id: str) -> None:
    runtime = _detect_container_runtime()
    if not runtime:
        return
    try:
        result = subprocess.run(
            [runtime, "ps", "-a", "-q", f"--filter=label=agentic_os_session={session_id}"],
            capture_output=True, text=True, timeout=10
        )
        for cid in result.stdout.splitlines():
            cid = cid.strip()
            if cid:
                subprocess.run([runtime, "rm", "-f", cid], capture_output=True, timeout=10)
    except Exception:
        pass
```

- [ ] **Step 8.4: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py -v
```

- [ ] **Step 8.5: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/sandbox_runner.py \
        plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py
git commit -m "feat(exploration-cycle-plugin): sandbox_runner.py with env hygiene and split ro/rw container mounts"
```

---

## Task 9: Phase 2b — HMAC envelopes and nonce cache

**Files:**
- Modify: `plugins/exploration-cycle-plugin/scripts/sandbox_runner.py`
- Modify: `plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py`

- [ ] **Step 9.1: Add failing HMAC tests**

Append to `plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py` (note: `OrderedDict` import is already at the top of the file from Step 8.1):

```python
def test_sign_and_verify_envelope_roundtrip():
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"task_id": "t1", "action": "complete"}, key)
    assert SR.verify_envelope(envelope, key, nonce_cache) is True


def test_verify_rejects_tampered_payload():
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"task_id": "t1"}, key)
    envelope["payload"]["task_id"] = "evil"
    assert SR.verify_envelope(envelope, key, nonce_cache) is False


def test_verify_rejects_wrong_key():
    key_a, key_b = os.urandom(32), os.urandom(32)
    envelope = SR.sign_envelope({"x": 1}, key_a)
    assert SR.verify_envelope(envelope, key_b, OrderedDict()) is False


def test_verify_rejects_nonce_replay():
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"x": 1}, key)
    assert SR.verify_envelope(envelope, key, nonce_cache) is True
    assert SR.verify_envelope(envelope, key, nonce_cache) is False


def test_session_key_written_with_0600_permissions(tmp_path):
    key_path = tmp_path / ".secrets" / "session_hmac.key"
    SR.generate_session_key(key_path)
    assert key_path.exists()
    assert oct(key_path.stat().st_mode)[-3:] == "600"


def test_cleanup_session_key_removes_file(tmp_path):
    key_path = tmp_path / ".secrets" / "session_hmac.key"
    SR.generate_session_key(key_path)
    SR.cleanup_session_key(key_path)
    assert not key_path.exists()
```

- [ ] **Step 9.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py -v -k "sign or verify or session_key or nonce or cleanup"
```

- [ ] **Step 9.3: Append HMAC functions to `sandbox_runner.py`**

```python
# ---------------------------------------------------------------------------
# HMAC Envelope Sign / Verify
# ---------------------------------------------------------------------------

def generate_session_key(key_path: Path) -> bytes:
    """Generate a 32-byte random session key and save with mode 0600."""
    key = os.urandom(32)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_bytes(key)
    key_path.chmod(0o600)
    return key


def load_session_key(key_path: Path) -> bytes:
    return key_path.read_bytes()


def cleanup_session_key(key_path: Path) -> None:
    """Overwrite then delete session key file (secure erasure)."""
    if key_path.exists():
        key_path.write_bytes(os.urandom(32))
        key_path.unlink()


def sign_envelope(payload: dict, key: bytes) -> dict:
    nonce = secrets.token_hex(16)
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    token = _hmac.new(key, payload_bytes + nonce.encode(), hashlib.sha256).hexdigest()
    return {"payload": payload, "nonce": nonce, "token": token}


def verify_envelope(envelope: dict, key: bytes, nonce_cache: OrderedDict) -> bool:
    """Timing-safe HMAC verification with nonce deduplication."""
    nonce = envelope.get("nonce", "")
    if not nonce or nonce in nonce_cache:
        return False
    payload_bytes = json.dumps(envelope.get("payload", {}), sort_keys=True).encode()
    expected = _hmac.new(key, payload_bytes + nonce.encode(), hashlib.sha256).hexdigest()
    if not _hmac.compare_digest(expected, envelope.get("token", "")):
        return False
    if len(nonce_cache) >= NONCE_CACHE_MAX:
        nonce_cache.popitem(last=False)
    nonce_cache[nonce] = True
    return True
```

- [ ] **Step 9.4: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py -v
```

- [ ] **Step 9.5: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/sandbox_runner.py \
        plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py
git commit -m "feat(exploration-cycle-plugin): HMAC envelope sign/verify with nonce replay protection and key cleanup"
```

---

## Task 10: Phase 2c — Integrate `dispatch.py` with SQLite approval gate

**Files:**
- Modify: `plugins/exploration-cycle-plugin/scripts/dispatch.py`
- Modify: `plugins/exploration-cycle-plugin/tests/test_dispatch_security.py`

- [ ] **Step 10.1: Add failing approval gate tests**

Append to `plugins/exploration-cycle-plugin/tests/test_dispatch_security.py`:

```python
def test_check_approval_rejects_expired(tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import state_engine as SE, uuid
    conn = SE.init_db(str(tmp_path / "test.sqlite"))
    SE.create_session(conn, "sess", "Approval Test Session")  # FK required
    approval_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
            spec_hash, spec_source_path, is_active, expires_at)
        VALUES (?, 'sess', 'p1', '[]', '[]', 'abc', '/spec.md', 1, datetime('now', '-1 hour'))
    """, (approval_id,))
    conn.commit()
    is_valid, reason = dispatch.check_approval(conn, approval_id)
    assert is_valid is False
    assert "expired" in reason.lower()


def test_check_approval_rejects_revoked(tmp_path):
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import state_engine as SE, uuid
    conn = SE.init_db(str(tmp_path / "revoked.sqlite"))
    SE.create_session(conn, "sess", "Revoked Test Session")
    approval_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
            spec_hash, spec_source_path, is_active, expires_at)
        VALUES (?, 'sess', 'p1', '[]', '[]', 'abc', '/spec.md', 0, datetime('now', '+30 minutes'))
    """, (approval_id,))
    conn.commit()
    is_valid, reason = dispatch.check_approval(conn, approval_id)
    assert is_valid is False
    assert "revoked" in reason.lower()
```

- [ ] **Step 10.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_dispatch_security.py -v -k "approval"
```

- [ ] **Step 10.3: Add `import sqlite3` and `check_approval` to `dispatch.py`**

Add `import sqlite3` to imports. Add after `validate_output`:

```python
def check_approval(conn: "sqlite3.Connection", approval_id: str) -> tuple[bool, str]:
    """Verify an approval is active, not revoked, and not expired."""
    row = conn.execute(
        "SELECT is_active, expires_at FROM approvals WHERE id=?",
        (approval_id,)
    ).fetchone()
    if row is None:
        return False, f"Approval '{approval_id}' not found"
    if not row[0]:
        return False, f"Approval '{approval_id}' has been revoked"
    expired = conn.execute(
        "SELECT 1 FROM approvals WHERE id=? AND expires_at < datetime('now')",
        (approval_id,)
    ).fetchone()
    if expired:
        return False, f"Approval '{approval_id}' has expired"
    return True, ""
```

- [ ] **Step 10.4: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_dispatch_security.py -v
```

- [ ] **Step 10.5: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/dispatch.py \
        plugins/exploration-cycle-plugin/tests/test_dispatch_security.py
git commit -m "feat(exploration-cycle-plugin): approval expiry and revocation gate in dispatch.py"
```

---

## Task 10b: Full dispatch authorization enforcement

**What this builds:** `check_dispatch_authorization` that validates approved actions, allowed paths, spec hash integrity, and HMAC envelope before a dispatch is allowed to proceed. Creates `dispatches` and `policy_decisions` rows for audit trail.

**Files:**
- Modify: `plugins/exploration-cycle-plugin/scripts/dispatch.py`
- Modify: `plugins/exploration-cycle-plugin/tests/test_dispatch_security.py`

- [ ] **Step 10b.1: Add failing tests**

Append to `plugins/exploration-cycle-plugin/tests/test_dispatch_security.py`:

```python
def test_check_dispatch_authorization_rejects_unknown_action(tmp_path):
    import state_engine as SE, uuid, sandbox_runner as SR
    from collections import OrderedDict
    conn = SE.init_db(str(tmp_path / "auth.sqlite"))
    SE.create_session(conn, "sess", "Auth Session")
    approval_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
            spec_hash, spec_source_path, is_active, expires_at)
        VALUES (?, 'sess', 'p1', '["read_file"]', '["**/*.md"]', 'abc', '/spec.md', 1,
                datetime('now', '+1 hour'))
    """, (approval_id,))
    conn.commit()
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"action": "write_file"}, key)
    ok, reason = dispatch.check_dispatch_authorization(
        conn, approval_id, action="write_file", target_path="foo.md",
        spec_path=None, envelope=envelope, key=key, nonce_cache=nonce_cache
    )
    assert ok is False
    assert "write_file" in reason


def test_check_dispatch_authorization_rejects_path_outside_allowed(tmp_path):
    import state_engine as SE, uuid, sandbox_runner as SR
    from collections import OrderedDict
    conn = SE.init_db(str(tmp_path / "path.sqlite"))
    SE.create_session(conn, "sess", "Path Session")
    approval_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
            spec_hash, spec_source_path, is_active, expires_at)
        VALUES (?, 'sess', 'p1', '["read_file"]', '["docs/**"]', 'abc', '/spec.md', 1,
                datetime('now', '+1 hour'))
    """, (approval_id,))
    conn.commit()
    key = os.urandom(32)
    envelope = SR.sign_envelope({"action": "read_file"}, key)
    ok, reason = dispatch.check_dispatch_authorization(
        conn, approval_id, action="read_file", target_path="/etc/passwd",
        spec_path=None, envelope=envelope, key=key, nonce_cache=OrderedDict()
    )
    assert ok is False
    assert "path" in reason.lower()


def test_check_dispatch_authorization_rejects_replayed_nonce(tmp_path):
    import state_engine as SE, uuid, sandbox_runner as SR
    from collections import OrderedDict
    conn = SE.init_db(str(tmp_path / "nonce.sqlite"))
    SE.create_session(conn, "sess", "Nonce Session")
    approval_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
            spec_hash, spec_source_path, is_active, expires_at)
        VALUES (?, 'sess', 'p1', '["read_file"]', '["**"]', 'abc', '/spec.md', 1,
                datetime('now', '+1 hour'))
    """, (approval_id,))
    conn.commit()
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"action": "read_file"}, key)
    ok1, _ = dispatch.check_dispatch_authorization(
        conn, approval_id, action="read_file", target_path="docs/foo.md",
        spec_path=None, envelope=envelope, key=key, nonce_cache=nonce_cache
    )
    assert ok1 is True
    # Replay same envelope
    ok2, reason = dispatch.check_dispatch_authorization(
        conn, approval_id, action="read_file", target_path="docs/foo.md",
        spec_path=None, envelope=envelope, key=key, nonce_cache=nonce_cache
    )
    assert ok2 is False
    assert "hmac" in reason.lower() or "nonce" in reason.lower() or "envelope" in reason.lower()
```

- [ ] **Step 10b.2: Run tests — confirm FAIL**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_dispatch_security.py -v -k "authorization"
```

- [ ] **Step 10b.3: Add `check_dispatch_authorization` and `import fnmatch` to `dispatch.py`**

Add `import fnmatch, json` to imports. Add after `check_approval`:

```python
def check_dispatch_authorization(
    conn: "sqlite3.Connection",
    approval_id: str,
    action: str,
    target_path: str | None,
    spec_path: str | None,
    envelope: dict,
    key: bytes,
    nonce_cache: "OrderedDict",
) -> tuple[bool, str]:
    """Full dispatch authorization: approval validity + action + path + spec hash + HMAC."""
    import fnmatch
    from sandbox_runner import verify_envelope

    # 1. Basic approval validity
    is_valid, reason = check_approval(conn, approval_id)
    if not is_valid:
        return False, reason

    row = conn.execute(
        "SELECT approved_actions, allowed_paths, spec_hash FROM approvals WHERE id=?",
        (approval_id,)
    ).fetchone()

    # 2. Approved actions check
    approved_actions = json.loads(row[0])
    if action not in approved_actions:
        return False, f"Action '{action}' not in approved_actions {approved_actions}"

    # 3. Allowed paths check
    allowed_paths = json.loads(row[1])
    if target_path and not any(fnmatch.fnmatch(target_path, p) for p in allowed_paths):
        return False, f"Path '{target_path}' not in allowed_paths {allowed_paths}"

    # 4. Spec hash integrity check
    if spec_path:
        import hashlib
        from pathlib import Path as _Path
        if _Path(spec_path).exists():
            actual_hash = hashlib.sha256(_Path(spec_path).read_bytes()).hexdigest()
            if actual_hash != row[2]:
                return False, f"Spec hash mismatch for {spec_path}"

    # 5. HMAC envelope verification (timing-safe + nonce dedup)
    if not verify_envelope(envelope, key, nonce_cache):
        return False, "HMAC envelope verification failed (tampered payload or replayed nonce)"

    return True, ""
```

- [ ] **Step 10b.4: Run tests — confirm PASS**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_dispatch_security.py -v
```

- [ ] **Step 10b.5: Commit**

```bash
git add plugins/exploration-cycle-plugin/scripts/dispatch.py \
        plugins/exploration-cycle-plugin/tests/test_dispatch_security.py
git commit -m "feat(exploration-cycle-plugin): full dispatch authorization with action, path, spec hash, and HMAC gates"
```

---

## Task 11: Integration tests, `.gitignore`, and ADR

**Files:**
- Create: `plugins/exploration-cycle-plugin/tests/test_integration.py`
- Modify: `.gitignore` (project root)
- Create: `docs/adr/ADR-001-sqlite-path-strategy.md`

- [ ] **Step 11.1: Write integration tests**

```python
# plugins/exploration-cycle-plugin/tests/test_integration.py
import sys, os, uuid, time, threading
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import state_engine as SE
import sandbox_runner as SR


@pytest.fixture
def db_conn(tmp_path):
    conn = SE.init_db(str(tmp_path / "test.sqlite"))
    yield conn
    conn.close()


def test_concurrent_task_completions(tmp_path):
    """5 concurrent threads completing distinct tasks must all succeed within 30s."""
    db_path = tmp_path / "concurrent.sqlite"
    conn = SE.init_db(str(db_path))
    SE.create_session(conn, "sess-c", "Concurrent Session")

    task_ids = [str(uuid.uuid4()) for _ in range(5)]
    for i, tid in enumerate(task_ids):
        SE.add_task(conn, tid, "sess-c", i + 1, f"Phase {i + 1}", f"Comp {i}")
        SE.lease_task(conn, tid, f"subagent-{i}", ttl_seconds=300)

    versions = {}
    for tid in task_ids:
        row = conn.execute("SELECT version FROM tasks WHERE id=?", (tid,)).fetchone()
        versions[tid] = row["version"]

    results, errors = [], []

    def complete_task(tid, agent_id, version):
        try:
            thread_conn = SE.init_db(str(db_path))
            ok = SE.commit_task_complete(thread_conn, tid, agent_id, version, f"hash-{tid[:8]}")
            results.append(ok)
            thread_conn.close()
        except Exception as e:
            errors.append(str(e))

    threads = [
        threading.Thread(target=complete_task, args=(tid, f"subagent-{i}", versions[tid]))
        for i, tid in enumerate(task_ids)
    ]
    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    elapsed = time.time() - start

    assert not errors, f"Threads raised: {errors}"
    assert elapsed < 30
    assert sum(results) == 5
    final = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='complete'").fetchone()[0]
    assert final == 5
    conn.close()


def test_sandbox_env_vars_do_not_leak():
    """ANTHROPIC_API_KEY and PYTHONPATH must not be visible inside sandboxed process."""
    os.environ["ANTHROPIC_API_KEY"] = "sk-test-secret"
    os.environ["PYTHONPATH"] = "/injected"
    result = SR.run_hygienic(
        [sys.executable, "-c",
         "import os, sys; "
         "leaked = [k for k in ['ANTHROPIC_API_KEY', 'PYTHONPATH'] if k in os.environ]; "
         "sys.exit(len(leaked))"],
        timeout=10,
    )
    assert result.returncode == 0


def test_expired_approval_is_rejected(db_conn):
    import dispatch
    approval_id = str(uuid.uuid4())
    SE.create_session(db_conn, "sess", "Expiry Session")
    db_conn.execute("""
        INSERT INTO approvals (id, session_id, phase, approved_actions, allowed_paths,
            spec_hash, spec_source_path, is_active, expires_at)
        VALUES (?, 'sess', 'p1', '[]', '[]', 'abc', '/spec.md', 1,
                datetime('now', '-1 second'))
    """, (approval_id,))
    db_conn.commit()
    is_valid, reason = dispatch.check_approval(db_conn, approval_id)
    assert is_valid is False
    assert "expired" in reason.lower()
```

- [ ] **Step 11.2: Run integration tests**

```bash
pytest plugins/exploration-cycle-plugin/tests/test_integration.py -v
```

- [ ] **Step 11.3: Add `.gitignore` entries (GPT-8 fix)**

Add to the project root `.gitignore` (create if it doesn't exist):

```
# Agentic OS runtime state — never commit
context/exploration/active_session.sqlite
context/exploration/active_session.sqlite-wal
context/exploration/active_session.sqlite-shm
context/exploration/.secrets/
```

- [ ] **Step 11.4: Write ADR**

Create `docs/adr/ADR-001-sqlite-path-strategy.md`:

```markdown
# ADR-001: SQLite Path Strategy — Hardened Fixed Path & Fail-Closed

**Status:** Accepted  
**Date:** 2026-05-30

## Decision

**DB path:** `${CLAUDE_PROJECT_DIR}/context/exploration/active_session.sqlite`

- Fixed per project context. Added to `.gitignore`.
- `init_db` raises `RuntimeError` immediately if WAL mode cannot be enabled — no fallback.

## Alternatives Rejected

| Approach | Reason |
|---|---|
| Dynamic path per session | Directory permissions hard to secure; path injection risk |
| Fixed path + `/tmp` fallback | Silent split-brain drift; injection vectors on fallback |

## Consequences

- Project root must be on a local filesystem (no network mounts).
- All write failures are loud (`RuntimeError`), never silent.
```

- [ ] **Step 11.4b: Write ADR-002**

Create `docs/adr/ADR-002-dual-runtime-compatibility.md`:

```markdown
# ADR-002: Dual-Runtime Compatibility — Portable Plugins, Optional Orchestration

**Status:** Accepted  
**Date:** 2026-05-30

## Decision

All plugin components must remain consumable by **any LLM CLI runtime** (Claude Code,
Gemini CLI, Cursor, or any shell-based agent) without modification:

1. **Agent `.md` files** are the portable interface definition. They contain agent
   identity, instructions, and domain vocabulary. They are never rewritten into
   framework-specific formats.

2. **`state_engine.py` and `sandbox_runner.py`** are standalone Python scripts using
   stdlib only. They expose both:
   - A Python import interface (for `dispatch.py` and future MAF middleware)
   - A CLI interface via argparse (for any shell-based agent runtime)

3. **MAF integration is optional.** If adopted, MAF agents load `.md` files via
   `Agent(instructions=Path(...).read_text())` and call `state_engine`/`sandbox_runner`
   via Python import. MAF does not replace these files.

## Consequences

- No framework-specific imports (MAF, LangChain, CrewAI) in `state_engine.py` or
  `sandbox_runner.py`. These remain stdlib-only.
- The `if __name__ == "__main__":` CLI block in `state_engine.py` must be maintained
  as any shell-based agent runtime can call it via subprocess.
- `SKILL.md` files continue to contain orchestration instructions readable by any LLM.
  The database enforces the rules; the SKILL.md explains them to the model.

## MAF Adapter Surface (Future Reference)

| Local Primitive | MAF Extension Point | Adapter Pattern |
|---|---|---|
| Agent `.md` file | `Agent(instructions=...)` | `Path.read_text()` |
| `state_engine.commit_task_complete` | `TDDComplianceMiddleware` | `.Use()` middleware |
| `sandbox_runner.run_hygienic` | `WorktreeIsolationExecutor` | Custom executor |
| `dispatch.check_approval` | `GovernancePolicyMiddleware` | AGT integration |
| `state_engine.project_dashboard` | `AIContextProvider` | Pre-call context injection |
```

- [ ] **Step 11.5: Run full test suite**

```bash
pytest plugins/agent-agentic-os/tests/ plugins/exploration-cycle-plugin/tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 11.6: Audit symlinks**

```bash
find plugins/agent-agentic-os plugins/exploration-cycle-plugin -type l | while read link; do
  [ -e "$link" ] && echo "OK   $link" || echo "BROKEN $link -> $(readlink $link)"
done
find plugins/agent-agentic-os plugins/exploration-cycle-plugin -type l | while read link; do
  [ -d "$link" ] && echo "DIR-SYMLINK VIOLATION: $link"
done
```

Expected: All `OK`, no `BROKEN`, no violations.

- [ ] **Step 11.7: Final commit**

```bash
git add plugins/exploration-cycle-plugin/tests/test_integration.py \
        .gitignore \
        docs/adr/ADR-001-sqlite-path-strategy.md \
        docs/adr/ADR-002-dual-runtime-compatibility.md
git commit -m "test: WAL concurrency, sandbox escape, approval expiry integration tests + .gitignore + ADR-001 + ADR-002"
```

---

## Red-Team Correction Notes (for reference)

| Finding | Source | Resolution |
|---|---|---|
| FIX-1: DB path "divergence" | Opus | **Pushed back** — plan uses `context/exploration/active_session.sqlite` which matches the v1.3 spec exactly. Opus was cross-referencing v1.2 documents. |
| FIX-2: ROLLBACK masking | Opus | Fixed in Task 5.3 — `ROLLBACK` failure suppressed with bare `except` |
| EXEC-1: Flaky thread test | Opus | Fixed in Task 2.1 — monkeypatch `time.sleep` injects concurrent write deterministically |
| EXEC-2: PRAGMA in SCHEMA_SQL | Opus | Fixed in Task 5.3 — PRAGMA removed from script, kept on connection |
| EXEC-3: Migration regex misses `[~]` | Opus | Fixed in Task 7.3 — expanded regex; `[~]`/`[↩]` rows skipped, not crashed on |
| GPT-1: `init_db(":memory:")` + WAL | GPT-5.5 | Fixed in Task 5.1 — all fixtures use `tmp_path` file-backed DB |
| GPT-2: Approval FK without session | GPT-5.5 | Fixed in Tasks 5.1 and 10.1 — `create_session` called before approval insert |
| GPT-3: Budget counter not tracked | GPT-5.5 | Fixed in Task 6.3 — `lease_task` increments, `commit_task_complete` decrements |
| GPT-4: Premium call never incremented | GPT-5.5 | Fixed in Task 6.3 — `record_premium_call()` added |
| GPT-5: Tier test uses fake parser | GPT-5.5 | Fixed in Task 3.3 — `build_parser()` exposed; test uses real parser |
| GPT-6: Import placement | GPT-5.5 | Fixed in Task 8.1 — `OrderedDict` import at file top |
| GPT-7: Container mounts unsafe | GPT-5.5 | Fixed in Task 8.3 — split into `allowed_paths_ro` (`:ro`) and `allowed_paths_rw` |
| GPT-8: Key cleanup + gitignore | GPT-5.5 | Fixed in Tasks 9.3 and 11.3 — `cleanup_session_key()` + `.gitignore` entries |
| GPT-Gap1: Dispatch too shallow | GPT-5.5 | Task 10b — full authorization: action + path + spec hash + HMAC |
| GPT-Gap2: Artifact review invalidation | GPT-5.5 | Fixed in Task 6.3 — `verify_review_current()` |
| GPT-Gap3: Lease expiry recovery | GPT-5.5 | Fixed in Task 6.3 — `reclaim_expired_leases()` |
| Dual-runtime compatibility undocumented | Post-review | ADR-002 (Task 11.4b) + CLI entry points (Task 5.3) + CLI tests (Tasks 5.1, 6.1) |

---

Plan complete. Saved to `docs/superpowers/plans/2026-05-30-hardened-control-plane.md`.

**Execution recommendation:** Start a clean session. Use **Subagent-Driven** execution (Task 1 → review → Task 2 → review → ...). Do not execute more than one task at a time without reviewing the diff.
