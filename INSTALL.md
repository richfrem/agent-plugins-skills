# Repository Installation & Lifecycle — Central Authority

This document defines the authoritative installation, retention, and lifecycle management methods for all plugins and skills in the Universal Agent Plugins & Skills repository.

---

## Consumer Installation & Management

These commands are for consumers who want to add and manage plugins seamlessly in any project repository. Installed artifacts are deployed directly into `.agents/` and registered in `plugin-sources.json` and `plugin-retention.json`.

### 1. Install Plugins (`plugin-add`)

Use [uvx](https://docs.astral.sh/uv/) for instant, isolated, cross-platform installation:

```bash
# Interactive TUI: select plugins and optionally toggle specific skills
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Install everything non-interactively (all plugins, all skills)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y

# Install a specific plugin non-interactively (e.g. agent-orchestration/)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills/plugins/agent-orchestration -y

# Dry-run preview
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --dry-run
```

---

### 2. Prune Unneeded Skills (`plugin-prune`)

Reduce model context size and eliminate token bloat by retaining only the exact skills, rules, and agents you need:

```bash
# Interactive TUI: review installed plugins and untoggle unneeded skills/rules/agents
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-prune --interactive

# Headless execution against plugin-retention.json
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-prune --execute --confirm-token PRUNE-INSTALLED-SKILLS

# Dry-run inspection
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-prune --dry-run
```

---

### 3. Uninstall Plugins (`plugin-remove`)

Safely remove installed plugins and scrub their artifacts from `.agents/`, `.claude/`, `.gemini/`, etc.:

```bash
# Interactive uninstaller TUI
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove

# Headless: remove a specific plugin
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove --plugins agent-orchestration/ --yes

# Headless: remove all tracked plugins
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove --all --yes
```

---

### 4. Sync Environment (`plugin-sync`)

Re-synchronize all declared plugins from `plugin-sources.json` and enforce your retention settings from `plugin-retention.json`:

```bash
# Full sync: reinstalls tracked plugins and runs post-sync retention pruning
python3 plugins/plugin-manager/scripts/sync_with_inventory.py

# Dry-run sync inspection
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --dry-run

# Sync without pruning
python3 plugins/plugin-manager/scripts/sync_with_inventory.py --no-prune
```

---

## Alternative: Native Marketplace (Claude Code / Copilot CLI)

If using **Claude Code** or **Copilot CLI**, you can add this repository as a native marketplace:

### Claude Code Syntax
```text
/plugin marketplace add richfrem/agent-plugins-skills
/plugin
/plugin install <plugin-name>
```

### Copilot CLI Syntax
```bash
copilot plugin marketplace add richfrem/agent-plugins-skills
copilot plugin
copilot plugin install <plugin-name>@richfrem-agent-plugins-skills
```

---

## Local Development (Contributors & Testing)

From a local clone of this repository:

```bash
# Install from local directory
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/<plugin-name> -y
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ --all -y

# Interactive pruner
python3 plugins/plugin-manager/scripts/prune_installed_skills.py --interactive

# Interactive remover
python3 plugins/plugin-manager/scripts/plugin_remove.py

# Sync inventory
python3 plugins/plugin-manager/scripts/sync_with_inventory.py
```

