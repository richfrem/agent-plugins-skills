# Copilot Instructions for agent-plugins-skills

> Authoritative rules for all AI agents (Claude Code, Copilot, Gemini) working in this repo.
> Mirrors CLAUDE.md — keep in sync.

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## Project-Specific Rules

### Purpose
Upstream source monorepo for a cross-platform library of reusable AI agent plugins and skills.
Plugins are authored here and deployed into target projects via the bridge installer.
Individual skills must be **fully self-contained** — no runtime cross-plugin dependencies.

### Key Commands
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
```

> **Windows**: Never use `npx skills add` — use `uvx` or `bootstrap.py` instead.

```bash
# Dependencies (per plugin)
pip-compile ./requirements.in && pip install -r ./requirements.txt
```

### Architecture
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

## Plugin Evolution Entry Points

The agent-agentic-os plugin provides a structured workflow for evolving any plugin,
skill, or sub-agent in this repo. Three key capabilities:

| Skill / Agent | Invoke as | Purpose |
|---------------|-----------|---------|
| `os-architect` | `/os-architect` | Front-door intake — start here for any evolution activity |
| `os-evolution-planner` | called by os-architect | Writes task plans + Copilot CLI delegation prompts |
| `os-architect-tester` | agent dispatch | Validates os-architect via pre-scripted scenario transcripts |

### Evolution workflow

1. **Invoke `/os-architect`** — describe what you want to evolve in plain language
2. **Intent classified** into one of 5 categories (pattern abstraction, research application, lab setup, gap fill, multi-loop)
3. **Ecosystem audit** — os-architect checks what exists vs what's needed
4. **Path proposed**: A (orchestrate existing) / B (update existing) / C (create new)
5. **os-evolution-planner** writes the task plan + Copilot CLI delegation prompt
6. **Dispatch** via `run_agent.py` with `claude-sonnet-4.6` (single premium request, batch everything)
7. **Validate** via `os-architect-tester` after any changes to os-architect

---

## Plugin State — Current Versions (11 plugins · 137 skills)

### agent-agentic-os (v1.7.0)

Core improvement loop:
```
os-architect → os-improvement-loop → os-eval-runner → os-eval-backport → os-experiment-log
```

**Active skills (17):** os-architect, os-improvement-loop, os-eval-runner, os-eval-lab-setup,
os-eval-backport, os-experiment-log, os-evolution-planner, os-evolution-verifier,
os-environment-probe, os-memory-manager, os-improvement-report, os-guide, os-init,
os-clean-locks, todo-check, optimize-agent-instructions, self-evolution

**Agents (5):** os-architect-agent, os-architect-tester-agent, improvement-intake-agent,
agentic-os-setup, os-health-check

**Do not reference:** `triple-loop-architect`, `triple-loop-orchestrator`

**os-skill-improvement**: exists as a methodology/reference skill — **do not delete**. Prefer `os-improvement-loop` for active orchestration unless specifically improving skill routing methodology.

---

### agent-loops (v2.1.0) — OS-decoupled

**6 execution primitives:** orchestrator, learning-loop, dual-loop, agent-swarm, red-team-review, triple-loop-learning

**Plugin boundary:** agent-loops provides execution patterns only — no eval gate, no memory.
os-improvement-loop delegates its inner loop to `triple-loop-learning` as the execution substrate.

Do not add OS infrastructure (evals, memory promotion, kernel calls) to agent-loops skills.

---

### cli-agents (v1.1.0) — consolidated from claude-cli, copilot-cli, gemini-cli

**Skills (6):** agy-cli-agent, claude-cli-agent, copilot-cli-agent, gemini-cli-agent,
claude-project-setup, antigravity-project-setup

**Note:** `gemini-cli-agent` — Gemini CLI consumer access ends June 18, 2026. Use `agy-cli-agent` for frontier models going forward.

**Scripts:** Each skill has its own `scripts/run_agent.py` for its respective CLI tool.

**Do not reference:** `plugins/claude-cli`, `plugins/copilot-cli`, `plugins/gemini-cli` — all deleted.

---

### agent-memory (v1.0.0) — consolidated from rlm-factory, vector-db, memory-management

**Skills (13):** rlm-init, rlm-curator, rlm-search, rlm-distill-agent, rlm-cleanup-agent,
rlm-audit, vector-db-init, vector-db-launch, vector-db-ingest, vector-db-search,
vector-db-cleanup, vector-db-audit, memory-management

**Do not reference:** `plugins/rlm-factory`, `plugins/vector-db`, `plugins/memory-management` — all deleted.

---

### dev-utils (v1.1.0) — consolidated from 9 standalone plugins

**Skills (12):** adr-management, coding-conventions-agent, context-bundler, convert-mermaid,
hf-init, hf-upload, humanize, link-checker-agent, optimize-context, red-team-bundler,
symlink-manager, task-agent

**Do not reference:** `plugins/adr-manager`, `plugins/coding-conventions`, `plugins/context-bundler`,
`plugins/huggingface-utils`, `plugins/link-checker`, `plugins/mermaid-to-png`,
`plugins/task-manager`, `plugins/voice-writer` — all deleted.

### Copilot CLI delegation pattern (canonical)

> **June 2026:** `gpt-5-mini` remains included (no AI Credits cost). All other models consume credits per token. Plan first — fewer requests saves quality, not necessarily credits. See `cli-agents/skills/copilot-cli-agent` for updated model table.

```bash
# 1. Heartbeat (included model — always first, zero credit cost)
python3 plugins/cli-agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null temp/heartbeat.md "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."

