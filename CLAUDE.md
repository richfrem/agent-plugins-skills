# CLAUDE.md

## Purpose

Upstream source monorepo for a cross-platform library of reusable AI agent plugins and skills.
Plugins are authored here and deployed into target projects via the bridge installer.
Individual skills must be **fully self-contained** — no runtime cross-plugin dependencies.

---

## Key Commands

```bash
# Install plugins into any project (recommended)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Interactive local install
python plugins/plugin-manager/scripts/plugin_add.py

# Bulk install all plugins
python plugins/plugin-manager/scripts/install_all_plugins.py
```

> **Windows**: Never use `npx skills add` — use `uvx` or `bootstrap.py` instead.

```bash
# Dependencies (per plugin)
pip-compile ./requirements.in && pip install -r ./requirements.txt
```

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

See `plugins/plugin-manager/scripts/` for ecosystem management scripts.
See `ADRs/` for authoritative architecture rules.

---

## Behavior & Judgment (Karpathy Principles)

These govern HOW to think, not just what to do. Apply before writing any code or content.

### 1. Think Before Acting

Don't assume. Don't hide confusion. Surface tradeoffs before starting.

- State assumptions explicitly. If uncertain, ask — don't run with a guess.
- If multiple interpretations exist, name them. Pick only after confirming.
- Before adding a new skill or plugin, ask: does this belong in an existing plugin? Is there a scaffold skill to use (`create-skill`, `create-plugin`)?
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

Minimum change that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- SKILL.md under ~500 lines — push extra detail to `references/` files.
- No error handling for impossible scenarios.
- If 200 lines could be 50, rewrite it. If a skill could be a pointer file, make it one.

Ask: *Would a senior engineer say this is overcomplicated? If yes, simplify.*

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent SKILL.md sections, comments, or evals you weren't asked to change.
- Don't refactor things that aren't broken.
- Match existing style in the plugin you're editing, even if you'd do it differently.
- If you notice unrelated dead code or stale skill content, mention it — don't silently fix it.
- Every changed line should trace directly to what was asked.

### 4. Goal-Driven Execution

Define success criteria first. Loop until verified.

- For evals: write `evals.json` routing criteria *before* writing SKILL.md content. The evals are the spec.
- For scripts: state what the script will output and verify it before claiming complete.
- For multi-step tasks, state a brief plan with a verification step for each stage.
- Use the `verification-before-completion` skill on non-trivial tasks — it enforces shell verification before claiming done.

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
- SKILL.md: under ~500 lines; extra detail goes in `references/` files
- Helper scripts: Python only — never generate `.sh` bash scripts

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

Before reading source files blindly or running grep across the whole repo, follow the 3-phase protocol:

| Phase | Command | When to use |
|:------|:--------|:------------|
| **1 — Keyword (O(1))** | `/rlm-factory:search "term"` | Always start here. Dense summaries of every file. |
| **2 — Semantic (O(log N))** | `/vector-db:search "term"` | When Phase 1 finds the right area but lacks the exact payload. |
| **3 — Concept node** | `/wiki-query "concept"` | When you need the full synthesized understanding of a concept. |

Only fall back to raw `grep` if all three phases miss entirely.

The RLM cache is at `.agent/learning/`. The wiki is at `.wiki/`. Vector data at `.vector_data/`.
