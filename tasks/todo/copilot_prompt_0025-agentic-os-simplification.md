# Copilot Prompt — 0025: agent-agentic-os Simplification

**Model:** claude-sonnet-4.6
**Status:** DRAFT — Phase 1 sections are final; Phase 2+ marked [PENDING reviewer feedback]
**Plan reference:** tasks/todo/0025-agentic-os-simplification-plan.md
**Triggered by:** os-architect (simplification + restructure initiative)

---

## Context

You are implementing a planned simplification of the `agent-agentic-os` plugin. This is
NOT a ground-up rewrite. It is a set of targeted cuts and structural upgrades to a working
system. The core learning loop (os-architect → os-improvement-loop → os-eval-runner →
os-eval-backport → os-experiment-log) is NOT touched.

Read the full plan before writing any files:
```bash
cat tasks/todo/0025-agentic-os-simplification-plan.md
```

All file paths are relative to the repo root:
`/Users/richardfremmerlid/Projects/agent-plugins-skills`

---

## PHASE 1 — Component Removals (execute in full)

### WS-1A: Delete deprecated agent files

Delete these two files. They are replaced by `os-improvement-loop` with a `--lab` flag.
Do NOT delete the `agent-loops` plugin's `triple-loop-learning` skill — that is a different
plugin and is kept as the execution substrate.

```bash
rm plugins/agent-agentic-os/agents/triple-loop-architect.md
rm plugins/agent-agentic-os/agents/triple-loop-orchestrator.md
rm plugins/agent-agentic-os/references/sample-prompts/triple-loop-architect-prompt.md
```

Verify removals:
```bash
ls plugins/agent-agentic-os/agents/
```

Expected: only `agentic-os-setup.md`, `improvement-intake-agent.md`, `os-architect-agent.md`,
`os-architect-tester-agent.md`, `os-health-check.md` remain.

---

### WS-1B: Delete os-skill-improvement skill

Delete the entire skill directory. Its function is absorbed into `os-improvement-loop`.

```bash
rm -rf plugins/agent-agentic-os/skills/os-skill-improvement/
```

Verify:
```bash
ls plugins/agent-agentic-os/skills/
```

Expected: `os-skill-improvement` no longer appears.

---

### WS-1C: Update os-architect-agent.md — remove deprecated references

File: `plugins/agent-agentic-os/agents/os-architect-agent.md`

Read the file first. Then make these targeted edits:

**1. Remove three rows from the embedded knowledge table (around line 54–57):**
Remove the rows for:
- `os-skill-improvement` ("Single-skill improvement without full lab")
- `triple-loop-architect` ("Sets up a full triple-loop eval lab interactively")
- `triple-loop-orchestrator` ("Runs unattended overnight improvement iterations")

**2. Update Category 3 routing (around line 174):**
Change:
```
improvement-intake-agent → triple-loop-orchestrator
```
To:
```
improvement-intake-agent → os-improvement-loop
```

**3. Update the optional step (around line 265):**
Change:
```
Optionally run `os-skill-improvement` or `os-improvement-loop` after update to validate.
```
To:
```
Optionally run `os-improvement-loop` after update to validate.
```

**4. Add skill creation threshold rule** — insert after the gap detection section (Phase 2).
Add this block after the existing "ecosystem audit" or "gap detection" content:

```markdown
### Skill Creation Threshold

A new skill is only created when ALL of the following are true:
- The capability gap has been identified in ≥ 3 separate architect sessions
- An audit confirms no existing skill can be extended to cover it
- A skill creation plan is written before any SKILL.md is created

Do not create skills reactively. Modify first; create only when modification fails repeatedly.
```

**5. Add Routing Decision Audit block** — append to the HANDOFF_BLOCK output format.
Add as a required field after the existing 7 HANDOFF_BLOCK fields:

```markdown
## ROUTING DECISION AUDIT
- Chosen path: [A / B / C / no-op]
- Alternatives considered: [list with one-line rationale for rejection]
- Why chosen: [one sentence — key deciding factor]
```

This block is required on every os-architect run. It makes routing decisions reviewable.

---

### WS-1D: Update os-improvement-loop SKILL.md — remove os-skill-improvement references

File: `plugins/agent-agentic-os/skills/os-improvement-loop/SKILL.md`

Read the file first. Make these targeted edits:

