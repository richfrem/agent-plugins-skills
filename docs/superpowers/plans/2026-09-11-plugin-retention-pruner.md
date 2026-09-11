# Component Retention Pruner & Progressive Disclosure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the `plugin-pruner` skill and deterministic pruning engine in `plugin-manager`, integrate retention lifecycle into `plugin_add.py` and `sync_with_inventory.py`, and refactor `plugin-manager` and `agent-scaffolders` skills to adhere to progressive disclosure and deterministic-first architecture.

**Architecture:** A unified manifest (`plugin-retention.json`) tracks installed components with an explicit boolean map (`"skills": { "<name>": true/false }`). `plugin_add.py` supports install-time granular toggles and seeds the manifest. `prune_installed_skills.py` provides dry-run, token confirmation, dependency advisory, and an interactive plugin-by-plugin TUI. `sync_with_inventory.py` enforces retention post-sync. Skills are refactored into ultra-lean routers ($\le 60$ lines) pointing conditionally to `references/`.

**Tech Stack:** Python 3.8+ (standard library: `argparse`, `json`, `pathlib`, `shutil`, `re`), ANSI terminal controls for TUI, pytest for unit/functional tests.

**Spec:** `docs/superpowers/specs/2026-09-11-plugin-retention-pruner-design.md`

## Global Constraints

- Monorepo source of truth is `plugins/`; `.agents/` is an installed deployment.
- ADR-001: No cross-plugin script execution.
- ADR-002: Multi-skill script sharing within a plugin via hub-and-spoke (`plugins/<plugin>/scripts/`).
- ADR-003: File-level symlinks only via `symlink_manager.py` and `symlinks.json`.
- Strict relative path execution inside `SKILL.md` (relative to skill root).
- Deterministic-first: scripts handle transformations, exit codes, and manifest sync; LLM handles judgment.
- Confirmation token: `--confirm-token PRUNE-INSTALLED-SKILLS` required for physical deletion.
- Preserves all 6 alignment invariants and self-healing `--fix` engine in `audit-skill`.

---

### Task 1: Retention Manifest Template & Data Model Helpers

**Files:**
- Create: `plugins/plugin-manager/assets/templates/plugin-retention.template.json`
- Create: `tests/plugin_manager/test_retention_manifest.py`
- Create: `plugins/plugin-manager/scripts/retention_manifest.py`

**Interfaces:**
- Produces:
  - `load_manifest(path: Path) -> dict`
  - `save_manifest(path: Path, data: dict) -> None`
  - `merge_installed_components(manifest: dict, plugin_name: str, artifacts: list[str]) -> dict`
  - `get_component_states(manifest: dict) -> tuple[dict[str, bool], dict[str, bool], dict[str, bool]]` (skills, rules, agents)

- [ ] **Step 1: Write the failing test for retention manifest helper**

```python
# tests/plugin_manager/test_retention_manifest.py
import json
from pathlib import Path
import pytest
from plugins.plugin_manager.scripts.retention_manifest import (
    load_manifest,
    save_manifest,
    merge_installed_components,
    get_component_states,
)

def test_load_and_merge_manifest(tmp_path: Path):
    template_path = tmp_path / "template.json"
    template_data = {
        "version": 1,
        "updated_at": "2026-09-11T00:00:00Z",
        "protected_defaults": ["plugin-installer", "plugin-remover", "plugin-syncer", "plugin-pruner"],
        "plugins": {}
    }
    template_path.write_text(json.dumps(template_data), encoding="utf-8")

    manifest = load_manifest(template_path)
    assert manifest["version"] == 1

    artifacts = [
        ".agents/skills/os-architect",
        ".agents/skills/evo-smoketest",
        ".agent/rules/self-evolution-policy.md",
        ".agents/agents/agent-agentic-os-os-architect-agent.md"
    ]
    updated = merge_installed_components(manifest, "agent-agentic-os", artifacts)
    assert "agent-agentic-os" in updated["plugins"]
    assert updated["plugins"]["agent-agentic-os"]["skills"]["os-architect"] is True
    assert updated["plugins"]["agent-agentic-os"]["skills"]["evo-smoketest"] is True
    assert updated["plugins"]["agent-agentic-os"]["rules"]["self-evolution-policy.md"] is True
    assert updated["plugins"]["agent-agentic-os"]["agents"]["agent-agentic-os-os-architect-agent.md"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/plugin_manager/test_retention_manifest.py -v`  
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement template and `retention_manifest.py`**

