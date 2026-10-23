---
description: Universal dependency management rules for Python and agent services.
globs: ["requirements*.txt", "requirements*.in", "Dockerfile", "pyproject.toml", "apm.yml", "apm.lock.yaml"]
---

## 🐍 Python Dependency Rules (Summary)

**Full workflow details → the `dependency-management` skill**

### Non-Negotiables
1. **No manual `pip install`** — all changes go through `.in` → `pip-compile` → `.txt`.
2. **Commit `.in` + `.txt` together** — the `.in` is intent, the `.txt` is the lockfile.
3. **Service sovereignty** — every agent service owns its own `requirements.txt`.
4. **Tiered hierarchy** — Core (`requirements-core.in`) → Service-specific → Dev-only.
5. **Declarative Dockerfiles** — only `COPY requirements.txt` + `RUN pip install -r`. No ad-hoc installs.
6. **Hub-and-Spoke DRY** — one canonical script at the plugin root, listed in the copy manifest (`symlinks.json`, `strategy: "copy"`) for each skill that needs it; no committed duplicates, no new symlinks (plugin architecture policy Section 5).
7. **Build-Time Copies** — the APM build pipeline creates the per-skill copies and packs the bundle APM installs; installed skills must be fully self-contained.
8. **Agent Orchestration** — cross-plugin coordination uses skill delegation via the prompt loop, not direct script execution.

## 📦 Agent Package Dependencies (APM)

9. **`apm.yml` + `apm.lock.yaml` are a pair** — `apm.yml` is intent, `apm.lock.yaml` is the lockfile; commit them together, like `.in` + `.txt`. Never edit the lockfile by hand.
10. **Pinned refs only** — every APM dependency pins `#<tag>` or `#<commit-sha>`; update deliberately with `apm outdated` / `apm update`, never floating refs.
11. **Reproducible CI** — CI installs with `apm install --frozen`, which refuses when the lockfile and `apm.yml` disagree.
12. **The APM CLI is a pinned dev dependency** — `apm-cli==<version>` in `plugins/agent-scaffolders/requirements-dev.in`, compiled with `pip-compile`; upgrade it only after re-verifying APM behaviour.
13. **Skill Python dependencies are not installed by APM** — a skill with third-party imports keeps its own requirements file inside the skill (or documents the install step); plugin-root `requirements.txt` files are not deployed with skills.
