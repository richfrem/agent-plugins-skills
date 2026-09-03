# AGENTS.md


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

**This working directory has no application/domain data.** If a session shows a domain-specific
slash command or agent (e.g. `portfolio-advisor`, `tradingview`, `stock-valuation`) that isn't one
of the plugins listed below, it's installed globally via the Claude Code marketplace and belongs
to a *different* project — it expects files (e.g. `investment_screener/backend/data/...`) that
don't exist here. Check `pwd` before assuming this repo owns an unfamiliar command.

### Key Commands
```bash
# Install plugins into any project (recommended)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Install a specific plugin non-interactively (e.g., agent-orchestration/)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills/plugins/agent-orchestration -y

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

### Plugin Reinstall Rule (always active)

> **After modifying any skill, script, reference, sub-agent, or plugin source file in `plugins/`**, you MUST reinstall the affected plugin(s) into `.agents/` so the live runtime reflects the changes and gets replicated/updated.
> The skills in `.agents/skills/` are what agents actually run — edits to `plugins/` are inactive until synced.

```bash
# Reinstall all plugins from local source (recommended after multi-plugin edits / testing)
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y

# Alternatively, sync all tracked plugins
python3 plugins/plugin-manager/scripts/sync_with_inventory.py

# Reinstall a single plugin only
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/<plugin-name> -y
```

Skip reinstall only for: documentation-only edits to `references/`, `ADRs/`, or `docs/` that contain no agent-executable content.

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
> **`plugins/` is the source of truth.** `.agents/` and the Claude Code marketplace/plugin system
> contain installed copies only — never treat them as authoritative. All counts, skill lists, and
> version references in this file must reflect what is in `plugins/`, not what is installed.
> Skills run from `.agents/skills/` at runtime — NOT from `plugins/`. Files in `plugins/` are
> inactive until installed via `plugin_add.py` or `uvx`.

See `plugins/plugin-manager/scripts/` for ecosystem management scripts.
See `ADRs/` for authoritative architecture rules.
See `architecture.md` for the full repo architecture overview (project structure, plugin-by-plugin breakdown, ADR summary, symlink system, runtime state layout).

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

## Idea Intake Entry Points

Three front doors exist for a new idea, problem, or need. They are **not 1:1** — pick by how
well the problem is already understood, not by idea "type":

| Starting point | Entry point | Output |
|---|---|---|
| Already know exactly what's broken/needed | `github-issue-agent` — file the issue directly | GitHub Issue |
| Know WHAT to build, need to design the HOW (single subsystem, one session) | `superpowers:brainstorming` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` |
| Don't know the shape yet — unknowns, multiple stakeholders, need a prototype first | `exploration-cycle-plugin`'s `intake-agent` (multi-session discovery) | `exploration/handoffs/handoff-package.md` |

**Confirmed bridge, not a guess:** `handoff-preparer-agent.md` explicitly offers a "Superpowers"
destination and writes to the *same* `docs/superpowers/specs/` path/format `brainstorming`
produces directly. Exploration-cycle is a heavier front-end for fuzzy problems — it funnels into
the same `writing-plans` → `docs/superpowers/plans/` pipeline once the problem is shaped, not a
competing path. (The "Spec-Kitty" destination also offered there is unused in this repo — see the
spec-kitty note above.)

**When to create/link the GitHub issue:** at the commit-to-build moment (after `writing-plans`
produces a plan doc), not at idea time — early design thinking can dead-end, and tracking
abandoned explorations is noise. If an issue already exists and the fix turns out to need real
design work, drop into brainstorming from there and link the resulting spec back onto the *same*
issue (`gh_issue_comment.py`) rather than opening a duplicate — see
`github-issue-logging-policy.md` §3, Root-Cause Consolidation.

---

**spec-kitty is not installed or used in this repo.** `plugins/spec-kitty-plugin/` is legacy/deprecated
(superseded by the native Spec Kitty CLI, per README.md) and was never part of the tracked local plugin
set in `plugin-sources.json`. Do not suggest routing work to spec-kitty or `spk-*` skills unless the user
explicitly reinstalls it themselves.

## Plugin State — Current Versions (10 plugins · 137 skills)

### agent-agentic-os (v1.8.0)

Core improvement loop:
```
os-architect → os-improvement-loop → os-eval-runner → os-eval-backport → os-experiment-log
```

