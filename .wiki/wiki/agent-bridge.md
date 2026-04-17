---
concept: agent-bridge
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/plugin-installer/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.188601+00:00
cluster: plugin
content_hash: 91704c85fb9f7f9a
---

# Agent Bridge

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: plugin-installer
description: >-
  Installs plugin components (skills, commands/workflows, rules, hooks, MCP)
  into the .agents/ central store and symlinks them to agent environments that
  require it (.claude/). DEFAULT method: run plugin_add.py for an interactive
  TUI that supports local and GitHub owner/repo installs. Use plugin_installer.py
  for scripted/CI single-plugin installs. Trigger when a user says "install
  plugin", "deploy plugin", "add plugin", "install from GitHub", or "sync
  plugin to agents".
allowed-tools: Bash, Write, Read
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

# Agent Bridge

## Overview

This skill deploys plugin components to agent environments using the
`.agents/` central store + symlink pattern. It is the **full-stack** installer:

| Installer | Features | Requires Local Clone? | Recommended For |
|-----------|----------|-----------------------|-----------------|
| `uvx` ★ **default** | Full interactive TUI | No (runs from GitHub) | Everyone using `uv` |
| `bootstrap.py` | Full interactive TUI | No (downloads in-memory) | End users without `uv` |
| `legacy methods` | Skills only | No (runs from GitHub) | Users wanting only individual skills |
| `plugin_add.py` | Full interactive TUI | Yes | Local developers debugging the installer |

> **Use `uvx`** (★ recommended default) for an interactive TUI that installs full plugins without requiring Node.js.
> **Use the `bootstrap.py` curl pipeline** if you do not have `uv` installed.
> **Use `plugin_add.py`** directly for scripted/CI single-plugin installs from a local clone.

## Initial vs Subsequent Installs

There is no difference between an initial install and a subsequent install from the consumer's perspective. Because `uvx` and `bootstrap.py` execute ephemerally, they are inherently stateless tooling. 

You do not need to "install the installer". Just run the `uvx` or `curl` command whenever you need to add or update a plugin. The state is strictly kept inside your `.agents/` repository.

---

## Attribution

The `plugin_add.py` interactive TUI (multiselect, arrow-key navigation, fuzzy search, `owner/repo` GitHub shorthand, temp-clone-then-install flow) is inspired by universal one-liner installation patterns:

- GitHub Repository Patterns: <https://github.com/vercel-labs/skills>
- Marketplace: <https://skills.sh>

This implementation re-creates those UX patterns in **pure Python stdlib** (no npm, no external packages) so they work on Windows without symlink issues and operate at the **plugin** level rather than individual SKILL.md files.

---

## Architecture: How Installation Works

```
plugins/<plugin>/
  skills/          → .agents/skills/<skill>/        (canonical copy, all agents read from here)
                     .claude/skills/<skill>          → symlink (Claude Code)
  commands/        → .agents/workflows/<plugin>_<cmd>.md  (canonical copy)
                     .claude/commands/<plugin>_<cmd>.md   → symlink (Claude Code)
  rules/           → .agents/rules/<plugin>_<rule>.md     (canonical copy)
                     CLAUDE.md                            → appended (Claude Code)
  hooks/hooks.json → .agents/hooks/<plugin>-hooks.json   (canonical copy)
                     .claude/hooks/<plugin>-hooks.json    → symlink (Claude only)
  .mcp.json        → ./.mcp.json                         (merged)
```

**Central store is always `.agents/` at project root.** Symlinks point from
each agent's own directory back into `.agents/`. This mirrors exactly how
`npx skills` manages its canonical store at `.agents/skills/`.

---

## Component Mapping Matrix

| Component | `.agents/` (canonical) | `.claude/` (Claude Code) |
|-----------|---------------------

*(content truncated)*

## See Also

- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]
- [[template-post-run-agent-self-assessment]]
- [[research-summary-agent-operating-systems-agent-os]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/plugin-installer/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.188601+00:00