# 2. Dispatch (plan well, batch for coherence)
python3 plugins/cli-agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null tasks/todo/copilot_prompt_<task>.md temp/copilot_output_<task>.md \
  "Generate all files exactly as specified. Use the Write tool to write files directly." \
  claude-sonnet-4.6

# 3. Verify output before claiming complete
wc -l temp/copilot_output_<task>.md  # expect 100+ lines for multi-file output
```

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

- **Friction = self-evolution event**: Any workaround, bypass, guess, or user correction requires fix / Map Debt / escalation before claiming done. Output the `PRE-COMPLETION GATE` block. Full rule: `.agent/rules/self-evolution-policy.md`
- **No file deletions without explicit user permission** (self-evolution policy). Auto-approved: adding functions, appending. Explicit confirmation required: rename/move. Hard gated: any deletion. Full rule: `.agent/rules/self-evolution-policy.md`
- **Skill deletion pre-check**: Before deleting anything under `plugins/**/skills/`, apply `.agent/rules/skill-deletion-guard.md`. If the reason contains "redundant", "absorbed", "consolidated", "superseded", "duplicate", "cleanup", "merge", "simplify", or "replace" — hard stop and ask the user to name the exact skill path.
- **ADR-001**: No cross-plugin script execution — delegate via agent skill at runtime
- **ADR-002**: Within-plugin multi-skill script sharing via hub-and-spoke (plugin root `scripts/`)
- **ADR-003**: File-level symlinks only — never directory symlinks, never duplicate files
- **ADR-004**: Installed artifacts must be self-contained — no runtime cross-plugin paths
- **ADR-007**: MAF is an optional certified runtime adapter — `.md` manifests are the source of truth, portable across Claude Code / Copilot CLI / Gemini CLI / MAF. Do not make MAF the primary orchestration kernel.

### Security-sensitive control plane (exploration-cycle-plugin)
`plugins/exploration-cycle-plugin/scripts/` contains the Python control plane: `dispatch.py`, `state_engine.py`, `sandbox_runner.py`. These files have active security work (v1.3 shipped; v1.4 in progress). Before modifying them, read `ADRs/007_maf_adapter_runtime_decision.md` and `docs/superpowers/specs/2026-05-31-maf-synthesis-v1.4-spec.md` for the current security model and planned changes. Do not add casual convenience bypasses to the authorization gate or path enforcement.

### Skill Standards (always applied)
- Skill `name`: kebab-case, matches directory name exactly, 1–64 chars
- Skill `description`: third person ("Extracts text", not "I extract text")
- `evals.json`: must use `should_trigger: true/false` — legacy `expected_behavior` produces 0% accuracy
- SKILL.md: under ~500 lines; extra detail goes in `references/` files
- Helper scripts: Python only — never generate `.sh` bash scripts

### Scaffolding New Plugins/Skills
Use these skills rather than hand-rolling structure:
- `create-plugin` — full plugin scaffold with discovery interview
- `create-skill` — skill scaffold with evals, references, acceptance-criteria
- `audit-plugin` — validate structure after scaffolding

Then run `plugin_add.py` to deploy.

### Scratch Output
Write temporary files and analysis output to `temp/` — never to the project root directly.