**Active skills (18):** os-architect, os-improvement-loop, os-eval-runner, os-eval-lab-setup,
os-eval-backport, os-experiment-log, os-evolution-planner, os-evolution-verifier,
os-environment-probe, os-memory-manager, os-improvement-report, os-guide, os-init,
os-clean-locks, todo-check, optimize-agent-instructions, self-evolution, gpt55-critical-auditor

**Reference skills (1):** os-skill-improvement — methodology/reference only; prefer `os-improvement-loop` for active orchestration. **Do not delete.**

**Agents (5):** os-architect-agent, os-architect-tester-agent, improvement-intake-agent,
agentic-os-setup, os-health-check

**Do not reference:** `triple-loop-architect`, `triple-loop-orchestrator`

---

### agent-orchestration (v2.3.0) — OS-decoupled

**9 execution primitives:** orchestrator, select-loop-strategy, co-pilot-loop, learning-loop, dual-loop, agent-swarm, red-team-review, triple-loop-learning, graph-execution

**Plugin boundary:** agent-orchestration/ provides execution patterns only — no eval gate, no memory.
os-improvement-loop delegates its inner loop to `triple-loop-learning` as the execution substrate.

Do not add OS infrastructure (evals, memory promotion, kernel calls) to agent-orchestration/ skills.

---

### cli-agents (v2.1.0) — consolidated from claude-cli, copilot-cli, gemini-cli

**Skills (14):** agent-file-synchronization, agt-security, agy-cli-agent, antigravity-project-setup,
claude-cli-agent, claude-project-setup, codex-cli-agent, copilot-cli-agent, gemini-cli-agent,
local-llm-bridge, local-llm-setup, maf-adapter, project-setup, update-cli-models

**Note:** `gemini-cli-agent` — Gemini CLI consumer access ended June 18, 2026 (that date has now passed). Only enterprise Gemini Code Assist licenses retain the `gemini` binary. Use `agy-cli-agent` — it is now the primary path for Gemini model access, not just frontier models.

**Scripts:** Each skill has its own `scripts/run_agent.py` for its respective CLI tool.

**Do not reference:** `plugins/claude-cli`, `plugins/copilot-cli`, `plugins/gemini-cli` — all deleted.

---

### agent-memory (v1.0.0) — consolidated from rlm-factory, vector-db, memory-management

**Skills (13):** rlm-init, rlm-curator, rlm-search, rlm-distill-agent, rlm-cleanup-agent,
rlm-audit, vector-db-init, vector-db-launch, vector-db-ingest, vector-db-search,
vector-db-cleanup, vector-db-audit, memory-management

**Do not reference:** `plugins/rlm-factory`, `plugins/vector-db`, `plugins/memory-management` — all deleted.

---

### dev-utils (v1.4.0) — consolidated from 9 standalone plugins

**Skills (17):** adr-management, coding-conventions-agent, context-bundler, convert-mermaid,
github-issue-agent, github-issue-backlog-agent, github-issue-prioritizer, hf-init, hf-upload,
hf-download, humanize, issue-pr-lifecycle-agent, issue-worktree-agent, link-checker-agent,
optimize-context, symlink-manager, task-agent

**Do not reference:** `plugins/adr-manager`, `plugins/coding-conventions`, `plugins/context-bundler`,
`plugins/huggingface-utils`, `plugins/link-checker`, `plugins/mermaid-to-png`,
`plugins/task-manager`, `plugins/voice-writer` — all deleted.

### Copilot CLI delegation pattern (canonical)

> **June 2026:** All Copilot models bill per AI Credits (token-based). Model selection should use
> `plugins/cli-agents/references/copilot-models.json` — see the `strategy` field for tier recommendations
> and `cost_tiers` for cheapest-to-most-expensive groupings. Plan first — fewer requests saves credits.

```bash
# 1. Heartbeat — use cheapest model (see copilot-models.json strategy.heartbeat)
python3 plugins/cli-agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null temp/heartbeat.md "HEARTBEAT CHECK: Respond HEARTBEAT_OK only." \
  gpt-5.4-nano

# 2. Dispatch — pick model from copilot-models.json strategy field for the task tier
python3 plugins/cli-agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null tasks/todo/copilot_prompt_<task>.md temp/copilot_output_<task>.md \
  "Generate all files exactly as specified. Use the Write tool to write files directly." \
  claude-sonnet-4.6  # strategy.complex — see copilot-models.json

# 3. Verify output before claiming complete
wc -l temp/copilot_output_<task>.md  # expect 100+ lines for multi-file output
```

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

