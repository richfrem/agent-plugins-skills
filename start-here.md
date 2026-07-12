# Coding Policy Alignment Audit & Fix - Session Guide

## PURPOSE

**Ensure ALL code in the repository aligns with established coding conventions and policies.**

Every script must comply with:
- **coding-conventions.md** - Documentation standards (module/function docstrings, headers)
- **self-evolution-policy.md** - Code quality standards
- **plugin-architecture-policy.md** - Architecture rules
- **test-driven-development.md** - Testing standards

**Secondary Benefit:** When all code aligns with policy, fresh agent sessions can understand what scripts do without running them or reading full implementations — every script's top 20 lines answer "what does this do, what does it need, what does it output, what are its key functions."

---

## Overview

**Audit Type:** Codebase-wide compliance with established coding policies
**Policy Authority:** `.agent/rules/coding-conventions.md`
**Auditor Tool:** `plugins/dev-utils/scripts/workspace_conventions_auditor.py` (AST-based Python auditor + regex JS/TS header checker)
**Branch:** `feat/updated-coding-conventions.md`
**GitHub:** https://github.com/richfrem/agent-plugins-skills/tree/feat/updated-coding-conventions.md
**Strategy:** Fix plugin-by-plugin, smallest-violation-count first. Commit + push after every file. PR + merge to main once all plugins reach 0 violations.

**Current violation count: 246** (down from 454 at start).

### Plugins completed (0 violations) ✅
- `plugin-manager`
- root (`bootstrap.py`, `__init__.py`)
- `agent-loops`
- `exploration-cycle-plugin`
- `dev-utils`
- `cli-agents`
- `obsidian-wiki-engine`

### Plugins remaining, smallest first
| Plugin | Violations |
|---|---|
| `agent-agentic-os` | 39 |
| `agent-memory` | 86 |
| `agent-scaffolders` | 121 |

Re-run the auditor before trusting these numbers — they were last confirmed at commit `d5cbff72`.

---

## What Counts as a Violation

The auditor flags, per file:
1. **Missing module docstring** — must have `Purpose:` + (`Key Input Dependencies:` or `Input Files:`) sections at minimum.
2. **Missing function docstring** — every function/method needs a one-line summary.
3. **Function exceeds 50 lines** — needs refactoring (extract helper functions), not just documentation.

Symlinked copies of a canonical file (e.g. under `plugins/<plugin>/skills/<skill>/scripts/`) show up as separate report entries but are fixed automatically once the canonical source file is fixed — **never edit a symlink target directly, always edit the canonical file** in `plugins/<plugin>/scripts/`.

---

## Two Kinds of Fixes — Both Are Now In Scope

Earlier sessions treated this as docs-only work. **That constraint has been lifted.** Fixing the 50-line function-length violations is now expected, with a stricter verification bar than doc-only changes:

### A. Docs-only (docstrings/headers) — low risk
- Add missing module docstring sections and/or function docstrings.
- Zero logic changes.
- Verify with: `py_compile` + re-run auditor to confirm the violation cleared.

### B. Refactor (functions >50 lines) — requires behavioral verification
- Extract nested logic into module-level (or class-level, for methods) helper functions.
- Preserve behavior byte-for-byte — same inputs must produce the same outputs, same side effects, same error paths.
- **Never weaken or delete the 50-line rule itself** — it stays policy; track any deferred refactor as backlog, don't argue the rule away.
- Verification bar for every refactor, **in this order, before committing**:
  1. `python3 -m py_compile <file>` — syntax check.
  2. Re-run the auditor — confirm the specific violation is gone: `python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py > /dev/null 2>&1 && grep -A 8 "### 📄 '<file>'" temp/workspace_conventions_report.md` (no output = clean).
  3. **Real behavioral test** — in priority order:
     - If a pytest suite already covers the file, run it (`python3 -m pytest <test_file> -v`) and confirm pass counts match pre-refactor.
     - Otherwise, write a live smoke test in an isolated `/tmp` sandbox: fake CLI binaries via `PATH` injection, a scratch directory standing in for the real vault/wiki-root/vault-path, fake subprocess targets — exercise both the success path AND at least one error path, and diff the output against what the pre-refactor code would have produced.
     - For files that touch **real system state** (installers, daemons, global config, `~/.claude/...`), do NOT run them live against the real system. Test only the pure/isolated helper functions directly, or use a fully sandboxed fake `$HOME`/`$TMPDIR`. See the "Critical Incident" note below for why.
  4. Only after all three pass: `git add <file> && git commit -m "..." && git push origin feat/updated-coding-conventions.md`.

**Commit message convention:** one commit per file, message states what was extracted and exactly what was verified (test suite pass counts, or the specific sandbox scenario exercised). Trailer: `Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>` (or whichever model did the work).

---

## ⚠️ Critical Incident — Read Before Touching System-Level Scripts