**1. Remove os-skill-improvement from the ASCII diagram (around line 53–59):**
Remove any lines referencing `os-skill-improvement`. Replace with `os-eval-runner` where
it appears as the improvement agent.

**2. Remove os-skill-improvement from the description and references (around line 74, 80):**
Replace `os-skill-improvement` with `os-eval-runner` where it appears as the inner agent.

**3. Update the "Not suitable for" list (around line 229):**
Remove: `Single-session work (use learning-loop or triple-loop instead)`
Replace with: `Single-session work on a well-understood problem (use os-eval-runner directly)`

**4. Add evaluation budget guard** — append to the Execution section or constraints:

```markdown
### Evaluation Budget Guard (enforced)

These limits are hard constraints enforced by the orchestrator, not guidelines:

| Limit | Value | Rationale |
|-------|-------|-----------|
| max_iterations_per_lab | 10 | Prevents runaway cost; sufficient for signal |
| max_eval_datasets_per_run | 3 | base + holdout + adversarial only |
| critic_invocations_per_iteration | 1 | One cheap-model challenge per mutation |

Labs that exceed these limits must be split into separate sessions.
```

**5. Update agent-loops relationship note** (line 900 area, references section):
Change the reference to triple-loop to clarify the dependency:
```markdown
- This skill delegates to [agent-loops Pattern 5 (triple-loop-learning)](../../agent-loops/skills/triple-loop-learning/SKILL.md)
  for the inner loop execution pattern. agent-loops is the execution substrate;
  os-improvement-loop adds the eval gate, experiment log, and lab isolation on top.
```

---

### WS-1E: Update README.md

File: `plugins/agent-agentic-os/README.md`

Read the file first. This is a structural reframe, not a content rewrite.

**1. Remove triple-loop-architect and triple-loop-orchestrator from the Day-to-Day Usage table.**
Replace the triple-loop row with:
```
| Run an unattended improvement loop | `/os-architect` → "improve X skill with a lab" → os-improvement-loop |
```

**2. Remove triple-loop-architect and triple-loop-orchestrator from the Agents table.**
The "Invoke directly" agents are now: `agentic-os-setup`, `os-health-check` only.
(triple-loop-architect and triple-loop-orchestrator are deleted.)

**3. Remove os-skill-improvement from the Evaluation & Improvement skills table.**

**4. Add "Utilities" subsection** under "What's in the Box" — move these skills out of the
core skills table into a clearly labeled utilities section:

```markdown
#### Utilities (support tools — not part of the core loop)

| Skill | Purpose |
|-------|---------|
| `optimize-agent-instructions` | Audits and rewrites AI agent instruction files |
| `os-clean-locks` | Removes stale lock files to resolve deadlocked agents |
| `todo-check` | Audits files for TODO comments |
| `os-guide` | Full OS reference — layers, interactions, patterns |
```

**5. Update the "How It Works — Triple-Loop Learning System" section.**
Replace the current description with:

```markdown
### Learning Loop

The core learning cycle: **os-improvement-loop** orchestrates multi-iteration improvement
runs against a locked eval set. **os-eval-runner** scores each mutation (KEEP/DISCARD).
**os-eval-lab-setup** isolates each run in a sibling repo. **os-eval-backport** provides
the human review gate before any winning change reaches production.

Execution pattern delegates to [agent-loops Pattern 5](../agent-loops/skills/triple-loop-learning/)
for inner loop mechanics. agent-loops provides the loop substrate; this plugin adds the
eval gate, experiment log, and lab isolation.

→ Full detail: [references/operations/triple-loop.md](./references/operations/triple-loop.md)
```

**6. Add relationship note** to the "Part of the Plugin Triad" section:

```markdown
| Plugin | Role |
|--------|------|
| `agent-scaffolders` | Spec + Factory — what ecosystem artifacts are and how to create them |
| **`agent-agentic-os`** | **Operations — eval-gated improvement loop, experiment log, memory** |
| `agent-loops` | Execution patterns — loop substrate used by os-improvement-loop |
```

---

## PHASE 2 — Structural Upgrades [PENDING — finalize after reviewer feedback]

These sections are drafted but not finalized. Do NOT implement until the plan has been
reviewed by Claude and Gemini and Phase 1 changes are merged.

---

### WS-2A: os-evolution-verifier — Binary PASS/FAIL contract [PENDING]

File: `plugins/agent-agentic-os/skills/os-evolution-verifier/SKILL.md`