Create `plugins/plugin-manager/assets/templates/plugin-retention.template.json` with the canonical schema.  
Implement `plugins/plugin-manager/scripts/retention_manifest.py` to satisfy `load_manifest`, `save_manifest`, `merge_installed_components`, and `get_component_states`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/plugin_manager/test_retention_manifest.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/plugin-manager/assets/templates/plugin-retention.template.json plugins/plugin-manager/scripts/retention_manifest.py tests/plugin_manager/test_retention_manifest.py
git commit -m "feat(plugin-manager): add retention manifest template and data helpers"
```

---

### Task 2: Core Pruning & Dependency Scanner Engine

**Files:**
- Create: `plugins/plugin-manager/scripts/prune_installed_skills.py`
- Create: `tests/plugin_manager/test_prune_installed_skills.py`

**Interfaces:**
- Consumes: `retention_manifest.py`
- Produces:
  - CLI: `python3 prune_installed_skills.py [--manifest PATH] [--execute] [--confirm-token TOKEN] [--dry-run]`
  - Function: `scan_dependencies(skills_dir: Path, retained_skills: set[str]) -> dict[str, set[str]]`
  - Function: `plan_pruning(root: Path, manifest: dict) -> dict[str, list[Path]]` (removable files/dirs per component)
  - Function: `execute_pruning(removals: dict[str, list[Path]]) -> int`

- [ ] **Step 1: Write the failing tests for dependency scanning and pruning plan**

```python
# tests/plugin_manager/test_prune_installed_skills.py
import json
from pathlib import Path
import pytest
from plugins.plugin_manager.scripts.prune_installed_skills import (
    scan_dependencies,
    plan_pruning,
    CONFIRM_TOKEN,
)

def test_scan_dependencies(tmp_path: Path):
    skills_dir = tmp_path / ".agents" / "skills"
    skill_a = skills_dir / "skill-a"
    skill_a.mkdir(parents=True)
    (skill_a / "SKILL.md").write_text(
        "---\nname: skill-a\n---\nSee .agent/rules/test-rule.md and requires skill-b.",
        encoding="utf-8"
    )

    deps = scan_dependencies(skills_dir, {"skill-a"})
    assert "test-rule.md" in deps["rules"]
    assert "skill-b" in deps["skills"]

def test_plan_pruning_protects_defaults(tmp_path: Path):
    root = tmp_path
    skills_dir = root / ".agents" / "skills"
    skills_dir.mkdir(parents=True)
    (skills_dir / "plugin-installer").mkdir()
    (skills_dir / "unwanted-skill").mkdir()

    manifest = {
        "protected_defaults": ["plugin-installer"],
        "plugins": {
            "dummy": {
                "skills": {"plugin-installer": True, "unwanted-skill": False},
                "rules": {},
                "agents": {}
            }
        }
    }
    plan = plan_pruning(root, manifest)
    removable_names = [p.name for p in plan["skills"]]
    assert "unwanted-skill" in removable_names
    assert "plugin-installer" not in removable_names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/plugin_manager/test_prune_installed_skills.py -v`  
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `prune_installed_skills.py` core logic**

Implement `scan_dependencies`, `plan_pruning`, `execute_pruning`, and CLI argument handling with safety checks and dry-run reporting.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/plugin_manager/test_prune_installed_skills.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/plugin-manager/scripts/prune_installed_skills.py tests/plugin_manager/test_prune_installed_skills.py
git commit -m "feat(plugin-manager): implement core pruning script and dependency scanner"
```

---

### Task 3: Interactive Plugin-by-Plugin Multiselect TUI

**Files:**
- Modify: `plugins/plugin-manager/scripts/prune_installed_skills.py`
- Test: `tests/plugin_manager/test_prune_interactive_tui.py`

