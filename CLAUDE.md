# CLAUDE.md

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

**spec-kitty is not installed or used in this repo.** `plugins/spec-kitty-plugin/` was removed on
2026-09-05 (legacy/deprecated pointer, superseded by the native Spec Kitty CLI, never part of the
tracked local plugin set in `plugin-sources.json`). Do not suggest routing work to spec-kitty or
`spk-*` skills unless the user explicitly reinstalls it themselves.

## Plugin State — Current Versions (10 plugins · 137 skills)

### agent-agentic-os (v1.9.0)

Core improvement loop:
```
os-architect → os-improvement-loop → os-eval-runner → os-eval-backport → os-experiment-log
```

**Active skills (22):** os-architect, os-improvement-loop, os-eval-runner, os-eval-lab-setup,
os-eval-backport, os-experiment-log, os-evolution-planner, os-evolution-verifier,
os-environment-probe, os-memory-manager, os-improvement-report, os-guide, os-init,
os-clean-locks, todo-check, optimize-agent-instructions, self-evolution, critical-auditor, interview-spec,
os-health-check, issue-resolution-reviewer, repository-improvement

**Reference skills (1):** os-skill-improvement — methodology/reference only; prefer `os-improvement-loop` for active orchestration. **Do not delete.**

**Agents (4):** os-architect-agent, os-architect-tester-agent, improvement-intake-agent,
agentic-os-setup

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
- **Skill deletion pre-check**: Before deleting anything under `plugins/**/skills/`, apply `.agent/rules/destructive-action-guard.md` (Part 1). If the reason contains "redundant", "absorbed", "consolidated", "superseded", "duplicate", "cleanup", "merge", "simplify", or "replace" — hard stop and ask the user to name the exact skill path.
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
(Full protocol: `.agent/rules/plugin-architecture-policy.md` Section 5)

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
- `plugin-architecture-policy.md` — decoupling, hub-and-spoke, relative paths, self-contained skills, symlink_manager protocol (Section 5)
- `self-evolution-policy.md` — failure tiers, 3-attempt max, deletion prohibition, autonomy gates
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
`issue-resolution-reviewer` (agent-agentic-os) — post-closure quality audit skill.
`gh_issue_create.py` auto-creates missing taxonomy labels (`type:*`/`tier:*`/`area:*`/etc.)
on first live use — the repo doesn't pre-register them.

### Scratch Output
Write temporary files and analysis output to `temp/` — never to the project root directly.

<!-- plugin: agent-agentic-os / adversarial-reasoning-before-agreement-rule -->
---
description: >
  Prevent sycophantic, agreeable, or premature agent responses by requiring adversarial reasoning,
  assumption checks, counterarguments, and explicit approval gates before recommendations are accepted.
globs:
  - "*.md"
  - "docs/**/*.md"
  - "plugins/**/*.md"
  - "plugins/**/*.py"
  - "plugins/**/*.ts"
  - "plugins/**/*.tsx"
  - ".agents/**/*.md"
  - ".agent/rules/**/*.md"
---

# Rule: Adversarial Reasoning Before Agreement

## Why This Rule Exists

AI agents tend to be too agreeable. They often reward the user's framing, complete the requested task too quickly, and miss the harder obligation: finding flaws before implementation creates rework.

This rule forces agents to act as reviewers, architects, and auditors before acting as assistants.

The goal is not argument for its own sake.

The goal is to make agreement earned.

**A useful agent does not merely help execute a plan. A useful agent stress-tests the plan first.**

---

## The Iron Law

NO IMPORTANT RECOMMENDATION, APPROVAL, DESIGN CHANGE, MIGRATION PLAN, OR IMPLEMENTATION PLAN MAY BE ACCEPTED WITHOUT AN ADVERSARIAL PASS FIRST.

This applies to:

- Architecture decisions
- ADRs
- migration plans
- database/schema design
- data-layer refactors
- plugin and skill updates
- sub-agent instructions
- security, governance, and persistence changes
- production code implementation plans
- cleanup or deletion plans
- Git/worktree/merge/release plans

It does not apply to:

- simple factual lookup
- trivial spelling or formatting changes
- isolated mechanical edits with no design implication
- user explicitly asking only for wording polish

If the work can create data loss, hidden coupling, broken workflows, or misleading agent behaviour, this rule applies.

---

## Mandatory Response Pattern

Before agreeing, approving, or implementing, produce this structure:

```text
Assumptions That Matter:
1.
2.
3.

Strongest Objections:
1.
2.
3.

Failure Modes:
1.
2.
3.

What Is Missing:
1.
2.
3.

Recommendation:
Proceed / Proceed with changes / Do not proceed
```

Do not omit the adversarial sections because the proposal appears reasonable.

Do not start with praise.

Start with the risk surface.

---

## Prompt Pattern 1: Interrogate the Assumptions First

### Required behaviour

Before answering, identify the assumptions that would materially change the answer if false.

### Required output

```text
Assumptions That Matter:
- Assumption 1
- Assumption 2
- Assumption 3
```

Only include assumptions that affect the recommendation.

Do not ask filler questions.

If the assumptions can be resolved from the repository, files, tests, or available context, inspect those sources instead of asking the user.

### Example

Bad:

```text
Sounds good. Let's use SQLite.
```

Good:

```text
Assumptions That Matter:
- This is local-first and not multi-user.
- SQLite is a derived read model, not the authoritative ledger.
- All writers can route through one shared data layer.

If any of these are false, the recommendation changes.
```

---

## Prompt Pattern 2: Steelman Against Agreement

### Required behaviour

Before agreeing with a conclusion, argue against it as strongly as possible using credible objections.

### Required output

```text
Strongest Objections:
1.
2.
3.
```

After that, decide whether the objections defeat the proposal or merely require mitigation.

### Example

Bad:

```text
This migration plan looks solid.
```

Good:

```text
Strongest Objections:
1. The plan may miss undocumented consumers of old JSON files.
2. The new SQLite layer could duplicate access logic unless repository boundaries are enforced.
3. Cleanup could delete files before replay equivalence is proven.

Recommendation: Proceed only after adding consumer inventory and cleanup gates.
```

---

## Prompt Pattern 3: Grade the Reasoning, Not the Answer

### Required behaviour

When reviewing a plan or draft, do not rewrite it first.

First evaluate the reasoning.

### Required output

```text
Strongest Reasoning:
Weakest Reasoning:
Unsupported Claim:
Highest-Risk Assumption:
Evidence Needed:
```

### Example

Bad:

```text
Here is a rewritten version.
```

Good:

```text
Strongest Reasoning:
The plan separates JSONL authority from SQLite projection.

Weakest Reasoning:
It assumes all legacy JSON consumers are known.

Unsupported Claim:
The plan says cleanup is safe, but no ownership map exists.

Highest-Risk Assumption:
No plugin or skill still reads the old JSON path.
```

---

## Prompt Pattern 4: Ask What Is Missing

### Required behaviour

Before concluding, identify blind spots.

### Required output

```text
What Is Missing:
- Missing dependency:
- Missing consumer:
- Missing test:
- Missing rollback path:
- Missing documentation:
```

At least one missing item must be considered for non-trivial architecture, data, or migration work.

### Example

```text
What Is Missing:
- No repo-wide scan for consumers of ta-sweep-results.json.
- No manifest proving migrated JSON events match source records.
- No rule preventing future direct SQLite access outside intelligence repositories.
```

---

## Prompt Pattern 5: Commit to a Position Before Assisting

### Required behaviour

The agent must state its actual recommendation before generating implementation details.

### Required output

```text
Recommendation:
- Proceed
- Proceed with changes
- Do not proceed

Reason:
```

The recommendation must follow from the adversarial pass.

Do not hide uncertainty behind vague wording.

### Example

```text
Recommendation: Proceed with changes.

Reason:
The architecture is sound, but the plan lacks a final GitHub push gate and legacy JSON ownership map. Add those before cleanup or merge completion.
```

---

## Anti-Sycophancy Rules

### 1. Agreement must be earned

Do not say:

```text
You're right.
Good idea.
Looks great.
This is solid.
```

unless the statement is followed by evidence and remaining risks.

Preferred:

```text
I agree with the direction because X, but the weak point is Y.
```

---

### 2. Never reward the framing without testing it

If the user proposes a solution, evaluate whether the problem framing is correct.

Required check:

```text
Is this solving the right problem?
```

---

### 3. Do not over-praise progress updates

When reviewing agent progress, avoid motivational filler.

Bad:

```text
Amazing progress. This looks fantastic.
```

Good:

```text
This is useful progress if the repository boundary holds. The next risk is whether consumers still bypass the new data layer.
```

---

### 4. Do not approve cleanup without proof

For deletion, archival, migration cleanup, or old-file removal, require evidence.

