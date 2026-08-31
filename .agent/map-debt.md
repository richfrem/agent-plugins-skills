# Map Debt Registry

This registry tracks technical debt, process friction, and workarounds.
Entries must be resolved, aged, or escalated. 
Do not delete resolved items; set `Status: RESOLVED` to maintain history.

---

## 2026-07-25 — Backlog review & GitHub issue lifecycle smoke test session

- **Artifact:** `plugins/dev-utils/skills/github-issue-agent/scripts/gh_issue_create.py`
  **Friction:** Live issue creation raised an unhandled subprocess traceback the first time a taxonomy label (`type:*`, `tier:*`, etc.) didn't already exist in the repo — `gh issue create --label X` fails hard on unregistered labels.
  **Why not deferred:** Small, in-bounds fix.
  **Fix:** Added `_ensure_labels_exist()` — auto-creates missing labels before live creation. Regression test added.
  **Evidence:** Reproduced live filing issue #460; traceback captured in session transcript.
  **Severity:** M | **Repeat:** YES (same class hit gh_issue_prioritize.py below) | **Status:** RESOLVED

- **Artifact:** `plugins/dev-utils/scripts/gh_issue_prioritize.py` (`extract_friction_tier`)
  **Friction:** Only parsed bare `tier:N` labels via `int(name.split(":")[1])`. This repo's real taxonomy format (`tier:2-structural`, `tier:3-architecture`) raised `ValueError`, silently caught, defaulting every real issue to tier 0 / priority P3 — the prioritizer silently mis-scored 100% of real issues.
  **Why not deferred:** Small, in-bounds fix.
  **Fix:** Reads the leading digit run instead of the whole segment after the colon.
  **Evidence:** Live test against issues #460/#461/#462 — all scored P3/tier-0 before fix, correct P1/P0/tier-2/tier-3 after.
  **Severity:** M | **Repeat:** YES | **Status:** RESOLVED

- **Artifact:** `plugins/agent-scaffolders/scripts/update_ecosystem_index.py` (`count_ecosystem`)
  **Friction:** Counted every directory under `plugins/` as a "plugin" via bare `is_dir()`, with no check for `plugin.yaml`. Inflated README's plugin count by 2 — counted `plugins/__pycache__` (build artifact) and `plugins/spec-kitty-plugin` (deprecated, no `plugin.yaml`) as active plugins.
  **Why not deferred:** Small, in-bounds fix.
  **Fix:** Added `(plugin_path / "plugin.yaml").exists()` check to the iteration filter.
  **Evidence:** README showed 11→12 plugins pre-fix; corrected to 10 (matches CLAUDE.md canonical count) post-fix.
  **Severity:** S | **Repeat:** YES (third instance of the same underlying pattern — see note below) | **Status:** RESOLVED

- **Artifact:** `README.md`, `INSTALL.md`, `plugins/exploration-cycle-plugin/agents/intake-agent.md`
  **Friction:** Stale skill/plugin counts (INSTALL.md said "120 skills / 29 plugins", actual 128/10), a nonexistent CLI flag documented (`plugin_add.py --plugin <name>` — real flag is `--plugins` plural or positional path), and a stale routing reference to the deprecated spec-kitty engineering cycle in the OS's own front-door intake interviewer.
  **Why not deferred:** Small, docs-only fixes.
  **Fix:** Corrected counts, corrected CLI flag usage, repointed intake-agent's spec destination to Superpowers.
  **Evidence:** `plugin_add.py --help` output; live plugin/skill counts via `find`.
  **Severity:** S | **Repeat:** N/A (documentation, not code) | **Status:** RESOLVED

**Pattern across all four:** every one of these is a script or doc that hard-assumed a repo-defined convention (label taxonomy format, plugin directory structure, CLI flag surface, plugin routing state) without validating against the *live* convention source, and drifted silently until manually caught. See `test-driven-development.md` — "Prefer Replay Fixtures Over Synthetic Mocks" addendum on convention-file drift.

