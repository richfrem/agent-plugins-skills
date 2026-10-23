---
description: Universal dependency management rules for Python and agent services.
globs: ["requirements*.txt", "requirements*.in", "Dockerfile", "pyproject.toml", "apm.yml", "apm.lock.yaml"]
---

## 🐍 Python Dependency Rules (Summary)

### Non-Negotiables
1. **No manual `pip install`** — all changes go through `.in` → `pip-compile` → `.txt`.
2. **Commit `.in` + `.txt` together** — the `.in` is intent, the `.txt` is the lockfile.
3. **Service sovereignty** — every agent service owns its own `requirements.txt`.
4. **Tiered hierarchy** — Core (`requirements-core.in`) → Service-specific → Dev-only.
5. **Declarative Dockerfiles** — only `COPY requirements.txt` + `RUN pip install -r`. No ad-hoc installs.
6. **Security floors use `>=`** — pin advisory floors in `.in` files as `pkg>=X.Y.Z`, never `==`.
7. **CVE response** — raise the floor in the owning `.in` file, run `pip-compile` (core first, then services that `-r` it), rebuild and verify the affected container.
8. **Self-contained skills** — each script lives once, inside the skill that uses it; no plugin-root shared scripts, no copy manifest, no symlinks.
9. **Agent Orchestration** — cross-plugin coordination uses skill delegation via the prompt loop, not direct script execution.

## 📦 Agent Package Dependencies (APM)

10. **`apm.yml` + `apm.lock.yaml` are a pair** — `apm.yml` is intent, `apm.lock.yaml` is the lockfile; commit them together, like `.in` + `.txt`. Never edit the lockfile by hand.
11. **Pinned refs only** — every APM dependency pins `#<tag>` or `#<commit-sha>`; update deliberately with `apm outdated` / `apm update`, never floating refs.
12. **Reproducible CI** — CI installs with `apm install --frozen`, which refuses when the lockfile and `apm.yml` disagree.
13. **The APM CLI is a pinned dev dependency** — `apm-cli==<version>` in the `packaging-with-apm` skill's `requirements-dev.in` (the skill documents the install step), compiled with `pip-compile`; upgrade it only after re-verifying APM behaviour.
14. **Skill Python dependencies are not installed by APM** — a skill with third-party imports keeps its own requirements file inside the skill (or documents the install step); plugin-root `requirements.txt` files are not deployed with skills.