During the `cli-agents` plugin pass, a "quick background test" of `enable_global_routing.py` was run without full sandboxing. It ran far enough before being killed to: sync a real script into `~/.claude/proxy/`, rewrite the real macOS launchd plist, and spawn a duplicate long-running process alongside the user's pre-existing instance. It was resolved safely (confirmed no data loss, killed only the duplicate, restored to pre-incident state) but it was avoidable.

**Rule going forward:** any script that can install daemons/services, edit shell profiles (`~/.zshrc`, `~/.bashrc`), write to real user config directories, or spawn long-running background processes must be tested **only** via its pure/isolated helper functions called directly in-process, or against a fully faked `$HOME` pointed at a `/tmp` sandbox. Never run the real `main()`/entry point of such a script live, even backgrounded, even "just to check."

---

## Standard Workflow For a Fresh Session

1. **Read this file in full.**
2. Re-run the auditor to get current ground truth (numbers above may be stale):
   ```bash
   python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py > /tmp/audit.log 2>&1
   grep -c "^### 📄" temp/workspace_conventions_report.md
   grep "^### 📄" temp/workspace_conventions_report.md | sed -E "s|^### 📄 'plugins/([^/]+)/.*|\1|" | sort | uniq -c | sort -rn
   ```
3. Confirm branch state:
   ```bash
   git status
   git log --oneline -5
   git log origin/feat/updated-coding-conventions.md --oneline -1   # confirm pushed
   ```
4. Pick the **smallest-violation-count plugin remaining** (see table above, or the fresh auditor output — trust the fresh run over this file).
5. Within that plugin, list its canonical (non-symlink) files with violations, smallest fix first:
   ```bash
   grep -A 10 "^### 📄 'plugins/<plugin-name>" temp/workspace_conventions_report.md | grep -v Symlink
   ```
6. Fix one file at a time using the "Two Kinds of Fixes" rules above. Commit + push after each file — do not batch multiple files into one commit.
7. When the whole plugin reaches 0 violations, re-run the auditor plugin-wide to confirm, then move to the next-smallest plugin.
8. If you find a pre-existing bug unrelated to the current fix's scope (dead code, wrong variable use, hardcoded path that should be `sys.executable`, etc.) — **do not silently fix it**. Flag it in the commit message or ask the user via `AskUserQuestion` whether to fix it now or leave it for later.
9. Update the "Plugins completed" / "Plugins remaining" tables in this file before ending the session.

---

## Applicable Skills & Rules

**Primary Skill:**
- `dev-utils:coding-conventions-agent` — `plugins/dev-utils/skills/coding-conventions-agent/SKILL.md`
- Auditor: `plugins/dev-utils/scripts/workspace_conventions_auditor.py`

**Governing rule files:**
- `.agent/rules/coding-conventions.md` — module/function docstring format, 50-line function limit, naming conventions
- `.agent/rules/self-evolution-policy.md` — failure tiers, deletion prohibition (never delete without explicit permission)
- `.agent/rules/plugin-architecture-policy.md` — plugin structure, hub-and-spoke scripts
- `.agent/rules/test-driven-development.md` — testing standards
- `.agent/rules/symlink-cross-platform.md` — if a fix touches a shared/symlinked script, use `symlink_manager.py`, never raw `ln -s`

---

## Useful Commands

```bash
# Full re-audit
python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py

# Violation count by plugin
grep "^### 📄" temp/workspace_conventions_report.md | sed -E "s|^### 📄 'plugins/([^/]+)/.*|\1|" | sort | uniq -c | sort -rn

# Violations for one file
grep -A 8 "### 📄 'plugins/<plugin>/scripts/<file>.py'" temp/workspace_conventions_report.md

# Canonical (non-symlink) files with violations in one plugin
grep -A 10 "^### 📄 'plugins/<plugin>" temp/workspace_conventions_report.md | grep -v Symlink

# Compile-check after an edit
python3 -m py_compile <path-to-file>

# Confirm a specific file is now clean
python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py > /dev/null 2>&1 && \
  grep -A 8 "### 📄 '<path-to-file>'" temp/workspace_conventions_report.md || echo "NO VIOLATIONS"

# Commit + push pattern (one file per commit)
git add <file>
git commit -m "refactor: break up <function>() (<N> lines) in <file> ..."
git push origin feat/updated-coding-conventions.md
```

---

## Session Cleanup Checklist

Before ending a session:
- [ ] Re-run the auditor, confirm the new total violation count
- [ ] Confirm `git log origin/feat/updated-coding-conventions.md --oneline -1` matches local `HEAD` (everything pushed, nothing local-only)
- [ ] Update the "Plugins completed" / "Plugins remaining" tables in this file with current numbers
- [ ] Note which plugin/file to resume with next
- [ ] Flag (don't fix) any pre-existing bugs discovered outside the current fix's scope

---

## Last Updated

**Status:** `obsidian-wiki-engine` completed at commit `d5cbff72`. 246 violations remaining across `agent-agentic-os` (39), `agent-memory` (86), `agent-scaffolders` (121). Next up: `agent-agentic-os`.