**Interfaces:**
- Consumes: `prune_installed_skills.py` CLI
- Produces:
  - `interactive_prune_tui(root: Path, manifest: dict) -> dict` (returns updated manifest)
  - CLI flag: `--interactive`

- [ ] **Step 1: Write test for interactive selection state transitions**

```python
# tests/plugin_manager/test_prune_interactive_tui.py
from plugins.plugin_manager.scripts.prune_installed_skills import toggle_component_state

def test_toggle_component_state():
    manifest = {
        "plugins": {
            "demo": {
                "skills": {"skill-1": True, "skill-2": False},
                "rules": {},
                "agents": {}
            }
        }
    }
    updated = toggle_component_state(manifest, "demo", "skills", "skill-1")
    assert updated["plugins"]["demo"]["skills"]["skill-1"] is False
    updated = toggle_component_state(manifest, "demo", "skills", "skill-2")
    assert updated["plugins"]["demo"]["skills"]["skill-2"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/plugin_manager/test_prune_interactive_tui.py -v`  
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement TUI and toggle logic in `prune_installed_skills.py`**

Integrate zero-dependency ANSI key reader (`_read_key`), cursor rendering, plugin-by-plugin paging, and dependency warnings into `prune_installed_skills.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/plugin_manager/test_prune_interactive_tui.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/plugin-manager/scripts/prune_installed_skills.py tests/plugin_manager/test_prune_interactive_tui.py
git commit -m "feat(plugin-manager): add interactive multiselect TUI to pruner"
```

---

### Task 4: Scaffold `plugin-pruner` Skill & Register Symlinks

**Files:**
- Create: `plugins/plugin-manager/skills/plugin-pruner/SKILL.md` (lean router $\le 50$ lines)
- Create: `plugins/plugin-manager/skills/plugin-pruner/evals/evals.json`
- Create: `plugins/plugin-manager/references/retention-workflow.md` (Mermaid diagram + workflow)
- Create: `plugins/plugin-manager/references/pruner-cli-guide.md`
- Modify: `symlinks.json`
- Modify: `plugins/plugin-manager/plugin.yaml`

**Interfaces:**
- Produces: `plugin-pruner` skill callable by agents and slash command `/plugin-pruner`.
- Symlinks:
  - `plugins/plugin-manager/scripts/prune_installed_skills.py` $\to$ `skills/plugin-pruner/scripts/prune_installed_skills.py`
  - `plugins/plugin-manager/assets/templates/plugin-retention.template.json` $\to$ `skills/plugin-pruner/assets/templates/plugin-retention.template.json`
  - `plugins/plugin-manager/references/retention-workflow.md` $\to$ `skills/plugin-pruner/references/retention-workflow.md`
  - `plugins/plugin-manager/references/pruner-cli-guide.md` $\to$ `skills/plugin-pruner/references/pruner-cli-guide.md`

- [ ] **Step 1: Write `SKILL.md` as a lean router**

Create `plugins/plugin-manager/skills/plugin-pruner/SKILL.md` ($\le 50$ lines) with clear triggers, progressive disclosure links to `references/`, and deterministic command instructions.

- [ ] **Step 2: Create evals and references**

Create `evals.json` with positive/negative routing test cases using `should_trigger: true/false`.  
Create `retention-workflow.md` featuring the Mermaid flowchart and `pruner-cli-guide.md`.

- [ ] **Step 3: Register symlinks and update `plugin.yaml`**

Add entries to `symlinks.json`.  
Run `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py restore`.  
Run `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose` to verify 0 broken/imposter symlinks.  
Update `plugins/plugin-manager/plugin.yaml` to list `plugin-pruner` in `skills` and `prune_installed_skills` in `provides_tools`.

- [ ] **Step 4: Verify with `audit_skill.py`**

Run: `python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-pruner`  
Expected: 100% PASS (all 6 invariants pass).

- [ ] **Step 5: Commit**

```bash
git add plugins/plugin-manager/ symlinks.json
git commit -m "feat(plugin-manager): scaffold plugin-pruner skill and wire symlinks"
```