- **Source of truth**: `plugins/` is authoritative. `.agents/`, the marketplace, and the Claude Code plugin system are installed copies — never use them to derive counts, versions, or skill lists.
- **TDW (TDD & TDO)**: No code development or orchestration execution without a failing test or success contract first. Full rule: `.agent/rules/test-driven-development.md`
- **Self-Evolution & Map Debt**: Classify failures/friction (Tiers 0/1/2/3), max 3 attempts. Active map debt audit must pass. Always execute the `PRE-COMPLETION GATE` check block and log map debt before ending the session. Full rule: `.agent/rules/self-evolution-policy.md`
- **Evolution Integrity Gate**: PRs modifying core logic (`plugins/`, `src/`, `py_services/`) must stage an update to `references/map-debt.md` or `references/evolution-log.md`, or include `Evolution-Check: none` in the commit message.
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

### After editing any skill or script in a plugin — audit symlinks
**Never use `ln -s` directly. All symlink operations must go through `symlink_manager.py`.**
(Full protocol: `.agent/rules/symlink-cross-platform.md`)

```bash
# 1. Diagnose first — always
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose

# 2. Add new links to symlinks.json manifest (not by hand — via script)
# 3. Restore all from manifest
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py restore

# 4. Verify — zero broken or real-file imposters before committing
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
```
Fix any BROKEN entries before committing. A broken symlink in `plugins/` will silently fail at install time.
Shared scripts live in `plugins/<plugin>/scripts/` and are symlinked into each skill's `scripts/` — if you add a new shared script, add it to `symlinks.json` then run `restore`.

### skills-lock.json is machine-generated — never hand-edit, never manually merge conflicts in it
`skills-lock.json` records per-skill `installedAt`/`updatedAt` timestamps written by `plugin_add.py`/
`sync_with_inventory.py`. Two branches that each ran a reinstall independently will diverge on nearly
every entry — this is pure timestamp noise, not a real conflict. On a merge/rebase conflict in this file:
take either side to clear the markers (`git checkout --ours skills-lock.json` is fine), then regenerate it
fresh with `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y` and re-stage. Do not attempt
to manually reconcile `<<<<<<<`/`=======`/`>>>>>>>` blocks in this file line by line.
Note: the reinstall/sync scripts add and update entries but do not prune ones for skills that were
deleted — if you remove a skill, manually delete its `skills-lock.json` entry too.

### Run both plugin audits after any skill/plugin create or update
`audit.py` (compliance) and `audit_plugin_structure.py` (structural) check different things — passing
one does not mean the other passes. A new script or asset file written directly inside a skill directory
instead of the plugin root (ADR-002/003 hub-and-spoke) is invisible to `audit.py` and only caught by
`audit_plugin_structure.py`. Run both before considering any new or edited skill/plugin complete:

```bash
python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/<plugin-name>
python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>
```

Fix any structural errors via `symlink_manager.py` (move the real file to the plugin root, add a
`symlinks.json` entry, `restore`) — never `mv`/`ln -s` by hand. See `self-evolution-policy.md` Rule 12.

### Scaffolding New Plugins/Skills
Use these skills rather than hand-rolling structure:
- `create-plugin` — full plugin scaffold with discovery interview
- `create-skill` — skill scaffold with evals, references, acceptance-criteria
- `audit-plugin` — validate structure after scaffolding

Then run `plugin_add.py` to deploy.

### Instruction File Mirrors — CLAUDE.md, GEMINI.md, copilot-instructions.md, AGENTS.md
When the user asks to replicate CLAUDE.md into the other instruction files, the default workflow is a
**full copy with only the top `# ` line renamed** — but each target file has platform-specific content
that a blind copy will silently destroy. Check for and re-append these before considering the sync done:

| File | Platform-specific addition to preserve | Corresponding `cli-agents` skill |
|---|---|---|
| `GEMINI.md` | `## Gemini CLI Tool Mapping` table at the end of the file (Claude Code tool name → Gemini CLI equivalent) | `gemini-cli-agent` (deprecated, see note above), `agy-cli-agent` |
| `.github/copilot-instructions.md` | Header must be `# Copilot Instructions for <repo-name>` + an "Authoritative... Mirrors CLAUDE.md" blockquote, not a generic title | `copilot-cli-agent` |
| `AGENTS.md` | Cross-tool convention (Codex and other OpenAI-compatible agents read this file) — currently no required platform-specific section beyond shared content, but verify before assuming that's still true | `codex-cli-agent` |
| `CLAUDE.md` | Source of truth — no platform section of its own | `claude-cli-agent`, `claude-project-setup` |

The full canonical rules for what belongs in each file live in `optimize-agent-instructions`
(`plugins/agent-agentic-os/skills/optimize-agent-instructions/SKILL.md`) — consult it, don't just
diff against memory of what was there before. This was missed once already this session: a full-copy
sync silently dropped GEMINI.md's tool-mapping table until caught in a later manual review.

### Active Rule Files
Full rule definitions live in `.agent/rules/` — these are the authoritative source, CLAUDE.md carries only the key non-negotiables.

**Some rule files exist as multiple logical copies — check before editing more than one.** A few are real
symlinks (e.g. `plugins/agent-agentic-os/skills/self-evolution/references/self-evolution-policy.md` →
`plugins/agent-agentic-os/rules/self-evolution-policy.md`; edit the real target once, both update). Others
are genuinely independent duplicate files with no symlink relationship (e.g. `.agent/rules/self-evolution-policy.md`
is a separate copy from the plugin's own copy — each needs its own edit). Run `ls -la` / `readlink` on every
known copy before editing to avoid either double-editing a symlink target or missing an independent duplicate.
- `coding-conventions.md` — dual-layer docs, file headers, type hints, naming, `tool_inventory.json` registration
- `dependency-management.md` — pip-compile workflow, no manual pip install, tiered hierarchy
- `plugin-architecture-policy.md` — decoupling, hub-and-spoke, relative paths, self-contained skills
- `self-evolution-policy.md` — failure tiers, 3-attempt max, deletion prohibition, autonomy gates
- `symlink-cross-platform.md` — `symlink_manager.py` protocol, symlinks.json manifest
- `test-driven-development.md` — TDD iron law, test tier locations, anti-patterns
- `github-issue-logging-policy.md` — friction-tier → GitHub Issue decision matrix; **mandatory dedup search
  (`gh_issue_search.py`) before filing any new issue** — consolidate into an existing root-cause issue via
  comment rather than opening a duplicate; 5 required body sections (Summary/Observed/Expected/Evidence/Impact)
- `graph-planning-superpowers-policy.md` — the plan/review/execution lifecycle for significant work: enter
  native Plan Mode (`/plan`) before drafting a plan (Phase 1), fan-out the plan draft to the Architecture
  Skeptic / Security-Edge-Case Auditor / TDD Contract Reviewer trio via `context-bundler`'s Multi-Persona
  Fan-Out Mode with a 2-3 round convergence cap, then execute in an isolated worktree with Superpowers TDD
  (Phase 2), then multi-stage verify — deterministic tests, worktree merge, out-of-band bundle review
  (Phase 3). Applies whenever `spec-driven-development-policy.md` used to apply — that file no longer exists.

### GitHub Issue Lifecycle Skills (dev-utils)
Local task scratchpad (`task-agent`) is ephemeral and gitignored — durable backlog lives as GitHub Issues:
```
github-issue-agent          ← create/search/comment/close issues; friction_cluster_agent for hotspot synthesis
github-issue-backlog-agent  ← bridge: promote tasks/*.md → GitHub Issue (dry-run default, --execute for live)
github-issue-prioritizer    ← rank issues, sync GitHub Projects v2
issue-worktree-agent        ← isolated git worktree per issue
issue-pr-lifecycle-agent    ← full issue → worktree → PR → close orchestration
```
`issue-resolution-reviewer` (agent-agentic-os) — post-closure quality audit sub-agent.
`gh_issue_create.py` auto-creates missing taxonomy labels (`type:*`/`tier:*`/`area:*`/etc.)
on first live use — the repo doesn't pre-register them.

### Scratch Output
Write temporary files and analysis output to `temp/` — never to the project root directly.