- **Artifact:** `plugins/dev-utils/skills/context-bundler/assets/templates/*.md` (7 files), `plugins/dev-utils/skills/github-issue-agent/scripts/*.py` (8 files), `plugins/dev-utils/skills/github-issue-backlog-agent/scripts/task_to_issue_bridge.py`
  **Friction:** All 16 files were real files living inside their skill directory instead of canonical files in the plugin root with a `symlink_manager.py`-registered symlink (ADR-002/003 hub-and-spoke). `audit.py` (compliance) passed clean; only `audit_plugin_structure.py` (structural) caught it, and only because it was run manually — nothing in the skill-creation path runs it automatically.
  **Why not deferred:** Small, mechanical, in-bounds fix.
  **Fix:** Moved all 16 to `plugins/dev-utils/{scripts,assets/templates}/`, added `symlinks.json` entries, ran `symlink_manager.py restore`. 41/41 tests still pass post-move. Added Rule 12 to `self-evolution-policy.md` requiring new skill files to land in the plugin root first, and `audit_plugin_structure.py` to run before any new skill/script is considered complete.
  **Evidence:** `audit_plugin_structure.py plugins/dev-utils` — 16 errors → 0 errors post-fix.
  **Severity:** M | **Repeat:** YES (structural pattern, not a one-off — will recur for any skill scaffolded without running the structural audit) | **Status:** RESOLVED

- **Artifact:** `plugins/cli-agents/skills/update-cli-models/` (pre-existing, not introduced this session)
  **Friction:** Missing `references/acceptance-criteria.md` — flagged by `audit.py` during the compliance pass run after scaffolding `agent-file-synchronization`.
  **Why not fixed now:** Resolved via symlink to `plugins/cli-agents/references/acceptance-criteria.md`.
  **Evidence:** `audit.py --path plugins/cli-agents` — passes clean.
  **Severity:** S | **Repeat:** NO | **Status:** RESOLVED

---

## 2026-08-24 — Marketplace Manifest Schema & Scaffolding/Auditing Hardening

- **Artifact:** `plugins/agent-scaffolders/skills/create-plugin/SKILL.md`, `scaffold.py`, `manage-marketplace/SKILL.md`, `audit.py`, `audit-plugin/SKILL.md`, `audit-plugin-l5/SKILL.md`, `l5-red-team-auditor/SKILL.md`, `plugins/plugin-manager/scripts/plugin_add.py`
  **Friction:** Claude Code `/plugin install` strictly requires `"author"` to be an object (`{"name": "...", "email": "..."}`) and fails on string author or duplicate manifest keys. Scaffolding templates and validators allowed string authors or lacked duplicate key checking.
  **Why not deferred:** In-bounds, high-impact fixes preventing production plugin installation failures across all consuming repositories.
  **Fix:** Updated `scaffold.py`, `create-plugin`, `manage-marketplace`, `audit.py`, `audit-plugin`, `audit-plugin-l5`, and `plugin_add.py` to enforce the author object schema and reject duplicate keys in `plugin.json`.
  **Evidence:** `audit.py` across all plugins, structural audits, and `plugin_add.py` validation passes.
  **Severity:** M | **Repeat:** NO | **Status:** RESOLVED

- **Artifact:** `plugins/agent-orchestration/skills/co-pilot-loop/references/acceptance-criteria.md`
  **Friction:** `audit_plugin_structure.py` detected a real file inside `skills/co-pilot-loop/references/` instead of a symlink to plugin root.
  **Why not deferred:** In-bounds structural rule compliance (ADR-002/ADR-003).
  **Fix:** Relocated canonical file to `plugins/agent-orchestration/references/acceptance-criteria.md` and created symlink via `symlink_manager.py`.
  **Evidence:** `audit_plugin_structure.py plugins/agent-orchestration` passes with 0 errors.
  **Severity:** S | **Repeat:** NO | **Status:** RESOLVED

---