---

### Task 5: Installer Seeding & Day 1 Granular Skill Selection

**Files:**
- Modify: `plugins/plugin-manager/scripts/plugin_add.py`
- Modify: `plugins/plugin-manager/scripts/plugin_installer.py`
- Create: `tests/plugin_manager/test_installer_retention.py`

**Interfaces:**
- Produces:
  - Interactive drill-down toggles in `plugin_add.py` when installing a plugin.
  - Automatic creation / merging of `plugin-retention.json` on install completion.

- [ ] **Step 1: Write tests for installer retention seeding**

```python
# tests/plugin_manager/test_installer_retention.py
from pathlib import Path
from plugins.plugin_manager.scripts.retention_manifest import load_manifest

def test_install_creates_or_updates_retention_json(tmp_path: Path):
    # Tests that when an install completes, plugin-retention.json records the installed components
    pass
```

- [ ] **Step 2: Run test to verify behavior**

Run: `pytest tests/plugin_manager/test_installer_retention.py -v`

- [ ] **Step 3: Update `plugin_add.py` and `plugin_installer.py`**

Add optional sub-skill checkboxes to `plugin_add.py` interactive multiselect.  
After copying artifacts and writing `.agents/ownership/<plugin>.json`, invoke `merge_installed_components` to seed or update `plugin-retention.json`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/plugin_manager/test_installer_retention.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/plugin-manager/scripts/plugin_add.py plugins/plugin-manager/scripts/plugin_installer.py tests/plugin_manager/test_installer_retention.py
git commit -m "feat(plugin-manager): add install-time skill selection and retention seeding"
```

---

### Task 6: Syncer Retention Enforcement

**Files:**
- Modify: `plugins/plugin-manager/scripts/sync_with_inventory.py`
- Create: `tests/plugin_manager/test_syncer_pruning.py`

**Interfaces:**
- Produces:
  - Automatic post-sync pruning pass if `plugin-retention.json` exists.
  - CLI flag `--no-prune` in `sync_with_inventory.py`.

- [ ] **Step 1: Write test for sync pruner execution**

```python
# tests/plugin_manager/test_syncer_pruning.py
def test_syncer_executes_prune_when_manifest_present(tmp_path: Path):
    pass
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/plugin_manager/test_syncer_pruning.py -v`

- [ ] **Step 3: Update `sync_with_inventory.py`**

Wire the post-sync step to invoke `prune_installed_skills.py --execute --confirm-token PRUNE-INSTALLED-SKILLS` unless `--no-prune` or `--cleanup-only` or `--dry-run` is passed.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/plugin_manager/test_syncer_pruning.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add plugins/plugin-manager/scripts/sync_with_inventory.py tests/plugin_manager/test_syncer_pruning.py
git commit -m "feat(plugin-manager): enforce retention manifest in sync_with_inventory"
```

---

### Task 7: Refactor `plugin-manager` Skills to Progressive Disclosure Routers

**Files:**
- Modify: `plugins/plugin-manager/skills/plugin-installer/SKILL.md`
- Create: `plugins/plugin-manager/references/installer-cli-guide.md`
- Modify: `plugins/plugin-manager/skills/plugin-remover/SKILL.md`
- Create: `plugins/plugin-manager/references/remover-cli-guide.md`
- Modify: `plugins/plugin-manager/skills/plugin-syncer/SKILL.md`
- Create: `plugins/plugin-manager/references/syncer-cli-guide.md`
- Modify: `symlinks.json`

**Interfaces:**
- Ensures all `SKILL.md` files in `plugin-manager` are $\le 50$ lines, cleanly separating routing from deep reference guides.

- [ ] **Step 1: Refactor each `SKILL.md` into an ultra-lean router**

Move deep CLI flag catalogs and manual uninstallation procedures into `references/*.md`.  
Keep `SKILL.md` under 50 lines with explicit progressive disclosure links.

- [ ] **Step 2: Wire references and update symlinks**

Symlink new reference guides into the corresponding skill `references/` directories via `symlinks.json` and `symlink_manager.py restore`.