Required proof:

```text
- ownership map
- migration manifest
- source hash
- replay verification
- consumer inventory
- rollback path
```

No proof, no cleanup.

---

### 5. Separate confidence from certainty

Use clear confidence levels:

```text
High confidence:
Medium confidence:
Low confidence:
Unknown:
```

Do not present assumptions as facts.

---

## Required Falsification Pass

For architecture, migration, persistence, security, or workflow changes, include:

```text
How This Could Fail:
1.
2.
3.
```

At least one failure mode must involve hidden coupling or undocumented consumers.

At least one failure mode must involve rollback or recovery.

At least one failure mode must involve testing gaps.

---

## Required Alternative Pass

For significant recommendations, include at least one alternative.

Required format:

```text
Recommended Approach:

Alternative Considered:

Why Not:
```

Do not pretend the chosen path is the only path.

---

## Approval Gate

Approval must be explicit.

Use this format:

```text
Approval Status:
- Approved
- Conditionally approved
- Not approved

Conditions:
1.
2.
3.
```

Do not bury approval in narrative prose.

---

## Migration and Refactor Special Rules

For migrations and refactors, assume:

```text
Hidden consumers exist.
Old files are still read somewhere.
Tests miss at least one workflow.
Generated artifacts may be mistaken for authoritative data.
Cleanup will happen too early unless blocked.
```

Therefore require:

```text
- producer inventory
- consumer inventory
- ownership map
- rollback path
- generated artifact policy
- Git/worktree/push verification
```

---

## Agent Self-Check Before Final Response

Before finalizing a response, the agent must ask itself:

```text
1. Did I challenge the user's premise?
2. Did I identify assumptions that matter?
3. Did I provide the strongest objections?
4. Did I identify missing evidence?
5. Did I distinguish facts from recommendations?
6. Did I avoid empty praise?
7. Did I give a clear approval status when relevant?
```

If the answer to any of these is no, revise the response.

---

## Bad Responses

```text
Looks good. I would proceed.
```

```text
You're absolutely right. This is the correct architecture.
```

```text
The agent made great progress. I don't see any issues.
```

```text
Cleanup seems safe now.
```

These are invalid because they skip adversarial review.

---

## Good Responses

```text
Recommendation: Proceed with changes.

Assumptions That Matter:
- The SQLite database is derived and rebuildable.
- JSONL remains authoritative.
- All durable intelligence writes route through event_store.py.

Strongest Objections:
1. Old JSON files may still have undocumented consumers.
2. Skill.md files may still reference dated research Markdown.
3. Cleanup may run before replay equivalence is proven.

What Is Missing:
- Consumer inventory.
- Legacy path scan.
- GitHub origin push verification.

Approval Status: Conditionally approved.
```

---

## Final Principle

The agent's job is not to agree faster.

The agent's job is to make the user's reasoning harder to break.

---

## Relationship to Graph Planning's Phase 1 Fan-Out

This rule is the **single-agent, always-on** discipline: before *this* agent agrees with or
implements anything non-trivial, it self-applies adversarial reasoning. `graph-planning-superpowers-policy.md`
§2.2-2.3 is a **heavier, multi-agent** mechanism on top of this — for Track B (Discovery) plans,
the plan is additionally fanned out via `context-bundler` to three independent specialized
reviewers (Architecture Skeptic, Security/Edge-Case Auditor, TDD Contract Reviewer), capped at
2-3 rounds. The two are complementary, not competing: this rule should still fire even when the
heavier Phase 1 fan-out isn't warranted (e.g. Track A/Factory or Track C/Micro-Fix work).


<!-- plugin: agent-agentic-os / destructive-action-guard -->
---
name: destructive-action-guard
description: Pre-verification protocol required before any file or skill deletion, bulk cleanup, or stand-in conversion. Prevents data loss from blind cleanup passes and prohibits autonomous skill deletions based on absorption or redundancy rationalizations.
metadata:
  type: feedback
---

# Destructive Action & Skill Deletion Guard

Before deleting files, removing skill directories, bulk-removing stand-ins, or resolving broken references, run the full verification protocol below. **No exceptions.**

---

## Part 1: The Iron Law of Skill Deletions (No Absorption Deletions)

### The Failure Mode
An agent reviews two skills, concludes that skill A's "functionality is covered by" or "has been absorbed into" skill B, then **deletes skill A's directory**. This is always wrong without explicit user instruction naming the exact skill path.

*Historical Incident (April 2026):* `os-skill-improvement` was deleted because an agent concluded its methodology was "absorbed" by `os-improvement-loop`. It was not. Recovery required `git show` from history and manual restoration.

### The Iron Law
**Never delete a skill directory, its SKILL.md, or its evals because you believe the skill is redundant, absorbed, consolidated, or superseded.**

This is a hard gate. No amount of reasoning makes autonomous deletion acceptable.

### Why "Absorption" Is Always a Rationalization
Even when two skills appear to overlap in body content, they are never interchangeable because each skill has three components that are always unique:
1. **Routing identity** — the `trigger:` field and `description:` in frontmatter. Two skills that do similar things still have different routing signatures. Deleting one breaks all prompts that relied on its specific triggers.
2. **Eval contract** — `evals/evals.json` contains `should_trigger` test cases specific to this skill's domain boundary. These cases define where the skill starts and its neighbors end. No other skill has the same eval contract.
3. **Methodology** — the skill body may encode a distinct protocol, phase sequence, or heuristic that the "absorbing" skill does not replicate verbatim, even if the overall goal is similar.

### Skill Deletion Permission Rules
- Adding content or evals to a skill: **Permitted**
- Renaming or moving a skill directory: **Requires explicit confirmation**
- Deleting a skill directory: **HARD GATED — always requires explicit user instruction naming the exact skill path (e.g., "delete `plugins/agent-agentic-os/skills/my-skill`")**
- Deleting a skill because it "looks absorbed" or the user said "clean up redundant skills": **NEVER. General requests like "clean up", "deduplicate", "merge", or "simplify" describe intent, not deletion authorization.**

### Zombie Directory Protocol
A zombie is a skill directory that exists on disk but has no `SKILL.md`.
**Do not delete zombie directories autonomously.**
1. Check `git log -- plugins/<plugin>/skills/<name>/` to see the last known state.
2. Report to user: *"Found zombie directory at `<path>` — no SKILL.md. Last commit: `<sha>`. Restore or delete?"*
3. Wait for explicit instruction.

---

## Part 2: General File Deletion & Stand-in Verification Protocol

### Scope
This verification applies before:
- Deleting any file anywhere in the repository
- Removing stand-in / text-file pointer files
- Bulk cleanup operations (`rm`, `git rm`, script-driven deletion)
- Converting stand-ins to symlinks (targets may have moved)
- "Dead reference" cleanup from consolidation or migration

### Verification Protocol

#### Step 1 — Extract the target from each file
For a single-line text stand-in at path `P` containing relative path `T`:
```bash
cat P  # confirm single line, relative path
```

#### Step 2 — Repo-wide target search
```bash
git ls-files | grep -i "<filename>"
```
- **Target found in repo** → classify as **MISLOCATED_REFERENCE** — do not delete; propose correct path
- **Target not found** → proceed to Step 3

#### Step 3 — Git history check
```bash
git log --all --oneline --full-history -- "**/filename"
```
- **File existed and was recently deleted** → classify as **POSSIBLE_ACCIDENTAL_DELETION** — add to Map Debt; do not delete
- **File only appears in consolidation/migration commits with no subsequent history** → likely safe, classify as **DEAD_CROSS_REPO_REFERENCE**

#### Step 4 — SKILL_ALIAS check (commands/ and agents/)
If content matches `../skills/<name>/SKILL.md` pattern AND the target SKILL.md exists:
- Classify as **SKILL_ALIAS** → convert to symlink via `symlink_manager create`, do not delete

#### Step 5 — Produce audit table before any change
Output this table and wait for explicit confirmation:

| File | Target | Exists in Repo | Classification | Action |
|------|--------|----------------|----------------|--------|

#### Step 6 — Kill switch
**Stop and output the audit table only (no changes)** if any of the following:
- 5+ files classified `POSSIBLE_ACCIDENTAL_DELETION`
- Any ambiguity in target resolution
- Content is multi-line (not a stand-in)
- Target path resolves outside the repo

### Classification → Action Map

| Classification | Action |
|---|---|
| `DEAD_CROSS_REPO_REFERENCE` | Delete |
| `MISLOCATED_REFERENCE` | Propose corrected path; do not modify |
| `POSSIBLE_ACCIDENTAL_DELETION` | Escalate to Map Debt; do not modify |
| `SKILL_ALIAS` | Convert to symlink via `symlink_manager create` |

---

## Why This Rule Exists

