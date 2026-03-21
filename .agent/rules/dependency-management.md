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