- [ ] **Step 3: Run `audit_skill.py` on all 4 skills**

```bash
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-installer
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-remover
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-syncer
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/plugin-manager/skills/plugin-pruner
```
Expected: All 4 skills PASS with 100% compliance.

- [ ] **Step 4: Commit**

```bash
git add plugins/plugin-manager/ symlinks.json
git commit -m "refactor(plugin-manager): convert skills to progressive disclosure routers"
```

---

### Task 8: Refactor `agent-scaffolders` (`create-skill` & `audit-skill`)

**Files:**
- Modify: `plugins/agent-scaffolders/skills/create-skill/SKILL.md`
- Create: `plugins/agent-scaffolders/references/discovery-interview.md`
- Create: `plugins/agent-scaffolders/references/platform-primitives.md`
- Modify: `plugins/agent-scaffolders/scripts/create_skill.py` (ensure generated `SKILL.md` defaults to progressive disclosure)
- Modify: `plugins/agent-scaffolders/skills/audit-skill/SKILL.md`
- Modify: `plugins/agent-scaffolders/scripts/audit_skill.py` (add progressive disclosure line/structure audit)
- Create: `tests/agent_scaffolders/test_audit_skill_progressive.py`

**Interfaces:**
- `create-skill`: Lean router ($\le 60$ lines) that links to interview and platform references.
- `audit_skill.py`: Flags `SKILL.md` $> 80$ lines and verifies progressive disclosure links, while preserving all 6 invariants and `--fix`.

- [ ] **Step 1: Write test for progressive disclosure audit in `audit_skill.py`**

```python
# tests/agent_scaffolders/test_audit_skill_progressive.py
from pathlib import Path
from plugins.agent_scaffolders.scripts.audit_skill import audit_skill_directory

def test_audit_flags_bloated_skill_router(tmp_path: Path):
    skill_dir = tmp_path / "bloated-skill"
    skill_dir.mkdir()
    # Write a SKILL.md > 80 lines
    lines = ["---", "name: bloated-skill", "description: Tests bloat", "---"] + ["Line"] * 90
    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")
    report = audit_skill_directory(skill_dir)
    assert any("exceeds progressive disclosure budget" in w for w in report["warnings"])
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/agent_scaffolders/test_audit_skill_progressive.py -v`

- [ ] **Step 3: Implement progressive disclosure check in `audit_skill.py` and refactor `create-skill`**

Trim `create-skill/SKILL.md` to $\le 60$ lines; move discovery questions and platform notes to `references/`.  
Update template in `create_skill.py`.  
Enhance `audit_skill.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/agent_scaffolders/test_audit_skill_progressive.py -v`  
Expected: PASS

- [ ] **Step 5: Run self-audit on `create-skill` and `audit-skill`**

```bash
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/agent-scaffolders/skills/create-skill
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/agent-scaffolders/skills/audit-skill
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add plugins/agent-scaffolders/ tests/agent_scaffolders/ symlinks.json
git commit -m "refactor(agent-scaffolders): apply progressive disclosure and audit checks"
```

---

### Task 9: Ecosystem Audit, Reinstall & Verification Gate

**Files:**
- Verification only: runs existing audit suites and executes live deployment.

- [ ] **Step 1: Symlink Audit**

Run:
```bash
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
```
Expected: 0 broken symlinks, 0 imposter real files.

- [ ] **Step 2: Plugin Structure Audits**

Run:
```bash
python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/plugin-manager
python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/plugin-manager
python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/agent-scaffolders
python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/agent-scaffolders
```
Expected: All audits PASS.

- [ ] **Step 3: Reinstall plugins into `.agents/`**

Per plugin reinstall rule:
```bash
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/plugin-manager -y
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/agent-scaffolders -y
```
Verify `.agents/skills/plugin-pruner` exists and is functional.

- [ ] **Step 4: Final verification dry-run**

Run:
```bash
python3 plugins/plugin-manager/scripts/prune_installed_skills.py --dry-run
```
Expected: Clean exit code 0, displaying selected and removable component summary.
