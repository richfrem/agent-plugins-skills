# Optimizer Engine Patterns — Reference Design

These patterns are validated through red team audit cycles on the exploration-cycle-plugin optimizer
(v4–v6). They apply to any optimizer loop that uses `eval_runner.py` as a subprocess scorer and
manages a target file with propose → test → decide iterations.

---

## Pattern 1: YAML Frontmatter Strip Before Agent Prompt Injection

**Problem:** SKILL.md files carry YAML frontmatter metadata (`--- ... ---`). When a SKILL.md is
passed as an agent prompt, the model treats the frontmatter description as additional instructions,
causing prompt confusion.

**Fix:** Strip frontmatter before passing content to the agent dispatcher:

```python
import re

skill_content = Path(target_skill).read_text(encoding="utf-8")
# Use [\r\n]+ to tolerate both POSIX and Windows line endings
stripped = re.sub(r'^---[\r\n]+.*?[\r\n]+---[\r\n]+', '', skill_content, count=1, flags=re.DOTALL)
stripped_path = Path(target_skill).with_suffix(".stripped.md")
stripped_path.write_text(stripped, encoding="utf-8")
# ... pass stripped_path to dispatcher ...
stripped_path.unlink(missing_ok=True)  # clean up immediately after subprocess returns
```

**Notes:**
- `re.sub` with `count=1` only strips the first `---` block (the frontmatter), not any later `---` dividers.
- If no frontmatter is present, `re.sub` returns the content unchanged — this is a safe no-op.
- The `.stripped.md` temp file persists if the process is SIGKILLed between write and unlink.
  This is an acceptable hazard; nothing should glob the skill directory for `.stripped.md`.

---

## Pattern 2: Consecutive Failure Counter with Backup Restoration

**Problem:** If the artifact eval subprocess fails repeatedly, the optimizer silently falls back to
the routing-only score and may accept a proposal based on incomplete signal. Three consecutive
failures likely indicate a broken eval environment that won't recover.

**Fix:** Mutable counter in closure; abort with backup restoration after N failures:

```python
artifact_fail_streak = [0]  # mutable list used as closure variable (avoids `nonlocal`)
MAX_ARTIFACT_FAILURES = 3

def combined_score(skill_path):
    artifact = run_artifact_eval(...)
    if artifact < 0:
        artifact_fail_streak[0] += 1
        if artifact_fail_streak[0] >= MAX_ARTIFACT_FAILURES:
            print(f"Fatal: artifact eval failed {MAX_ARTIFACT_FAILURES} consecutive times. "
                  "Restoring from backup and aborting.", file=sys.stderr)
            # Restore before abort — sys.exit(1) raises SystemExit(BaseException),
            # which bypasses the iteration's `except Exception` backup-restore block.
            if backup_path.exists():
                shutil.copy(backup_path, target_path)
                os.remove(backup_path)
            sys.exit(1)
        return routing  # fall back to routing score for this iteration
    artifact_fail_streak[0] = 0  # reset on any success
    return (artifact * 0.7) + (routing * 0.3)
```

**Critical:** Restore from backup BEFORE calling `sys.exit(1)`. `SystemExit` is a `BaseException`
and bypasses `except Exception` blocks — without the explicit restore, the target file is left in
the proposed (unevaluated) state and an orphaned `.bak` is stranded on disk.

**Style note:** `[0]` mutable list is correct Python for closure mutation but unconventional.
A `nonlocal` declaration is the idiomatic alternative if the counter is in a nested function.

---

## Pattern 3: Orphaned Backup Warning

**Problem:** If a previous optimizer run exited uncleanly (SIGKILL, unhandled exception, power
loss), a `.bak` file persists next to the target. On the next run, `shutil.copy` silently
overwrites it, destroying the previous clean state.

**Fix:** Warn before overwriting:

```python
backup_path = target_path.with_suffix(target_path.suffix + ".bak")
if backup_path.exists():
    print(
        f"Warning: orphaned backup found at {backup_path} — a previous run may have "
        "exited uncleanly. Overwriting with fresh backup. If you want to restore from "
        "the previous run, copy it manually before continuing.",
        file=sys.stderr
    )
shutil.copy(target_path, backup_path)
```

**Notes:**
- The warning fires to stderr before the overwrite, giving a human operator watching output
  a brief window to `Ctrl+C`.
- For unattended automation, a non-interactive warning (not a `y/n` prompt) is correct — a
  blocking prompt would break `--iterations N` runs.

---

## eval_runner.py Programmatic Interface

`eval_runner.py` supports two calling conventions:

**Interactive (human operator):**
```bash
python eval_runner.py --skill path/to/SKILL.md --desc "My hypothesis"
```
Outputs human-readable score report with KEEP/DISCARD/BASELINE status.

**Programmatic (optimizer loop):**
```bash
python eval_runner.py --target path/to/SKILL.md --json
```
`--target` is an alias for `--skill`. `--json` suppresses the human-readable output and prints:
```json
{"quality_score": 0.8500}
```
The optimizer's `run_eval()` function parses `quality_score` (or `score` as a fallback).
