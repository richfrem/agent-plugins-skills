---
description: Universal dependency management rules for Python and agent services.
globs: ["requirements*.txt", "requirements*.in", "Dockerfile", "pyproject.toml"]
---

## 🐍 Python Dependency Rules (Summary)

**Full workflow details → `.agents/skills/dependency-management/SKILL.md` (installed locally via `bridge_installer.py`)**

### Non-Negotiables
1. **No manual `pip install`** — all changes go through `.in` → `pip-compile` → `.txt`.
2. **Commit `.in` + `.txt` together** — the `.in` is intent, the `.txt` is the lockfile.
3. **Service sovereignty** — every agent service owns its own `requirements.txt`.
4. **Tiered hierarchy** — Core (`requirements-core.in`) → Service-specific → Dev-only.
5. **Declarative Dockerfiles** — only `COPY requirements.txt` + `RUN pip install -r`. No ad-hoc installs.
6. **Hub-and-Spoke DRY** (ADR-002) — canonical scripts at plugin root; file-level symlinks in `skills/` subfolders (no duplication in monorepo source).
7. **Symlink Resolution** (ADR-003) — installer resolves symlinks to physical copies in `.agents/`; installed skills must be fully self-contained.
8. **Agent Orchestration** (ADR-001) — cross-plugin coordination uses skill delegation via the prompt loop, not direct script execution.