Add to Phase 5 (Summary Report) section:

```markdown
### Binary PASS/FAIL Contract

A run PASSES only if ALL of the following are true:
- At least 1 artifact is present at a declared OUTPUTS path
- HANDOFF_BLOCK contains all 7 required fields
- STATUS is not `crashed`
- EVOLUTION_VERIFICATION VERDICT is PASS or PARTIAL

A run FAILS if any condition above is not met.

**Adversarial threshold:** When running WS-N failure injection scenarios (N-01 through N-06),
the verifier must produce FAIL verdicts on at least 3 of 6 adversarial inputs. A verifier
that passes all adversarial inputs is not operational — it is only checking the happy path.
```

---

### WS-2B: os-eval-runner — Global overfitting detection [PENDING]

File: `plugins/agent-agentic-os/skills/os-eval-runner/SKILL.md`

Add as a hard gate in the scoring section. The holdout set becomes a required input, not
optional. The rule:

```
IF base_score > prev_base AND holdout_score < prev_holdout → OVERFIT → force DISCARD
```

This overrides any KEEP decision. Overfitting is always a DISCARD, regardless of how the
lab was configured.

---

### WS-2C: experiment_log.py — Add synthesize command [PENDING]

File: `plugins/agent-agentic-os/scripts/experiment_log.py`

Add `synthesize` subcommand. Queries last N entries (default 5), groups by target and
outcome (KEEP/DISCARD, PASS/FAIL), and outputs a structured synthesis block:

```
## SYNTHESIZED LEARNINGS — [date]
### Patterns that consistently improve performance
- [pattern] → seen in [session IDs], avg delta +[X]
### Patterns that cause regressions
- [pattern] → seen in [session IDs], avg delta -[X]
### Recommended updates to core skills
- [skill] → [specific change suggested by pattern]
```

Output file: `context/experiment-log/synthesis-[date].md`
This file is the input to `os-memory-manager` for long-term promotion.

Also add `tags:` field support to the experiment log YAML header schema. Tags are
comma-separated strings: `tags: skill-improvement, overfitting-detected, path-b`

---

### WS-2D: os-architect-tester — Routing accuracy eval set [PENDING]

File: `plugins/agent-agentic-os/agents/os-architect-tester-agent.md`

Add a routing accuracy eval set alongside the existing 8 transcripts:

```json
[
  {"input": "improve todo-check skill", "expected_route": "os-improvement-loop"},
  {"input": "probe my environment", "expected_route": "os-environment-probe"},
  {"input": "there is no skill for monitoring plugin health", "expected_route": "Path C"},
  {"input": "update os-guide to mention environment profile", "expected_route": "Path B"},
  {"input": "everything looks fine, no changes needed", "expected_route": "Path A (no-op)"}
]
```

Track: routing accuracy % across all scenarios. Log as a metric in the experiment log
with `result_type: qualitative` and `tags: routing-accuracy`.

---

## Verification Steps (run after Phase 1 complete)

```bash
# 1. No broken symlinks
find plugins/agent-agentic-os -type l | while read link; do
  [ -e "$link" ] && echo "OK   $link" || echo "BROKEN $link -> $(readlink $link)"
done

# 2. No remaining triple-loop or os-skill-improvement references in active files
grep -r "triple-loop-architect\|triple-loop-orchestrator\|os-skill-improvement" \
  plugins/agent-agentic-os/agents/ \
  plugins/agent-agentic-os/skills/ \
  plugins/agent-agentic-os/README.md \
  2>/dev/null | grep -v "^Binary"

# 3. Agent directory contains expected files only
ls plugins/agent-agentic-os/agents/
# Expected: agentic-os-setup.md, improvement-intake-agent.md, os-architect-agent.md,
#           os-architect-tester-agent.md, os-health-check.md

# 4. Skills directory no longer contains os-skill-improvement
ls plugins/agent-agentic-os/skills/ | grep "os-skill-improvement"
# Expected: no output

# 5. README line count (should be 130-180 lines after edits)
wc -l plugins/agent-agentic-os/README.md
```

---

## Output Contract

After completing Phase 1, write a summary to `temp/copilot_output_0025_phase1.md` with:
- List of files deleted
- List of files modified with brief description of each change
- Output of all verification commands above
- Any anomalies found (broken refs, unexpected content)

Do NOT write a HANDOFF_BLOCK — this is a direct implementation task, not an architect session.
