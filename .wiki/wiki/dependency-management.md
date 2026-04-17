---
concept: dependency-management
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/dependency-management_dependency-management.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.320333+00:00
cluster: file
content_hash: d0b789d05f0cc035
---

# Dependency Management

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: dependency-management
description: >
  Python dependency and environment management for multi-service or monorepo python backends.
  Use when: (1) adding, upgrading, or removing a Python package, (2) responding to Dependabot
  or security vulnerability alerts (GHSA/CVE), (3) creating a new service that needs its
  own requirements files, (4) debugging pip install failures or Docker build issues related
  to dependencies, (5) reviewing or auditing the dependency tree, (6) running pip-compile.
  Enforces the pip-compile locked-file workflow and tiered dependency hierarchy.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Dependency Management

3. **One runtime per service.** Each isolated service owns its own `./requirements.txt` lockfile.

## Plugin & Skill Script Architecture (Hub-and-Spoke)

1. **DRY in source - Hub-and-Spoke.** One canonical script file lives at `plugins/<plugin-name>/scripts/`. Skills that need it use a file-level symlink in their own `scripts/` directory pointing back to the root (`ln -s ../../../scripts/foo.py`).
2. **File-level symlinks only.** Never symlink entire directories. The Bridge Installer (`bridge_installer.py`) only resolves individual file-level symlinks. Directory-level symlinks are silently dropped by binary packaging tools.
3. **Self-contained at install.** The installer (`bridge_installer.py`) resolves all symlinks to physical copies when deploying to `.agents/`. This ensures every skill is independently runnable regardless of the source mono-repo's presence.
4. **Windows Compatibility.** The `plugin_installer.py` uses a 3-tier strategy for Windows:
   - **Symlink** (if Developer Mode is on)
   - **Junction** (fallback for directory-level logic, though file-level is preferred)
   - **Full Copy** (ultimate fallback)
   This resolution ensures the Hub-and-Spoke pattern works cross-platform.
5. **No Cross-Plugin Script Execution.** A skill should never execute `python ../../other-plugin/scripts/foo.py`. If a cross-plugin capability is needed, use **Agent Skill Delegation**: instruct the Agent to invoke the target skill via the conversation layer. In the mono-repo source, cross-plugin file-level symlinks are acceptable for shared logic that the installer will then resolve.

## Repository Layout (Example)

```
src/
├── requirements-core.in          # Tier 1: shared baseline (fastapi, pydantic…)
├── requirements-core.txt         # Lockfile for core
├── services/
│   ├── auth_service/
│   │   ├── requirements.in       # Tier 2: inherits core + auth deps
│   │   └── ./requirements.txt
│   ├── payments_service/
│   │   ├── requirements.in
│   │   └── ./requirements.txt
│   └── database_service/
│       ├── requirements.in
│       └── ./requirements.txt
```

## Tiered Hierarchy

| Tier | Scope | File | Examples |
|------|-------|------|----------|
| **1 – Core** | Shared by >80% of services | `requirements-core.in` | `fastapi`, `pydantic`, `httpx` |
| **2 – Specialized** | Service-specific heavyweights | `<service>/requirements.in` | `stripe`, `redis`, `asyncpg` |
| **3 – Dev tools** | Never in production containers | `requirements-dev.in` | `pytest`, `black`, `ruff` |

Each service `.in` file usually begins with `-r ../../requirements-core.in` to inherit the core dependencies.

## Workflow: Adding or Upgrading a Package

1. **Declare** — Add or update the version constraint in the correct `.in` file.
   - If the package is needed by most services → `requirements-core.in`
   - If only one service → that service's `.in`
   - Security floor pins use `>=` syntax: `cryptography>=46.0.5`

2. **Lock** — Compile the lockfile:
   ```bash
   # Core
   pip-compile src/requirements-co

*(content truncated)*

## See Also

- [[dependency-management-guide]]
- [[dependency-management-plugin]]
- [[python-dependency-management-guide]]
- [[dependency-management-policy-detailed-reference]]
- [[procedural-fallback-tree-dependency-management]]
- [[dependency-management-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/dependency-management_dependency-management.md`
- **Indexed:** 2026-04-17T06:42:10.320333+00:00
