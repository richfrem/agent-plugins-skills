---
name: create-plugin
description: >
  This skill should be used when the user asks to "create a plugin", "scaffold a plugin",
  "build a new plugin", "set up plugin structure", "initialize a plugin", "make a Claude
  Code plugin", "organize plugin components", "set up plugin.json", or asks how to
  structure a plugin with commands, agents, skills, hooks, or MCP servers. Use this skill
  whenever someone wants to build a new plugin from scratch -- even if they just say
  "I want to build something for Claude Code." Do NOT use this for creating individual
  components in isolation (use create-skill, create-command, create-hook, create-sub-agent,
  or create-mcp-integration for those).
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

# Agent Plugin Architect

A plugin is a directory that bundles commands, agents, skills, hooks, and MCP servers
into a portable, auto-discovered package. Think of it as a "product" for Claude Code --
self-contained, distributable, and instantly usable when installed.

> Reference files:
> - `references/hitl-interaction-design.md` -- interaction design patterns for components
> - `references/pattern-decision-matrix.md` -- L4 pattern selection guide

---

## Plugin Structure at a Glance

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED: manifest (must be in .claude-plugin/, not root)
├── commands/                # Slash commands (.md files) -- auto-discovered
├── agents/                  # Sub-agent definitions (.md files) -- auto-discovered
├── skills/                  # Agent skills (one subdirectory per skill) -- auto-discovered
│   └── skill-name/
│       └── SKILL.md
├── hooks/
│   └── hooks.json           # Event handler configuration
├── .mcp.json                # MCP server definitions
├── .lsp.json                # LSP server configurations
├── settings.json            # Default settings (e.g., default agent)
├── scripts/                 # Shared utilities and helpers
└── README.md
```

**Critical rules:**
- `plugin.json` lives in `.claude-plugin/` -- NOT in the root
- Component dirs (`commands/`, `agents/`, `skills/`, `hooks/`) live at the ROOT, not inside `.claude-plugin/`
- Only create directories for components the plugin actually uses
- All names use kebab-case

---

## Phase 1: Discover the Plugin Purpose

Ask the user (or infer from context):

1. **What problem does this plugin solve?** Who uses it and when?
2. **What type of plugin?**
   - **Standalone** -- works entirely without external tools
   - **Supercharged** -- standalone + optional MCP integrations
   - **Integration-Dependent** -- requires MCP tools to function
3. **Is there a similar plugin to reference?**

Summarize understanding and confirm before proceeding.

---

## Phase 2: Plan Components

Determine which components are needed. Present as a table:

| Component | Count | Purpose |
|-----------|-------|---------|
| Skills | ? | Specialized knowledge/guidance |
| Commands | ? | User-initiated slash commands |
| Agents | ? | Autonomous sub-agents |
| Hooks | ? | Event-driven automation |
| MCP | ? | External service integration |
| Settings | ? | Per-project configuration |

**Load the relevant skill before implementing each type:**
- Skills -> `create-skill`
- Commands -> `create-command`
- Agents -> `create-sub-agent`
- Hooks -> `create-hook`
- MCP -> `create-mcp-integration`

Get user confirmation before moving to implementation.

---

## Phase 3: Ask Clarifying Questions

**DO NOT SKIP THIS PHASE.** For each component, identify underspecified aspects:

- **Skills**: What triggers them? What knowledge? Lean body target (1,500-2,000 words)?
- **Commands**: What arguments? Which tools? Interactive or automated?
- **Agents**: Proactive or reactive? Which tools? Output format?
- **Hooks**: Which events? prompt or command type? Validation criteria?
- **MCP**: Server type (stdio/SSE)? Auth? Which tools?
- **Settings**: What fields? Required vs optional? Defaults?

Present all questions grouped by component. Wait for answers before implementing.

---

## Phase 4: Scaffold Structure

```bash
# Create plugin structure
PLUGIN="plugin-name"
mkdir -p "$PLUGIN/.claude-plugin"
mkdir -p "$PLUGIN/skills"     # if needed
mkdir -p "$PLUGIN/commands"   # if needed
mkdir -p "$PLUGIN/agents"     # if needed
mkdir -p "$PLUGIN/hooks"      # if needed
mkdir -p "$PLUGIN/scripts"    # for shared utilities
```

**Create `plugin.json` manifest:**
```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Brief explanation of plugin purpose",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "homepage": "https://docs.example.com",
  "repository": "https://github.com/user/plugin-name",
  "license": "MIT",
  "keywords": ["tag1", "tag2"]
}
```

Only `name` is truly required. `name` must be kebab-case. Version follows semver.

**Custom path overrides** (supplements auto-discovery, does not replace it):
```json
{
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json",
  "lspServers": "./.lsp.json"
}
```

**If plugin has MCP integrations, create `../../CONNECTORS.md`:**
```markdown
# Connectors

