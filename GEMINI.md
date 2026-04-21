# GEMINI.md

> Gemini CLI instructions for the agent-plugins-skills monorepo.
> Mirrors CLAUDE.md — authoritative rules for all AI agents working in this repo.

## Purpose

Upstream source monorepo for a cross-platform library of reusable AI agent plugins and skills.
Plugins are authored here and deployed into target projects via the bridge installer.
Individual skills must be **fully self-contained** — no runtime cross-plugin dependencies.

---

## Key Commands

```bash
# Install plugins into any project (recommended)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Install a specific plugin non-interactively (e.g., agent-loops)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills/plugins/agent-loops -y

# Interactive local install
python plugins/plugin-manager/scripts/plugin_add.py

# Bulk install all plugins
python plugins/plugin-manager/scripts/plugin_add.py --all -y

# Local installation testing via uvx (uses remote script but local plugin files)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add plugins/
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add plugins/agent-scaffolders


# Dependencies (per plugin)
pip-compile ./requirements.in && pip install -r ./requirements.txt
```

> **Windows**: Never use `npx skills add` — use `uvx` or `bootstrap.py` instead.

---

## Architecture

```
plugins/<plugin>/           ← canonical source
  skills/<skill>/SKILL.md   ← skill definition
  evals/evals.json          ← routing evals (should_trigger boolean schema)
  scripts/                  ← shared scripts (file-level symlinks only)
  agents/ commands/         ← sub-agents and slash commands

.agents/                    ← bridge installer output (hard copies, symlinks resolved)
  skills/ agents/ workflows/
```

> Skills run from `.agents/skills/` at runtime — NOT from `plugins/`. The `plugins/` directory
> is the source. Files there are inactive until installed via `plugin_add.py` or `uvx`.

See `ADRs/` for authoritative architecture rules.

---

## Behavior & Judgment (Karpathy Principles)

Apply before writing any code or content.

### 1. Think Before Acting
Don't assume. Surface tradeoffs before starting. If uncertain, ask — don't run with a guess.
Before adding a new skill or plugin, ask: does this belong in an existing plugin? Is there a scaffold skill to use?

### 2. Simplicity First
Minimum change that solves the problem. SKILL.md under ~500 lines. No abstractions for single-use code. No features beyond what was asked.

### 3. Surgical Changes
Touch only what you must. Don't improve adjacent sections you weren't asked to change. Every changed line traces directly to what was asked.

### 4. Goal-Driven Execution
Define success criteria first. For evals: write `evals.json` routing criteria before writing SKILL.md content. Verify outputs before claiming complete.

---

## Coding Rules (always applied)

- **ADR-001**: No cross-plugin script execution — delegate via agent skill at runtime
- **ADR-002**: Within-plugin multi-skill script sharing via hub-and-spoke (plugin root `scripts/`)
- **ADR-003**: File-level symlinks only — never directory symlinks, never duplicate files
- **ADR-004**: Installed artifacts must be self-contained — no runtime cross-plugin paths

---

## Skill Standards (always applied)

- Skill `name`: kebab-case, matches directory name exactly, 1–64 chars
- Skill `description`: third person ("Extracts text", not "I extract text")
- `evals.json`: must use `should_trigger: true/false` — legacy `expected_behavior` produces 0% accuracy
- SKILL.md: under ~500 lines; extra detail in `references/`
- Helper scripts: Python only — never `.sh` bash scripts

---

## Scaffolding New Plugins/Skills

Use these skills rather than hand-rolling structure:
- `create-plugin` — full plugin scaffold with discovery interview
- `create-skill` — skill scaffold with evals, references, acceptance-criteria
- `audit-plugin` — validate structure after scaffolding

Then run `plugin_add.py` to deploy.

---

## Scratch Output

Write temporary files and analysis output to `temp/` — never to the project root directly.

---

## Context Retrieval Protocol (Super-RAG)

Before reading source files blindly or running grep, follow the 3-phase protocol:

| Phase | Command | When to use |
|:------|:--------|:------------|
| **1 — Keyword (O(1))** | `/rlm-factory:search "term"` | Always start here. Dense summaries of every file. |
| **2 — Semantic (O(log N))** | `/vector-db:search "term"` | When Phase 1 finds the right area but needs deeper retrieval. |
| **3 — Concept node** | `/wiki-query "concept"` | Full synthesized understanding of a concept. |

Only fall back to raw `grep` if all three phases miss entirely.

---

## Gemini CLI Tool Mapping

Gemini CLI uses different tool names from Claude Code. Key equivalents:

| Claude Code | Gemini CLI equivalent |
|:------------|:----------------------|
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `replace_in_file` |
| `Bash` | `run_shell_command` |
| `Glob` | `glob` |
| `Grep` | `grep` |

Skills in `.agents/skills/` use Claude Code tool names in their SKILL.md files.
When executing skills via Gemini, translate tool references using the table above.