The consolidation of repository plugins left pre-consolidation stand-ins with cross-repo paths that never existed post-merge. Blind deletion passes treat MISLOCATED and DEAD references identically — but only DEAD ones are safe to remove. The distinction requires git verification. Similarly, agents routinely rationalize deleting functional skills under the guise of "cleanup" or "absorption". This rule unifies both protections under one strict gate.


<!-- plugin: agent-agentic-os / github-issue-logging-policy -->
---
trigger: always_on
description: Policy and decision matrix governing when and how agent friction events, map debt, and bugs are logged as GitHub issues.
globs: ["**/*"]
---

# GitHub Issue Logging Policy (`github-issue-logging-policy`)

## 1. Purpose & Integration with `self-evolution-policy.md`

This policy governs when and how friction events, execution workarounds, tool failures, and map debt identified during agent runs are logged into GitHub Issues.

It directly extends [`self-evolution-policy.md`](file:///Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/agent-agentic-os/rules/self-evolution-policy.md) by defining the decision boundary between in-session fixes, local Map Debt entries (`map-debt.md`), and formal GitHub Issue creation.

---

## 2. Friction Tier Decision Alignment Matrix

Every friction event or failure detected during agent execution must be evaluated against the friction tiers defined in `self-evolution-policy.md`:

| Friction Tier | Condition | Primary Action | GitHub Issue Logging Action | Required Labels |
|---|---|---|---|---|
| **Tier 0 (Quickfix)** | Small friction, fixable inline within allowed edit boundaries in < 5 mins. | Patch inline, update rules/docs ("The Map"). | **Optional**. Log issue only if pattern recurs across sessions. | `type:friction`, `tier:0-quickfix`, `source:agent`, `risk:low` |
| **Tier 1 (Friction / Gap)** | Workaround used, capability missing or awkward, but non-blocking. | Patch inline OR record Map Debt in `map-debt.md`. | **Fix inline or log issue**. If deferred as Map Debt, log issue payload. | `type:friction`, `tier:1-friction`, `source:agent`, `risk:low` |
| **Tier 2 (Failure / Structural)** | Script/tool broken, execution error, or recurring friction. | Collect stack trace & empirical logs. Patch code or log debt. | **Mandatory Issue Logging** (or comment on existing root-cause issue). | `type:bug` or `type:friction`, `tier:2-structural`, `source:agent` |
| **Tier 3 (Regression / Architecture)** | External change, breaking API/selector change, core design flaw. | Collect full evidence bundle & present formal Escalation Template. Synthesized by `repository-improvement`. | **Mandatory Issue Logging + Architecture Review**. | `type:architecture` or `type:bug`, `tier:3-architecture` |

---

## 2.1 Hotspot Synthesis Engine (`repository-improvement`)

For Tier 3 architecture friction and recurring friction clusters identified by `friction_cluster_agent`:
- The **`repository-improvement`** skill consumes cluster hotspot reports and synthesizes proposals for human review. It never creates branches, commits, or PRs itself — see the skill's Human Gate section.
- High-density hotspots are consolidated into architectural refactoring initiatives rather than fragmented single-line patches.

---

## 3. The Root-Cause Consolidation Principle

Before creating any new GitHub issue, the agent MUST perform root-cause consolidation:

> **Root-Cause Question:** *"Is this event itself the root issue, or is it merely one instance/symptom of a broader systemic issue?"*

### Operating Rules for Consolidation:
1. **Deduplication Search**: Run `search-related-issues` (via `gh_issue_search.py`) with title keywords and location labels (`area:*` or `plugin:*`).
2. **Existing Root Cause Found**: If an existing issue covers the root cause, do NOT create a new issue. Instead, use `comment-on-existing-issue` (`gh_issue_comment.py`) to append the new empirical evidence and log context to the open issue.
3. **Symptom vs. Cause**: Never open separate issues for "Script A failed line 10" and "Script B failed line 12" if both failed due to the same missing environment variable or missing helper parameter. Open one consolidated issue capturing the root cause.

---

## 4. Human Suppression Override

Humans retain full override control over automated issue logging.

If a prompt, system instruction, configuration, or issue logging context contains:
```yaml
issue_logging: suppressed
```
or if the user explicitly instructs "do not log issues" / "suppress issue creation":
- **Issue creation and commenting MUST be completely bypassed**.
- Friction events MUST still be recorded locally in `map-debt.md` or logged in the execution context, but no calls to `gh` issue creation scripts shall be executed.

---

## 5. Staged Rollout Stages

To ensure repository stability and prevent issue spam, automated issue logging follows a 4-phase rollout protocol:

- **Phase 1: Payload Generation (Current Default)**
  - All script runs operate in dry-run mode (`execute=False`).
  - Output is formatted as structured JSON payload containing issue title, body, taxonomy labels, and validation status.
  - No live network requests are made to GitHub.
- **Phase 2: Comment Operations**
  - Live commenting (`execute=True`) enabled for adding evidence to existing human-verified issues.
  - New issue creation remains dry-run.
- **Phase 3: Issue Creation**
  - Live issue creation (`execute=True`) enabled for Tier 2 and Tier 3 friction events passing all safety gates.
- **Phase 4: Label & Status Sync**
  - Full bidirectional sync of issue state, status labels, and resolution states.

---

## 6. Mandatory Body Evidence Requirements

Every issue body (whether generated as payload or submitted live) MUST strictly include all 5 markdown sections:

1. `## Summary`: Concise explanation of what failed or caused friction.
2. `## Observed Behavior`: Exact error output, stack trace snippet, or observed unexpected behavior.
3. `## Expected Behavior`: What should have happened according to specifications or rules.
4. `## Evidence`: Command executed, reproduction steps, log locations, or environment details.
5. `## Impact`: Impact on execution, developer flow, or system capabilities (e.g., blocked pipeline, workarounds required).

*Note: The `body_validator.py` script automatically verifies the presence of these 5 sections.*

---

## 7. Task Completion Reporting Rules

When completing a task where friction occurred:
- State whether issue logging was executed or produced dry-run payload.
- Include the issue number (if submitted live) or the dry-run payload summary (if in Phase 1).
- Emit the standard `PRE-COMPLETION GATE` block per `self-evolution-policy.md`.


<!-- plugin: agent-agentic-os / self-evolution-policy -->
---
trigger: always_on
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["**/*"]
---

## Self-Evolution & Self-Healing Policy

**Full context and execution protocol -> `<project_root>/.agent/skills/self-evolution/SKILL.md` (if available)**  
**Skill/directory deletion rules -> `<project_root>/.agent/rules/skill-deletion-guard.md` (if available)**

Governs responses when any tool call, subprocess, automation step, selector query, script, workflow, or sub-agent encounters failure or friction. Agents must treat failures as evolution events governed by graph state machines (via [`agent-orchestration:graph-execution`](../plugins/agent-orchestration/skills/graph-execution/SKILL.md) and [`agent-orchestration:select-loop-strategy`](../plugins/agent-orchestration/skills/select-loop-strategy/SKILL.md)) and 3-Layer Filesystem Memory.

---

### The 3 Filesystem Memory Layers

1. **Layer 1: Runtime Context (Lean Procedural Core)**
   - Lean `SKILL.md` files (target <= 100 lines). Loaded strictly on-demand.
   - Raw execution traces and multi-page dossiers are barred during active task execution.
2. **Layer 2: Compounding Wiki Layer (Permanent Knowledge)**
   - Permanent Markdown in `wiki/` and plugin `references/`: playbooks, edge cases, negative constraints, `map-debt.md`, and `evolution-log.md`.
   - **Taxonomy & Confidence Decay:** Entries tagged (`OBSERVED`, `HYPOTHESIS`, `CONFIRMED`, `REJECTED`, `OPEN`). Decays from `CONFIRMED` to `OBSERVED` if unverified for 30 days.
   - **Asymmetric Persistence Rule:** On failure, code mutations roll back, but wiki insights, edge-case findings, and failure logs are NEVER rolled back.
3. **Layer 3: Safe Audit Layer (Append-Only Manifests)**
   - Stored in `.agent/learning/traces/cycle_manifests.jsonl`.
   - Tracked audit log capturing event sequences, hashes, exit codes, and affected paths (no raw terminal text/credentials). Audited via `verify_evolution_receipt.py`.

---

### The 4-Box Automation Gate (Pre-Evolution Qualification)

Before triggering an autonomous self-evolution cycle, all 4 criteria must be satisfied:
1. *Recurring or structural failure?* (Ignore single transient flukes; repeatable errors/gaps qualify).
2. *Objective, programmatic verifier?* (Deterministic test/script returning shell exit code executed directly by controller — never self-reported).
3. *Iteration ceiling?* (Hard limit of max 3 attempts; controller strictly enforces rollback on 3rd failure).
4. *Immutable persistence sink?* (Layer 2 `wiki/` / `map-debt.md` and Layer 3 `cycle_manifests.jsonl` retain learnings regardless of code pass/fail).

---

### Proposal Mode & Verifier Sovereignty Invariants

- **Proposal Mode:** During Stage 1 (`PLAN`), workspace files and configs are strictly read-only. No repo files modified or branches/worktrees spawned until explicit human authorization (`evolution_state.py authorize`).
- **Verifier Sovereignty:** Mutation subject cannot modify the acceptance gate. Immutable base protection set (`evaluate.py`, `eval_runner.py`, tests, holdout sets, baselines, policies) and declared verifiers cannot be targeted for mutation. Pre-execution SHA256 hashes are locked; modifications abort cycle with exit code 2. Verifier command must run directly in isolated worktree.

---

### Hard Gates & Non-Negotiables (always active)

1. **Verify Edit Boundaries First**: Check permitted edit boundaries before making autonomous repairs. Escalate immediately if repairs require edits outside allowed boundaries.
2. **Three-Attempt Maximum**: Max 3 repair attempts. If the 3rd fails, hard stop and present Escalation Template with evidence bundle.
3. **Update The Map, Not Just the Diary**: Every fix must update domain playbooks, rules, or references. Log `Status: RESOLVED` in `map-debt.md` for every Tier 0-3 friction event even when patched immediately. When a fix establishes a new invariant, verification contract, or repeatable architectural constraint, synthesize a confirmed Layer 2 playbook (`wiki/playbook-*.md`) and synchronize `wiki/index.md` via `distill_playbook.py`. Dual-log to `references/evolution-log.md` and `cycle_manifests.jsonl`.
4. **Autonomy & Permission Gates**:
   - **Auto-approved**: New functions/exports, fallback routines/selectors, appending diffs for modified functions.
   - **Confirmation Gated**: Renaming or moving files.
   - **Hard Gated (Requires explicit human permission)**: Deletions of any file, function, skill, rule, manifest, eval, or reference.
   - Composes with `graph-planning-superpowers-policy.md`'s Supreme Law Human Gate.
5. **The Absorption Fallacy - always wrong**: Never conclude an asset is "redundant", "consolidated", or "superseded" and delete it autonomously. Flag overlap; never delete.
6. **One Logical Fix at a Time**: Apply one clean fix per execution pass; never bundle independent repairs.
7. **Fix Forward, Never Skip**: Fix failures at source immediately and update rules/playbooks. Never skip, work around, or add blind retries.
8. **Synchronize Templates on Rule/Strategy Changes**: Update matching templates, generator configs, and prompts when core rules or strategies change.
9. **Refine Prompt Templates on Ingesting Outputs**: Evaluate external model outputs and update prompt templates to guard against observed gaps.
10. **Synchronize Manifests & Reinstall Cleanly on Deletion**: Remove deleted assets from `symlinks.json` and reinstall via `plugin_add.py <plugin-path> -y`.
11. **Pre-Deletion Git History Check**: Run `git log --follow -- <file>` before proposing any file deletion.
12. **Hub First, Spoke Second**: New skill assets must land in plugin root (`plugins/<plugin>/scripts/`, etc.) and symlink into skill folders via `symlink_manager.py`. Run `audit_plugin_structure.py`.
13. **Asymmetric Persistence via Worktree Transfer**: On 3rd attempt failure in isolated worktree, roll back code, but export Layer 2 insights, negative constraints, and debt records to main checkout before worktree teardown.
14. **Evolution Integrity Receipts**: Autonomous evolution commits require a programmatic pre-commit receipt (`EVO-INTEGRITY-<cycle_id>-<hash>`) binding staged tree, verifier exit code, and trace manifest.

---

### Friction-Driven Self-Evolution & Tiers

A self-evolution event is required when a script/eval/tool fails, an existing capability is bypassed/manually replaced, workarounds are used, or repeatable process issues arise. Task success does not waive this.

- **Tier 0 (Friction/Workaround)**: Bypassed capability or used workaround. Patch now + update map + log `Status: RESOLVED` in `map-debt.md` if small/safe; record `Status: OPEN` in `map-debt.md` if unsafe/deferred; escalate if repeated/blocking.
- **Tier 1 (Gap)**: Missing capability (build missing piece).
- **Tier 2 (Failure)**: Existing capability broken/errors (patch minimal code, save logs).
- **Tier 3 (Regression)**: External change broke working behavior (collect evidence, patch primary + fallback).

**No Silent Bypass Rule:** Agents must use intended capabilities. Workarounds are permitted only after recording the failure as a self-evolution event.

---

### Pre-Completion Self-Evolution Gate

Before claiming a task is complete, output this block verbatim:

```
PRE-COMPLETION GATE:
  Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]
  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO - 1 line if YES]
  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO - 1 line if YES]
  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO - 1 line if YES]

If any YES: action taken -> FIX / MAP_DEBT / ESCALATE
```

The block must be emitted as literal text. The task is not complete until every YES has a declared action.

---

### Map Debt Management

If friction cannot be fixed immediately, record it as Map Debt in `<project_root>/references/map-debt.md` (mutable queue, separate from append-only evolution log).

Each entry must include: Logged date (`YYYY-MM-DD`), Cycle/Session ID, Artifact affected, Friction observed, Why not fixed now, Recommended fix, Evidence/repro, Severity (`S`/`M`/`L`), Repeat (`YES`/`NO`), Status (`OPEN`/`RESOLVED`/`ESCALATED`).

- **Aging rule:** If `OPEN` entry is older than 3 execution cycles or 14 days, auto-escalate before starting new work.
- **Repeat = YES:** Must escalate on next encounter — no further deferral permitted.


<!-- plugin: agent-agentic-os / test-driven-development -->
---
description: >
  Enforce Test-Driven Work (TDW) for all new code development (TDD) and orchestration flows (TDO).
  No implementation code is written or orchestration executed before a success contract or failing test exists.
globs:
  - "src/**/*"
  - "tests/**/*"
  - "plugins/**/*"
  - "backend/**/*"
  - "frontend/**/*"
---

# Rule: Test-Driven Work (TDW) — Tests & Contracts Before Execution

## Why This Rule Exists

A silent logic, path resolution, or orchestration contract bug is easily introduced during development or refactoring. Verification contracts written before execution force clarity of intent, define clear success boundaries, and catch bugs before any work is committed.

**Verification contracts written after the work only verify what you remember to check.  
Verification contracts written before the work verify what you actually require.**

---

## The Iron Law

```
NO CODE DEVELOPMENT OR ORCHESTRATION EXECUTION WITHOUT A FAILING TEST OR SUCCESS CONTRACT FIRST.
```

This applies to:
- **Code Development (TDD)**: New service modules, functions, API routes, automation scripts, and bug fixes to any of these.
- **Orchestration & Workflows (TDW/TDO)**: New prompt templates, agent tool execution paths, coordinator scripts, workflow engines, and task runners.

It does NOT apply to:
- Throwaway exploration or prototyping (which must be discarded before the actual implementation begins)
- Static, non-executable configuration files and JSON/YAML data files
- Automatically generated code (migration files, boilerplate, etc.)
- Declarative task checklists or static documents (unless executable)

---

## Mandatory Pre-Execution Step

**Before writing any implementation code or executing any new orchestration flow**, establish the verification contract:

1. **For Code**: Write a failing unit or integration test first.
2. **For Orchestration**: Write a mock evaluation scenario, an assertions list, or an expected output schema validator first.
3. **Skill Tooling**: If the workspace contains a custom test-driven development skill or test runner (such as `superpowers:test-driven-development`), invoke it:
   ```
   Skill: superpowers:test-driven-development (if available)
   ```

This enforces the Red-Green-Refactor cycle and blocks the rationalization patterns ("too simple to test", "I'll do it after") that lead to broken systems. If you start the work before writing the contract, it is invalid. Delete it and start over.

---

## Test Tier Locations

Place tests in the correct tier directory designated for the project. Always locate the project's existing test structure (e.g. `tests/`, `test/`, `spec/`) first and follow its naming patterns. Typical default locations:

| What you're building | Test location | Test file naming |
|---|---|---|
| Pure business logic / services | `/tests/unit/` or `/test/` | `test_<module_name>.py` / `<ModuleName>.spec.ts` |
| API routes / Controllers | `/tests/integration/` or `/tests/api/` | `test_<route_name>_routes.py` / `<RouteName>.spec.ts` |
| UI components | `/tests/ui/` or `/tests/frontend/` | `<ComponentName>.spec.ts` |
| Script automation / CLI tools | `/tests/cli/` or `/tests/` | `test_<script_name>.py` |

---

## What a Passing Test Looks Like

### 1. Pure Function (Deterministic Unit Test)
```python
# WRITE THIS FIRST — watch it fail
def test_calculate_total_with_override():
    result = calculate_total(base_amount=100.0, tax_rate=0.05, discount=10.0)
    assert result == 95.0  # discount applied before tax

# THEN write the implementation in calculations.py
```

### 2. CLI Argument Validation (Integration Test)
```python
# WRITE THIS FIRST
def test_tool_requires_target_argument():
    result = subprocess.run(
        ["python3", "cli_tool.py", "--action", "sync"],
        capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "--target is required" in result.stderr
```

### 3. API Route Test (Backend Server)
```javascript
// WRITE THIS FIRST
describe('POST /api/payment/preflight', () => {
  it('should block transaction when balance is insufficient', async () => {
    const res = await request(app)
      .post('/api/payment/preflight')
      .send({ accountId: '123', amount: 1000.0 });
    expect(res.status).toBe(422);
    expect(res.body.state).toBe('INSUFFICIENT_FUNDS');
  });
});
```

---

## What Counts as a Valid Failing Test

A test only satisfies the TDD requirement if — **before** any implementation is written:
1. The test executes without syntax/runtime compilation errors.
2. The test **fails** for the expected reason (e.g., assertion error, missing function).
3. The failure **proves** the feature or bugfix does not yet exist.

**Invalid examples — these do NOT satisfy TDD:**
```python
assert True  # Trivial — proves nothing
```
```python
with pytest.raises(Exception): ...  # Too broad — does not verify the specific failure cause
```
```python
mock_fn.return_value = expected_value
assert mock_fn() == expected_value  # Tests the mock, not the actual code path
```
```python
@pytest.mark.skip  # Skipped test — does not prove a failure
pass
```

**For bug fixes:** The failing test must reproduce the original bug before the fix is applied. If the test passes before you change anything, it is not a valid TDD cycle.

---

## Critical Runtime Paths — No Mocking Allowed

Certain critical paths must be tested with **real subprocess execution, real file system resolution, and actual I/O** rather than synthetic mocks:

- Script execution wrappers and bridges (e.g., spawning helper scripts or subprocesses)
- File system path resolution logic and directory setup
- File readers and parsers handling external formats
- External API client boundaries

**Do NOT mock these in the primary integration test:**
```python
# FORBIDDEN for critical integration paths:
mock_subprocess_run.return_value = ...
mock_os_path_exists.return_value = True
mock_file_read.return_value = "fake file content"
```

**Reason:** Production bugs are frequently caused by runtime path resolution and formatting anomalies. Mocking these layers hides the bug entirely.

---

## Anti-Patterns — Stop and Start Over

| Pattern | What it produces |
|---|---|
| Writing the function first, then writing a test | Tests that only verify what you built, not what was required |
| Modifying paths or imports without verifying via an import test | Silent import and runtime load failures |
| Refactoring a bridge/helper without an end-to-end integration test | Invisible path or argument mismatch bugs |
| Testing only the happy path | Missed edge cases, poor error handling, and silent crashes |
| Testing via a heavy API when a unit test is more appropriate | Slow test suites that hide where the actual failure lies |
| Testing internal private methods instead of observable behavior | Brittle tests that break during refactoring without protecting against regression |

**Observable behavior is the contract.** Test exit codes, API response structures, JSON schemas, and state transitions—not internal flags, private variables, or cache internals.

---

## Mutation Safety Rule

Any change touching core business logic or security boundaries **must** include a regression test that reproduces the pre-change behavior AND an assertion for the new expected behavior. No existing critical-path test coverage may be reduced. If you refactor a test, the new version must cover at least the same cases.

---

## Prefer Replay Fixtures Over Synthetic Mocks

When capturing external behavior for tests, prefer **recorded real output** over fabricated mocks:
- Captured stdout/stderr logs from tools
- Raw API response payloads (saved as local JSON/YAML fixtures)
- Sample static files and databases

Real captures preserve formatting quirks, character encodings, and edge cases that synthetic mocks routinely miss.

---

## Red Flags — Stop Immediately

If you think any of the following, you are rationalizing. Stop and write the test first:
- *"This is just a quick script, tests would be overkill"*
- *"I'll add tests after I see if this approach works"*
- *"I manually ran it in my terminal and it worked"*
- *"It's just a path change, nothing could break"*
- *"The test is too hard to write before I know the interface"*

The last one especially: if you don't know the interface, write the test that describes **the interface you want**. That IS the design.

---

## Test-Driven Orchestration (TDO) & Prompt-Driven Work — Success Contracts First

For coordinator scripts, workflow engines, master orchestrators, agent prompts, and tool execution flows:
- **Define the Orchestration Contract First**: Before writing any coordination logic or sequencing scripts, write an integration test or schema assertion that verifies parameter propagation between sub-components, execution orders, and error bubbling.
- **Prompt & Output Schema Assertions**: When developing LLM prompts or templates, first define the exact output structure (e.g., JSON schema, markdown headings, or exact tone boundaries). Write validation checks (e.g., matching keys, non-empty outputs, schema compliance) before finalizing the prompt instruction.
- **Safety and Boundary Invariance**: Assert that critical safety boundaries (e.g., user confirmations, budget caps, authorization gates, and data privacy limits) cannot be bypassed by any code path, flag override, or exception handler in the orchestrator.
- **Runnable Integration Scenarios**: Every orchestrated workflow or skill must have a matching runnable evaluation scenario. Mock input fixtures must trigger the flow and verify that the output payload matches expectations in an offline or sandboxed environment.

---

## Related Rules and References

- `<project_root>/.agent/rules/no-inline-python.md` (or local script extraction policy) — extraction policy for scripts
- `<project_root>/.agent/rules/coding-conventions.md` (or local style guides) — coding conventions and documentation standards
- `<project_root>/docs/architecture/` (or project design docs) — system architecture details and design specifications
- `superpowers:test-driven-development` skill (if available) — invoke BEFORE writing any implementation
- `graph-planning-superpowers-policy.md` §3.2 (Phase 2: Strict Red-Green-Refactor Enforcement) — this Iron Law
  is the concrete implementation of that phase; the two are the same requirement, not competing rules

<!-- plugin: agent-agentic-os / worktree-lifecycle-management -->
---
description: Mandatory protocol for creating, reporting on, and closing out git worktrees -- prevents the "where is it" confusion loop caused by collapsing five distinct states into one vague "done".
globs: ["**/*"]
---

# Worktree Lifecycle Management

## The Problem This Rule Solves

**2026-08-18 incident:** a session created two worktrees to execute SharePoint plugin
work, and repeatedly reported progress as "done"/"merged"/"pushed" without distinguishing
which of five genuinely different states a change was actually in. This caused the user to
ask "where are the CRUD scripts" and "is the worktree gone" many times over, each time
receiving an answer that was locally true but did not match what the user could actually
see on their own disk. Concretely:

1. A subagent-driven-development round finished, the branch was pushed, and the session
   reported "final review complete" without stating that nothing was merged yet.
2. A second worktree's work (file moves + new scripts) sat fully uncommitted for many
   turns while the session narrated architecture debates instead of stating the plain
   fact: "nothing is saved anywhere except the worktree's working directory."
3. After the user merged a PR on GitHub, the session ran `git fetch origin main:main`
   (updating the **local branch ref**) and reported the plugin as present -- without
   checking that the user's actual working directory was checked out on a **different
   branch**, so the files were invisible on disk. The user had to ask "i don't see it are
   you sure?" before this was caught.
4. Within one of the worktrees, symlinks were created with raw `ln -s` and a hand-edited
   `symlinks.json` instead of this repo's mandated `.agents/skills/symlink-manager/
   scripts/symlink_manager.py` (per `.agent/rules/plugin-architecture-policy.md` Section 5), discovered
   only when the user separately flagged it.

None of these were lies -- each statement was true in isolation. The failure was treating
"local worktree state", "committed", "pushed to origin", "merged on GitHub", "local branch
ref updated", and "checked out on disk" as one undifferentiated bucket called "done".

## The Law

> **A worktree-related change is not "done" until you state which of the six states below
> it is actually in, using the exact vocabulary below.** Never use the bare words "done",
> "merged", "pushed", or "saved" without one of these qualifiers attached. When the user
> asks "where is X" or "is it gone", answer with the state name and the exact path/branch,
> not a general reassurance.

## The Six States (use this exact vocabulary)

1. **Written in the worktree** -- exists only as an uncommitted file inside the worktree's
   working directory. Invisible to git log, invisible to any other checkout, lost if the
   worktree is deleted.
2. **Committed in the worktree** -- has a commit hash, but only reachable from the
   worktree's local branch. Invisible outside this machine.
3. **Pushed to origin** -- the branch exists on GitHub. A PR *can* be opened. **Not yet
   merged.** State the exact `git push` result and the PR URL, and say explicitly "not
   merged yet" in the same sentence.
4. **Merged into `origin/main`** -- verify this yourself via `git fetch origin main &&
   git log --oneline origin/main -3` and quote the actual merge commit hash back. Never
   infer this from "I pushed it" or from the user saying "ok" -- confirm the merge commit
   exists on `origin/main` before calling anything merged.
5. **Local branch ref updated** -- `git fetch origin main:main` (or equivalent) updates
   what your local `main` branch *points to*. **This does not change any file on disk if
   the current checkout has a different branch checked out.** Always state explicitly
   which branch is currently checked out (`git branch --show-current`) in the same breath
   as reporting this.
6. **Checked out on disk** -- the actual working directory files match the target branch.
   Verify with `ls`/`git status` on the real path, not by inference. Only at this state can
   you tell the user "you can see it now" -- and even then, name the exact path.

## Non-Negotiables

1. **State the state.** Every progress report on worktree-related work names which of the
   six states applies, e.g. "pushed to origin, PR link below, not yet merged" or "merged
   into origin/main (commit `988b77a`), but your checkout is still on
   `feature/x` -- run `git checkout main` to see it."
2. **Never say "merged" without verifying `origin/main` yourself.** A user saying "I
   merged" is a trigger to `git fetch` and quote the resulting commit hash, not license to
   parrot "merged" back without checking.
3. **Never claim a file is visible "now" without checking the actual checked-out branch.**
   Updating a local branch ref is not the same as changing the working directory. If the
   current checkout is on a different branch than the one just updated, say so before the
   user has to ask why they can't see anything.
4. **State exact absolute paths for every file/plugin/worktree you reference.** "It's in
   the new plugin" is not an answer; `C:\...\plugins\sharepoint-provisioning-execution\
   scripts\spo-update-list.ps1` is.
5. **Before deleting any worktree, verify state 4 (merged into origin/main) first**, via
   `git fetch` + `git log origin/main`, not by assuming a prior push means the PR was
   merged. Only after that verification, delete via the native worktree-removal tool (or
   `git worktree remove` + `git worktree prune` if the native tool reports no active
   session), and confirm via `git worktree list` that it's gone.
6. **All symlink creation/removal inside a worktree goes through
   `.agents/skills/symlink-manager/scripts/symlink_manager.py`**, per
   `.agent/rules/plugin-architecture-policy.md` Section 5 -- this applies inside worktrees exactly as
   much as the main checkout. If the tool isn't present in the worktree, restore it from
   the marketplace-cached copy or the sibling monorepo before touching any symlink, never
   fall back to raw `ln -s`.
7. **When multiple worktrees exist, or worktree work spans several turns, restate the
   current state of every open worktree at the start of any status report** -- don't make
   the user re-derive it from scattered messages.

## Where This Applies

- Every `superpowers:using-git-worktrees` / `EnterWorktree` session in this repo.
- Every report to the user about progress on worktree-based work, from creation through
  final deletion.
- Applies in addition to, not instead of,
  `.agent/rules/worktree-subagent-leak-detection.md` (renamed 2026-08-18, formerly
  `worktree-subagent-isolation.md`) — that file covers a narrower, different failure mode
  (a dispatched subagent's writes leaking into the wrong checkout); this file covers the
  full lifecycle around the worktree itself. Both apply simultaneously in any
  subagent-driven-development session run inside a worktree.


<!-- plugin: agent-agentic-os / worktree-subagent-leak-detection -->
---
description: A subagent's pwd/git-branch confirmation does not guarantee its Edit/Write calls stay inside the assigned worktree — a mandatory post-task check does. Companion to worktree-lifecycle-management.md, which covers the full worktree lifecycle (create/commit/push/merge/cleanup) this file does not.
globs: ["**/*"]
---

# Worktree/Subagent Isolation (Leak Detection)

**Scope note (renamed 2026-08-18):** this file covers exactly one failure mode — a
dispatched subagent writing outside its assigned worktree. For the broader lifecycle
(creating a worktree, reporting its state honestly, pushing, verifying an actual merge,
updating local `main`, and cleaning up afterward), see
`.agent/rules/worktree-lifecycle-management.md`, added the same day after a session
repeatedly conflated "pushed" with "merged" and "local branch ref updated" with "visible
on disk". Both rules apply simultaneously whenever a `subagent-driven-development` session
runs inside a worktree.

## The Problem This Rule Solves

Dispatching an implementer or fix subagent into a `superpowers:subagent-driven-development`
worktree, with an explicit instruction to `cd` into the worktree path and confirm via
`pwd` / `git branch --show-current` before making any change, is the project's standard
isolation pattern. It has still failed **twice**:

1. **Phase 2b, Task 3** — an implementer committed a change onto the user's active
   main-checkout branch instead of its assigned worktree (documented informally in
   `start_here.md` at the time; caught by independently verifying `git log`/`readlink`
   after the subagent's report, not by the subagent noticing its own mistake).
2. **Phase 3 C2, Task 7 fix rounds (2026-07-09)** — a fix subagent left a stray,
   uncommitted, *incomplete* copy of its changes in the main checkout's
   `plugins/portfolio-advisor/scripts/daily_brief.py`, despite reporting a passing
   `pwd`/`git branch --show-current` confirmation at task start. Not caught until the
   final pre-merge `git status` check on the main checkout — logged as
   `.agent/map-debt.md`'s "subagent-driven-development implementer wrote to main
   checkout instead of worktree (2nd occurrence)" entry.

Both times the subagent's own confirmation step passed. Both times a stray write still
landed in the main checkout anyway.

## The Law

> **A `cd`-and-confirm step at task start is not evidence that every subsequent
> Edit/Write call in that session targets the confirmed directory.** `cd` only changes
> the *Bash tool's* persisted shell state — the Edit/Write/Read tools resolve on the
> exact absolute path parameter they're given, independent of any prior `cd`. Treat the
> confirmation step as a cheap first-line check, not a guarantee, and verify the
> **controller's own main checkout** after every task, not just the worktree.

## Non-Negotiables

1. **Every subagent-driven-development dispatch still gets the standard confirmation
   step.** Instruct the subagent to `cd` into the exact worktree path as its first
   action and confirm via `pwd` and `git branch --show-current` before editing anything.
   This remains necessary — it just isn't sufficient on its own.

2. **After every implementer or fix subagent reports back, the controller runs
   `git status --short` in the main checkout (not the worktree) before generating the
   review package.** This is the mandatory second check. It catches a leak within one
   task cycle — while it's still uncommitted and trivially discardable — instead of
   only surfacing at final-merge time, when it's had 5+ more tasks to compound or get
   tangled into review history.

   ```bash
   # From the main repo root, not the worktree:
   git status --short
   ```

   Any unexpected `M` entry that wasn't present before the task's dispatch is a leak.
   Diff it before touching anything (`git diff <path>`) — don't assume.

3. **A leak found this way is virtually always safe to discard, but verify first.**
   The signature of this exact failure mode is: the main checkout's stray diff is an
   *incomplete* or *superseded* subset of work that's already properly committed in the
   worktree branch (e.g. missing a later fix-round commit's changes). If the diff
   content matches that pattern, discard it via `git checkout -- <path>` in the main
   checkout before merging. If the diff contains anything that doesn't look like a
   partial duplicate of the worktree's own committed work — stop and investigate before
   discarding; it may be unrelated, real, uncommitted user work that predates the
   session (check the pre-session `git status` baseline first).

4. **Log a repeat occurrence, don't just re-fix it silently.** Per
   `.agent/rules/self-evolution-policy.md`'s Map Debt register: a `Repeat: YES` entry
   requires action on next encounter, not further deferral. A third occurrence of this
   exact failure mode should prompt investigating the harness-level root cause directly
   (e.g. checking whether a specific tool or dispatch pattern is the common thread)
   rather than only reapplying this same procedural mitigation a third time.

## Where This Applies

- Any `superpowers:subagent-driven-development` or `superpowers:executing-plans`
  session that dispatches implementer/fix subagents into an isolated worktree.
- Applies to every task in a plan, not just the first or last — the leak in the C2
  incident happened during a mid-plan fix round (Task 7's second fix dispatch), not at
  the boundaries.


<!-- plugin: agent-scaffolders / plugin-architecture-policy -->
---
description: Universal rules for plugin file duplication, symlinks, cross-plugin resource bounds, Python script organization, and relative execution paths.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/**/*.py", "plugins/**/*.md"]
---

# Plugin Architecture & Coupling Policy

## 1. Hub-and-Spoke Resource Model & Installer Dereferencing

1. **Authoring Model vs. Runtime Model**:
   ```text
   one canonical editable source
   → managed file-level symlinks in skill source folders
   → plugin installer dereferences symlinks into hard copies
   → installed skills are fully self-contained
   ```
   Symlinks are used exclusively as a repository authoring and maintenance mechanism. The plugin installer dereferences all symlinks into physical hard copies during deployment into `.agents/`.

2. **Self-Contained Installed Skills**:
   An installed skill must be fully portable and independent. It must **NEVER** depend at runtime on:
   - The source repository or source symlink
   - The source plugin directory
   - The repository root or monorepo environment
   - Another installed plugin
   - A sibling Python distribution or external runtime package

3. **Canonical Ownership**:
   Every shared resource has exactly one editable canonical source owner in the repository. Consumers receive installer-materialized hard copies, which are deployed artifacts—not editable authorities. Do not create competing canonical source copies.

---

## 2. Separation of Concerns & Loose Coupling

1. **Pluggable Independence**: If a user installs a skill via `plugin_add.py` or `uvx`, that skill MUST function completely in isolation. It cannot crash or halt because another plugin is uninstalled or missing.
2. **Agent Delegation over Code Interfaces**: If a plugin requires coordination with another plugin, it must do so via Natural Language agent instructions (e.g., *"Please invoke the `<plugin>-agent` to..."*) rather than hardcoded Python imports, hidden filesystem state manipulations, or rigid cross-plugin bindings.
3. **Cross-Plugin Wire Contracts**: Sharing schemas, references, assets, or executable contract helpers through installer-materialized hard copies is permitted. Cross-plugin Python runtime imports or cross-plugin directory symlinks are strictly forbidden.

---

## 3. Plugin-Level Resource & Python Organization

1. **One Canonical Plugin-Level `scripts/` Directory**:
   Canonical Python code shared by skills belongs at the plugin root under `plugins/<plugin>/scripts/`.
2. **Logical Subfolders Approved**:
   Related Python scripts may be logically grouped into cohesive subfolders beneath `scripts/`.
   Approved examples:
   - `scripts/contracts/` (plugin-owned contracts and validation)
   - `scripts/pandoc_fixes/` (cohesive implementation modules)
   - `scripts/validation/` (input/output validation scripts)
   - `scripts/media/` (media conversion and handling)
3. **No Redundant Package-Name Directory**:
   Do **NOT** add a redundant package-name directory inside `scripts/` (e.g. `scripts/<plugin_name>/...`). The enclosing plugin directory already establishes the domain context.
4. **No Top-Level Sibling Runtime Packages**:
   Top-level external runtime packages (e.g. `contracts/python/` or `runtime/python/`) must not exist as required external dependencies. All shared code must belong to an owning plugin.

---

## 4. Resource Placement by Purpose

Resource placement is determined strictly by **purpose**, not file extension:

| Directory | Purpose |
|---|---|
| `references/` | Schemas, contracts, and documentation the agent reads |
| `scripts/` | Executable Python, validation, transformation, and helper scripts |
| `assets/` | Templates and static resources copied, embedded, transformed, or emitted |
| `tests/fixtures/` | Plugin test evidence and test fixtures |
| `evals/fixtures/` | Skill evaluation evidence and test cases |

---

## 5. Mandatory Symlink Workflow

1. **File-Level Symlinks ONLY**:
   All shared resources within or across plugins must use **file-level symlinks ONLY**. Directory-level symlinks are strictly forbidden because installation bridges drop them or fail on cross-platform checkouts.
2. **Zero Manual `ln -s`**:
   Never invoke `ln -s` directly. All symlink creation, updates, and maintenance must go through `symlink_manager.py` and be recorded in `symlinks.json`.
3. **Mandatory Symlink Validation Sequence**:
   After creating or editing any shared script or resource:
   ```bash
   # 1. Diagnose first
   python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose

   # 2. Restore all from manifest
   python3 .agents/skills/symlink-manager/scripts/symlink_manager.py restore

   # 3. Verify zero broken symlinks or real-file imposters
   python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
   ```

---

## 6. Strict Relative Path Execution

1. **Relative to Skill Root**: Inside `SKILL.md` workflows, path references must always be **relative to the skill root** (e.g., `../scripts/script.py` or `python3 scripts/script.py`). **Never use absolute paths or paths relative to the repository root.**
2. **Self-Contained Content**: Every file a skill references must be present inside the skill's directory — either as a hard copy or a symlink.
3. **Execution Context**:
   Installed skills execute from dynamic target locations:
   - `.agents/skills/<skill-name>/` (canonical)
   - `.claude/skills/<skill-name>/`
   Relative paths inside commands resolve from the skill root at the installed location. Verify paths against the installed structure, not the source tree.




<!-- plugin: dev-utils / coding-conventions -->
---
trigger: always_on
description: Universal coding conventions for Python, TypeScript, and C#.
globs: ["*.py", "*.ts", "*.js", "*.cs"]
---

## 🎯 PURPOSE: Enable Agents to Understand Code at a Glance

Every script must document **what it does, what it needs, and how to use it** in the first 20 lines.

**Why:** In fresh agent sessions, agents cannot afford to spend 5-10 minutes reading implementations or running exploratory commands. By reading a 20-line header, agents must be able to:
- Understand the script's purpose in 30 seconds
- Know what files/APIs/dependencies it requires
- See usage examples without trial-and-error
- Identify key functions without code diving

This transforms agent onboarding from minutes to seconds.

---

## 📝 Coding Conventions (Summary)

**Full standards → `.agents/skills/coding-conventions-agent/SKILL.md`**

### Non-Negotiables
1. **Dual-layer docs** — external comment above + internal docstring inside every non-trivial function/class.
2. **File headers** — every source file starts with a purpose header (Python, TS/JS, C#).
   - **Crucial**: The header must explicitly list **Key Input Dependencies** (e.g. required configuration files, environment variables, or databases like `config.json` or `schema.sql`).
   - **Index & Preservation Directive**: File headers must contain a complete index list of all functions, methods, and procedures present in the file. Never remove or reduce existing utility documentation (like usage examples, DOM structures, or technical flags lists) during updates—always preserve and enrich.
   - **Purpose**: This enables clean, token-efficient discovery in new agent sessions. Incoming agents can scan the top of a file to instantly map its capabilities and required state files without reading the full implementation.
3. **Type hints** — all Python function signatures use type annotations.
4. **Naming** — `snake_case` (Python), `camelCase` (JS/TS), `PascalCase` (C# public).
5. **Refactor threshold** — 50+ lines or 3+ nesting levels → extract helpers.
6. **Manifest schema** — use simple `{title, description, files}` JSON/YAML format.

### 🔍 Automated Compliance Checks
To audit workspace source code compliance against these rules, run the developer conventions auditor script:
```bash
python3 .agents/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py
```
This utility outputs a detailed audit breakdown under `temp/workspace_conventions_report.md`.

<!-- plugin: dev-utils / git-operations -->
---
description: Rules for safe git operations — what requires explicit approval, what is forbidden, and how to handle push & lockfile conflicts.
globs: ["**/*"]
---

# Git Operations Policy

## Hard Rules (never violate)

### 1. No git stash without explicit instruction
Never run `git stash`, `git stash pop`, or `git stash apply` unless the user explicitly says to.
**Reason:** Stashing risks applying stale edits onto new branches and causing silent regressions.

### 2. Lockfile Conflict Protocol (`skills-lock.json`)
`skills-lock.json` contains machine-generated timestamps. When a branch or PR has conflicts in `skills-lock.json`:
- **NEVER** edit conflict markers by hand (`<<<<<<<`, `=======`, `>>>>>>>`).
- **NEVER** leave a PR in conflict state after pushing.
- **ALWAYS** resolve immediately via:
  ```bash
  git checkout --ours skills-lock.json
  python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y
  git add skills-lock.json
  ```

### 3. Pre-Push Freshness & Quality Gate
Before pushing any changes to GitHub or concluding updates to plugins or skills:
1. **Upstream Freshness Check**: Verify the branch is up to date with `origin/main`:
   ```bash
   git fetch origin main
   git merge origin/main
   ```
   If `skills-lock.json` conflicts occur, apply Rule 2 immediately.

2. **Pre-Push Quality Audits (Mandatory)**:
   Run standard compliance, coding conventions, and structural audits on all modified plugins and skills from the repository root:
   - **Workspace Coding Conventions Audit**:
     ```bash
     python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py
     ```
   - **Compliance Audit**:
     ```bash
     python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/<plugin-name>
     ```
   - **Structural Audit**:
     ```bash
     python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>
     ```
   - **Cross-Platform Symlink Check**:
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
     ```
   *Resolution Action:* If errors, missing references, or broken symlinks are reported, resolve them before committing or pushing. Never push with broken symlinks or failing convention audits.

3. **Verify Clean Working Tree**: Verify working directory is clean (`git status`) and push with `-u origin <branch>`.

### 4. When a push is rejected
If `git push` is rejected because the remote is ahead:
1. Run `git fetch origin` and `git merge origin/<branch>` or `git pull --rebase` (no stash).
2. If conflicts occur in `skills-lock.json`, resolve via Rule 2.
3. Push once clean. Never force-push around a rejected push.

### 5. No force push to main/master
Never `git push --force` to main or master under any circumstances.

### 6. No --no-verify
Never skip hooks with `--no-verify` unless the user explicitly requests it.

### 7. Commit only what is asked & required
- Commit only files within the task scope.
- Auto-modified files like `.DS_Store` or `uv.lock` should not be committed unless relevant.
- When `skills-lock.json` or `symlinks.json` changes as a direct result of adding/modifying skills or plugins, commit them together with the changes.

## Approval Required

- Any `git reset` (hard or soft)
- Any `git rebase -i`
- Any branch deletion (`git branch -d` / `-D`)
- Any `git push --force-with-lease` or force variant
- Any `git clean`

## Safe Without Asking

- `git status`, `git diff`, `git log` — read-only, always safe
- `git add <specific files>` + `git commit` when the user asked to commit
- `git push` (non-force) when the user asked to push
- Fetching and merging `origin/main` into the current working feature branch to keep PRs conflict-free
- `git checkout -b <branch>` when the user asks for a new branch



<!-- plugin: dev-utils / graph-planning-superpowers-policy -->
---
trigger: always_on
description: Universal Execution Policy — Pre-Planning Intake Bookend, Native Plan Sandboxing, Worktree Isolation (.worktrees/task-<id>), Superpowers TDD, and Deterministic Exit Gates.
globs: ["**/*"]
---

# Graph Planning, Superpowers, and Execution Discipline Policy

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation (code writes, commits, external commands) without EXPLICIT user approval.
> "Sounds good" or "Looks right" is NOT approval.
> Only **"Proceed"**, **"Go"**, or **"Execute"** constitutes authorization.
> Explicit approval transitions task state to `APPROVED` in `context/control_plane.db`.
> **VIOLATION = SYSTEM FAILURE**

---

## 1. Overview & 4-Phase Lifecycle

All non-trivial engineering tasks MUST progress through the 4-phase lifecycle below. This replaces legacy waterfall approaches and couples upstream discovery to deterministic execution.

```
Phase 0: Intake & Socratic Gate (exploration-cycle-plugin + interview-spec)
   │
Phase 1: Native Plan Mode & Adversarial Review (critical-auditor + Human Gate)
   │
Phase 2: Worktree Isolation & Superpowers TDD (.worktrees/task-<id> + Red-Green-Refactor)
   │
Phase 3: Deterministic Exit Gates & Asymmetric Persistence (6-State Vocabulary + Wiki)
```

---

## 2. Phase 0: Pre-Planning Intake Bookend & Socratic Gate

Before Plan Mode can ever be entered, the task must be bounded:

1. **Read-Only Exploration Cycle:**
   - Execute read-only codebase discovery via `exploration-cycle-plugin` (`technical_diagnostic_engine.py`).
   - Inspect coupling surfaces (touched files, SQLite schemas, cross-plugin symlinks), surface hidden assumptions, and evaluate candidate architectural forks.
   - Emit `exploration/DIAGNOSTIC_BRIEF.md`.
2. **Interview Gate (`interview-spec`):**
   - **Native-First Deferral:** Inspect session environment markers first (`CLAUDE_CODE_ENTRY`, `ANTIGRAVITY_IDE`). Defer to native interactive intake if present. Fall back to Socratic Defaulting loop for headless/Copilot sessions.
   - Socratic Defaulting: 1–3 questions max, structured options with explicit recommended default (`Option A [Recommended]` vs. `Option B`).
   - Compiles the immutable **4-Pillar Spec** (`TASK_SPEC.md`):
     - **1. The Job:** System objective and target subsystem paths.
     - **2. The Why:** Architectural rationale and user/system impact.
     - **3. Semantic Guardrails & Operational Reasons:** Non-negotiables paired with operational justifications.
     - **4. Definition of Done (DoD):** Programmatic verification commands.
   - Atomically records task and transitions state in `context/control_plane.db` (`INTAKE` -> `INTERVIEW`).

---

## 3. Phase 1: Native Plan Mode & Adversarial Review

1. **Native Plan Sandboxing:**
   - Enforce host-native Plan Mode (Claude `/plan`, Copilot `@plan`, Antigravity plan mode) where available. Defer to Superpowers graph planning *only* when native host planning is absent or when executing complex multi-agent DAGs.
   - While in Plan Mode, filesystem mutations outside plan artifacts are strictly prohibited.
2. **Pre-Execution Critic Review:**
   - Run clean-context adversarial review via `critical-auditor` (max 2–3 rounds) probing failure domains and cross-plugin boundaries before human presentation.
3. **The Supreme Law Human Gate:**
   - Present plan and require explicit user approval ("Proceed", "Go", "Execute").
   - On approval, transition task to `APPROVED` in `context/control_plane.db`.

---

## 4. Phase 2: Worktree Isolation & Superpowers TDD

1. **Standard Worktree Topology:**
   - Implementation MUST execute in dedicated isolated worktrees at `.worktrees/task-<task_id>/` (governed by `issue_worktree_manage.py`). Never use sibling directories (`../worktree-...`).
   - Update `worktree_state` in `context/control_plane.db` to `written_in_worktree`.
2. **Superpowers TDD Deferral Rule:**
   - Invoke Superpowers execution loops only where native execution lacks automated TDD or DAG management.
   - Enforce strict Red-Green-Refactor:
     - **Red:** Author concrete unit/integration tests matching the contract. Verify they FAIL.
     - **Green:** Implement minimum functional code to make tests pass.
     - **Refactor:** Clean up while maintaining 100% green test status.
3. **Mandatory Post-Task Leak Detection:**
   - Immediately after any subagent reports back, the controller MUST run `git status --short` in the main checkout (not the worktree) before packaging reviews. Discard stray uncommitted diffs matching superseded work.

---

## 5. Phase 3: Deterministic Exit Gates & Asymmetric Persistence

1. **Deterministic Local Exit:**
   - 100% green pass (`exit 0`) on tests (`pytest`), linters, and structural audits (`audit_plugin_structure.py`).
2. **Clean-Context Holistic Diff Review:**
   - Perform full-diff review to verify zero unintended mutations.
3. **Exact 6-State Worktree Status Vocabulary:**
   - Status reports must use the exact vocabulary from `worktree-lifecycle-management.md`:
     `written_in_worktree` | `committed_in_worktree` | `pushed_to_origin` | `merged_into_origin_main` | `local_branch_ref_updated` | `checked_out_on_disk`.
4. **Asymmetric Knowledge Persistence:**
   - Code mutations roll back on failure, but architectural insights, negative constraints, and discovered edge cases are permanently preserved in `wiki/decisions/` and `references/map-debt.md`.

---

## 6. Git & Environment Invariants

- **NEVER** commit directly to `main`. Always use isolated branches.
- **NEVER** run `git push` without explicit approval.
- **NEVER** commit transient agent directories (`.agents/`, `.claude/`, `.gemini/`, `.codex/`).
- UTF-8 encoding only. No smart quotes or non-ASCII characters in manifests and rules.


<!-- plugin: dependency-management / dependency-management -->
---
description: Universal dependency management rules for Python and agent services.
globs: ["requirements*.txt", "requirements*.in", "Dockerfile", "pyproject.toml"]
---

## 🐍 Python Dependency Rules (Summary)

**Full workflow details → `.agents/skills/dependency-management/SKILL.md`**

### Non-Negotiables
1. **No manual `pip install`** — all changes go through `.in` → `pip-compile` → `.txt`.
2. **Commit `.in` + `.txt` together** — the `.in` is intent, the `.txt` is the lockfile.
3. **Service sovereignty** — every agent service owns its own `requirements.txt`.
4. **Tiered hierarchy** — Core (`requirements-core.in`) → Service-specific → Dev-only.
5. **Declarative Dockerfiles** — only `COPY requirements.txt` + `RUN pip install -r`. No ad-hoc installs.
6. **Hub-and-Spoke DRY** — canonical scripts at plugin/project root; file-level symlinks in `skills/` subfolders (no duplicate files).
7. **Symlink Resolution** — installers resolve symlinks to physical copies in `.agents/`; installed skills must be fully self-contained.
8. **Agent Orchestration** — cross-plugin coordination uses skill delegation via the prompt loop, not direct script execution.