| Category | Examples | Used By |
|----------|----------|---------|
| ~~crm | Salesforce, HubSpot | outreach-skill |
| ~~source-control | GitHub, GitLab | pr-review-agent |
```
Use `~~category` abstraction for portability across tool vendors.

**Add to `.gitignore`:**
```gitignore
.claude/*.local.md
.claude/*.local.json
```

**Resource sharing between skills and commands/agents (ADR-003):**

When a plugin has BOTH skills AND commands/agents that reference the same scripts,
assets, or references, follow this pattern so `npx skills add` works correctly:

1. **If the plugin has only skills (no `commands/` or `agents/` files):** scripts, assets, and
   references can live directly inside the skill directory. No symlinks needed.

2. **If the plugin also has `commands/` or `agents/` files that reference the same scripts/assets:**
   Those shared resources must live at the **plugin root** (e.g., `plugin-name/scripts/`), with
   real mirrored directories inside each skill containing **file-level symlinks** pointing up to the
   plugin root. `npx` resolves file-level symlinks at install time (copies real content). Directory-level
   symlinks are silently dropped -- never use them.

   ```
   plugin-name/
   ├── scripts/
   │   └── process.py          <- canonical source (real file at plugin root)
   ├── commands/my-command.md   <- references .agents/skills/<name>/scripts/process.py
   └── skills/my-skill/
       └── scripts/
           └── process.py      -> ../../../scripts/process.py  (file-level symlink)
   ```

   Create the symlink:
   ```bash
   mkdir -p skills/my-skill/scripts
   ln -s ../../../scripts/process.py skills/my-skill/scripts/process.py
   ```

3. **Script path references in SKILL.md and command/agent files must always use the installed
   root-relative path:**
   ```bash
   # CORRECT -- works when agent runs from project root after npx skills add
   python3 .agents/skills/my-skill/scripts/process.py

   # WRONG -- breaks from project root
   python3 ./process.py
   python3 ./../scripts/process.py
   ```

See `ADRs/003_plugin_skill_resource_sharing_via_mirrored_folder_structure_and_file_level_symlinks.md`
for the full decision record.

---

## Phase 5: Implement Components

Use the appropriate scaffolder for each component type. Apply these cross-cutting standards:

**Skills (use create-skill):**
- Third-person description with trigger phrases + anti-undertrigger nudge
- Body in imperative form, 1,500-2,000 words (lean)
- Resources first: `references/`, `examples/`, `scripts/`, then `SKILL.md`

**Commands (use create-command):**
- Body written as instructions FOR Claude, not to the user
- `description` under 60 chars, `argument-hint` documents all args
- `allowed-tools` restricted to minimum needed
- Use `${CLAUDE_PLUGIN_ROOT}` for scripts/binaries bundled with the plugin (read-only in update)
- Use `${CLAUDE_PLUGIN_DATA}` for persistent state (e.g., `node_modules`, python venv) that survives updates

**Agents (use create-sub-agent):**
- 3+ `<example>` blocks in description (Context/user/assistant format)
- System prompt 500-3,000 chars, second-person, concrete steps
- Tool least-privilege: only what the agent actually needs

**Hooks (use create-hook):**
- Prefer prompt-based hooks for complex logic
- Always use `${CLAUDE_PLUGIN_ROOT}` for script paths
- Validate with `validate-hook-schema.sh` and `test-hook.sh`

**Settings (`.claude/plugin-name.local.md` pattern):**
- YAML frontmatter for structured config, markdown body for prompts/notes
- Always add `.claude/*.local.md` to `.gitignore` -- never commit
- Use quick-exit pattern in hooks: `if [ ! -f "$STATE_FILE" ]; then exit 0; fi`
- Parse frontmatter with: `sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE"`
- Document restart requirement: settings changes need Claude Code restart
- **Plugin settings.json**: Use at plugin root to set defaults (e.g., `{"agent": "default-agent"}`)

---

## Phase 6: Validate Plugin

**Run plugin-validator agent** (triggers automatically when asked):
```
"Validate my plugin before I publish it"
```

Validator checks: manifest JSON, name format, component structure, naming conventions,
agent `<example>` blocks, skill frontmatter, hook JSON schema, MCP config, security
(no hardcoded credentials, HTTPS for MCP servers).

**Also validate per component type:**
```bash
# Agents
bash scripts/validate-agent.sh agents/my-agent.md

# Hooks
bash scripts/validate-hook-schema.sh hooks/hooks.json
bash scripts/test-hook.sh --hook hooks/validate.sh --event PreToolUse \
  --input '{"tool_name": "Write", "tool_input": {"file_path": "src/app.py"}}'
```

Fix all critical issues. Address warnings that indicate real problems.

---

## Phase 7: Test and Verify

**Install locally:**
```bash
cc --plugin-dir /path/to/plugin-name
```

**Verification checklist:**
- [ ] Skills load when triggered (ask questions matching trigger phrases)
- [ ] Commands appear in `/help` and execute with correct arguments
- [ ] Agents trigger on appropriate scenarios
- [ ] Hooks activate on events -- test with `claude --debug`
- [ ] MCP servers connect -- check with `/mcp`
- [ ] Settings files parse correctly

---

## Phase 8: Document and Distribute

**README minimum structure:**
- Overview and purpose
- Features list (components included)
- Installation instructions
- Prerequisites (required tools, env vars)
- Usage for each command/agent
- Configuration template (if settings used)
- Contribution/publishing notes

**Security standards (non-negotiable):**
- No hardcoded credentials in any file
- MCP servers use HTTPS/WSS not HTTP/WS
- Hook scripts quote all bash variables
- No secrets in example files or README

---

## Next Actions
- **Add components**: Run `create-skill`, `create-command`, `create-hook` to add functionality
- **Add tools**: Run `create-mcp-integration` to add tool connectors
- **Validate**: Trigger `audit-plugin` or `plugin-validator` agent for full compliance check
- **Iterate**: Use eval loop to optimize skill trigger descriptions
