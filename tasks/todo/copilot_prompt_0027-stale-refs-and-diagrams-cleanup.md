# Copilot Prompt — 0027: Stale References, Diagrams, and Verifier Contract Fix

**Model:** claude-sonnet-4.6
**Status:** READY TO EXECUTE
**Triggered by:** Post-merge audit of tasks 0025 + 0026 — stale references not caught by Copilot implementation

---

## Context

Tasks 0025 (agent-agentic-os simplification) and 0026 (agent-loops simplification) were implemented
and merged. A post-merge audit found three categories of issues:

1. **Critical contract gap**: os-evolution-verifier adversarial threshold was implemented with the
   pre-Round-5 spec (3/6). Round 5 tightened it to 4/6 + critical scenarios N-04/N-05/N-06 must ALL FAIL.
   PARTIAL=FAIL for gating was also not enforced.

2. **Stale text references**: Skills still reference deleted components (triple-loop-orchestrator,
   os-skill-improvement) in examples, tables, and guide text.

3. **Unreferenced assets**: Diagrams and reference files point to deleted components or are never
   referenced by any active skill. Some are symlinks to deleted personas.

Read the full plan before writing any files:
```bash
cat tasks/todo/0025-agentic-os-simplification-plan.md
```

All file paths are relative to the repo root:
`/Users/richardfremmerlid/Projects/agent-plugins-skills`

---

## FIX-1: os-evolution-verifier — Binary contract (CRITICAL)

File: `plugins/agent-agentic-os/skills/os-evolution-verifier/SKILL.md`

Read the file. Find the `### Binary PASS/FAIL Contract` section (around line 213).

**Three changes in this section:**

**1a. PASS condition — remove PARTIAL from the passing VERDICT:**

Find:
```
- EVOLUTION_VERIFICATION VERDICT is PASS or PARTIAL
```
Replace with:
```
- EVOLUTION_VERIFICATION VERDICT is PASS
  (PARTIAL counts as FAIL for gating — logged but does not unblock pipeline)
```

**1b. FAIL condition — add explicit PARTIAL clause:**

Find:
```
A run FAILS if any condition above is not met.
```
Replace with:
```
A run FAILS if any condition above is not met, OR if VERDICT is PARTIAL.
PARTIAL means outputs are incomplete — this is a FAIL for any gating decision,
even though it is logged separately for diagnostic purposes.
```

**1c. Adversarial threshold — raise from 3/6 to 4/6, add critical scenario requirement:**

Find:
```
the verifier must produce FAIL verdicts on at least 3 of 6 adversarial inputs. A verifier
that passes all adversarial inputs is not operational — it is only checking the happy path.
```
Replace with:
```
the verifier must produce FAIL verdicts on at least 4 of 6 adversarial inputs. A verifier
that passes all adversarial inputs is not operational — it is only checking the happy path.

**Critical scenario requirement**: N-04 (malformed run-config), N-05 (truncated plan), and
N-06 (bad evals schema) MUST ALL produce FAIL verdicts. These test structural failures, not
just crashes. A verifier that catches crashes (N-01/N-02/N-03) but misses structural failures
(N-04/N-05/N-06) has a ceiling of 3/6 and is not detecting the important failure modes.
```

Verify the section reads correctly after edits (no duplication, no broken markdown).

---

## FIX-2: os-experiment-log/SKILL.md — Replace triple-loop-orchestrator examples

File: `plugins/agent-agentic-os/skills/os-experiment-log/SKILL.md`

Read the file. Find all references to `triple-loop-orchestrator`. There are approximately 4:

**2a. Example filename comment (around line 26):**
Find:
```
2026-04-25-orchestrator-os-eval-runner.md    ← from triple-loop-orchestrator
```
Replace with:
```
2026-04-25-os-improvement-loop-os-eval-runner.md    ← from os-improvement-loop
```

**2b. `triggered_by` table row (around line 41):**
Find the table row containing:
```
| `orchestrator` | triple-loop-orchestrator |
```
Replace `triple-loop-orchestrator` with `os-improvement-loop` in that row.

**2c. Example `--triggered-by` command (around lines 80 and 86):**
Find any line with:
```
--triggered-by triple-loop-orchestrator
```
Replace `triple-loop-orchestrator` with `os-improvement-loop`.

---

## FIX-3: os-guide/SKILL.md — Remove os-skill-improvement (6 occurrences)

File: `plugins/agent-agentic-os/skills/os-guide/SKILL.md`

Read the file. Find all 6 occurrences of `os-skill-improvement`. Make these changes:

**3a. Mutation table row (around line 57):**
Find the table row containing `os-skill-improvement` under Mutation.
Replace `os-skill-improvement` with `os-improvement-loop` in that row. The example should
now show os-improvement-loop as the mutation executor.

**3b. INNER loops sentence (around line 117):**
Find:
```
INNER loops (`os-eval-runner`, `os-skill-improvement`) never close a session.
```
Replace with:
```
INNER loops (`os-eval-runner`) never close a session.
```

**3c. Phase 7 section (around lines 153–165):**
Find the entire Phase 7 section header and body. It starts with:
```
### Phase 7: Continuous Skill Improvement (os-skill-improvement)
```
And contains content about invoking os-skill-improvement on weak skills.

Replace the entire Phase 7 section with:
```markdown
### Phase 7: Continuous Improvement (os-improvement-loop)

When routing accuracy reveals a weak skill, invoke `os-improvement-loop` with the target skill
and a locked eval set. The loop runs mutate→eval→KEEP/DISCARD cycles until improvement is
confirmed, then `os-eval-backport` gates the winner to production.

→ See [os-improvement-loop SKILL.md](../os-improvement-loop/SKILL.md) for invocation details.
```

**3d. Workflow step (around line 184):**
Find:
```
4. os-skill-improvement → Harden any skill whose routing was found weak (Phase 7)
```
Replace with:
```
4. os-improvement-loop → Harden any skill whose routing was found weak (Phase 7)
```

---

## FIX-4: os-environment-probe/SKILL.md — Replace triple-loop-orchestrator table entry

File: `plugins/agent-agentic-os/skills/os-environment-probe/SKILL.md`

Read the file. Find line 91 (or wherever the table row is):
```
| Overnight unattended loop | triple-loop-orchestrator | — |
```
Replace with:
```
| Overnight unattended loop | os-improvement-loop | — |
```

---

## FIX-5: optimize-agent-instructions/SKILL.md — Replace os-skill-improvement example

File: `plugins/agent-agentic-os/skills/optimize-agent-instructions/SKILL.md`

Read the file. Find the line (around line 29):
```
assistant: [triggers os-skill-improvement, not optimize-agent-instructions]
```
Replace with:
```
assistant: [triggers os-improvement-loop, not optimize-agent-instructions]
```

---

## FIX-6: os-improvement-loop/SKILL.md — Update stale diagram reference

File: `plugins/agent-agentic-os/skills/os-improvement-loop/SKILL.md`

Read the file. Find the line (around line 82):
```
See `assets/diagrams/triple-loop-learning-system.mmd` for the full visual.
```
Replace with:
```
See `assets/diagrams/agent-agentic-os-architecture.mmd` for the plugin structure overview.
```

(The triple-loop-learning-system diagram describes the deprecated triple-loop agents, not the
current os-improvement-loop. The architecture diagram is the correct current reference.)

---

## FIX-7: references/operations/operating-protocols.md — Remove triple-loop-orchestrator

File: `plugins/agent-agentic-os/references/operations/operating-protocols.md`

Read the file. Find the section referencing `triple-loop-orchestrator` and
`headless-overnight-orchestrator.mmd`.

This is likely a table row or paragraph that describes the unattended execution pattern
using the deleted triple-loop-orchestrator agent. Update it:

Replace `triple-loop-orchestrator` with `os-improvement-loop`.
Replace the diagram reference `headless-overnight-orchestrator.mmd` — the diagram is
being deleted (see FIX-10). Remove the diagram reference inline or replace with:
`See os-improvement-loop SKILL.md for headless execution details.`

---

## FIX-8: agent-loops references — Fix broken persona symlinks

The files below are reference stubs that symlinked to deleted personas.
They now contain only a dangling path like `../../../personas/security/security-auditor.md`.

**Check and delete these files:**
```bash
cat plugins/agent-loops/references/qa-expert.md
cat plugins/agent-loops/references/security-auditor.md
```

If they only contain a broken symlink path (a single line pointing to the deleted personas/),
delete them:
```bash
rm plugins/agent-loops/references/qa-expert.md
rm plugins/agent-loops/references/security-auditor.md
```

Then update the orchestrator skill which references these:

File: `plugins/agent-loops/skills/orchestrator/SKILL.md`

Find any reference to `qa-expert.md` or `security-auditor.md` reference files.
Update to say:
```
Adversarial personas: user-supplied system prompt or from an installed agent persona plugin.
The `qa-expert` and `security-auditor` persona stubs have been removed — supply your own
system prompt for specialized review agents.
```

Also check and delete the symlinks in orchestrator/references/:
```bash
cat plugins/agent-loops/skills/orchestrator/references/qa-expert.md
cat plugins/agent-loops/skills/orchestrator/references/security-auditor.md
```

If they only contain a path to the now-deleted root references/qa-expert.md, delete them:
```bash
rm plugins/agent-loops/skills/orchestrator/references/qa-expert.md
rm plugins/agent-loops/skills/orchestrator/references/security-auditor.md
```

Also check red-team-review fallback-tree.md for stale persona path:
```bash
grep -n "personas" plugins/agent-loops/skills/red-team-review/fallback-tree.md
```
If it references `personas/security/security-auditor.md`, update to:
```
If instructed to use a specific persona but the file cannot be found, ask the user to
supply a system prompt directly or install an agent persona plugin.
```

---

## FIX-9: agent-loops diagrams — Update agent_loops_overview.mmd

File: `plugins/agent-loops/assets/diagrams/agent_loops_overview.mmd`

Read the file. Find the comment at the end of the diagram:
```
Retro -.->|"Feeds Next Loop<br>(RLM Cache)"| Trigger
```

"RLM Cache" is an OS-level concept from agent-agentic-os. Replace with:
```
Retro -.->|"Feeds Next Loop<br>(Loop Learnings)"| Trigger
```

Also, the "Seal" nodes throughout the diagram (`SL_Seal`, `RT_Seal`, `AO_Seal`, `SW_Seal`)
were described as "Bundle Session Artifacts" — this is fine as a generic description.
No change needed to the Seal nodes themselves; the text is already generic.

---

## FIX-10: Delete unreferenced/stale diagrams

**agent-agentic-os** — delete diagrams with 0 active references that are also clearly stale
(for deleted components or legacy flows):

First, check each one is a real file and not referenced by a symlink from skill/references/diagrams/:

```bash
# Check for symlinks from skill directories pointing to these assets
for diagram in \
  "headless-overnight-orchestrator.mmd" \
  "triple-loop-learning-system.mmd" \
  "session-memory-manager-flow.mmd" \
  "shared-memory-layers.mmd" \
  "event-bus-architecture.mmd" \
  "agentic-os-init-flow.mmd" \
  "agentic-os-overview.mmd" \
  "agentic-os-structure.mmd" \
  "agentic-os-system-architecture.mmd" \
  "agentic-os-memory-subsystem.mmd" \
  "loop-progress-report.mmd" \
  "sibling-repo-labs.mmd"; do
  echo "=== $diagram ==="
  # Check if any file in skills/ references this diagram name
  grep -r "$diagram" plugins/agent-agentic-os/skills/ plugins/agent-agentic-os/agents/ \
    plugins/agent-agentic-os/references/ 2>/dev/null | grep -v "^Binary" | grep -v "^$"
  # Check if any symlink in skill/references/diagrams/ points to this asset
  find plugins/agent-agentic-os/skills -name "$diagram" -type l 2>/dev/null
done
```

For each diagram that has zero references AND no symlinks pointing to it, delete it:
```bash
# Delete only the confirmed-dead ones after the check above
# Use rm for each confirmed dead file — DO NOT use rm -rf on the diagrams directory
```

**Confirmed dead (delete these — they reference deleted components):**
- `plugins/agent-agentic-os/assets/diagrams/headless-overnight-orchestrator.mmd`
  Reason: only referenced in operating-protocols.md for triple-loop-orchestrator (deleted)

- `plugins/agent-agentic-os/assets/diagrams/triple-loop-learning-system.mmd`
  Reason: references triple-loop-architect/orchestrator (deleted). The only text refs
  are in references/operations/triple-loop.md and os-improvement-loop SKILL.md line 82
  — both are being updated in FIX-6 and FIX-11 below.

**Delete if confirmed no symlinks point to them (check first):**
- `plugins/agent-agentic-os/assets/diagrams/session-memory-manager-flow.mmd`
- `plugins/agent-agentic-os/assets/diagrams/shared-memory-layers.mmd`
- `plugins/agent-agentic-os/assets/diagrams/event-bus-architecture.mmd`
- `plugins/agent-agentic-os/assets/diagrams/agentic-os-init-flow.mmd`
- `plugins/agent-agentic-os/assets/diagrams/agentic-os-overview.mmd`
- `plugins/agent-agentic-os/assets/diagrams/agentic-os-structure.mmd`
- `plugins/agent-agentic-os/assets/diagrams/agentic-os-system-architecture.mmd`
- `plugins/agent-agentic-os/assets/diagrams/agentic-os-memory-subsystem.mmd`
- `plugins/agent-agentic-os/assets/diagrams/loop-progress-report.mmd`
- `plugins/agent-agentic-os/assets/diagrams/sibling-repo-labs.mmd`

**agent-loops** — delete ADK variant diagrams (0 references anywhere):

```bash
# Confirm no references first
grep -r "agent_loops_overview_adk\|agent_swarm_adk\|inner_outer_loop_adk\|learning_loop_adk\|red_team_review_loop_adk" \
  plugins/agent-loops/ 2>/dev/null | grep -v "^Binary"
```

If no output (confirmed 0 refs), delete:
```bash
rm plugins/agent-loops/assets/diagrams/agent_loops_overview_adk.mmd
rm plugins/agent-loops/assets/diagrams/agent_loops_overview_adk.png
rm plugins/agent-loops/assets/diagrams/agent_swarm_adk.mmd
rm plugins/agent-loops/assets/diagrams/agent_swarm_adk.png
rm plugins/agent-loops/assets/diagrams/inner_outer_loop_adk.mmd
rm plugins/agent-loops/assets/diagrams/inner_outer_loop_adk.png
rm plugins/agent-loops/assets/diagrams/learning_loop_adk.mmd
rm plugins/agent-loops/assets/diagrams/learning_loop_adk.png
rm plugins/agent-loops/assets/diagrams/red_team_review_loop_adk.mmd
rm plugins/agent-loops/assets/diagrams/red_team_review_loop_adk.png
```

---

## FIX-11: references/operations/triple-loop.md — Update or annotate as deprecated

File: `plugins/agent-agentic-os/references/operations/triple-loop.md`

Read the file. This document describes the old triple-loop architecture including
the deleted triple-loop-architect and triple-loop-orchestrator agents.

It is referenced by `skills/os-improvement-loop/references/operations/triple-loop.md`
(likely a symlink).

**Option A (preferred):** If the document is primarily about the triple-loop agents,
prepend a deprecation notice:
```markdown
> **DEPRECATED**: The `triple-loop-architect` and `triple-loop-orchestrator` agents described
> in this document have been removed as of v1.6.0. The capability is now handled by
> `os-improvement-loop`. This document is retained for historical reference only.
> For current operations, see [os-improvement-loop SKILL.md](../../skills/os-improvement-loop/SKILL.md).
```

**Option B:** If the document is mostly about the loop execution mechanics (not agent-specific),
update the agent names throughout to reference `os-improvement-loop` instead.

Read the document to determine which option applies. Do not delete — it may contain
useful mechanics that are still referenced indirectly.

---

## Verification (run after all fixes)

```bash
# 1. No remaining deprecated references in active agent/skill files
echo "=== Checking for deprecated component refs ==="
grep -r "triple-loop-orchestrator\|triple-loop-architect\|os-skill-improvement" \
  plugins/agent-agentic-os/agents/ \
  plugins/agent-agentic-os/skills/ \
  2>/dev/null | grep -v "^Binary" | grep -v "DEPRECATED\|historical\|deprecated"

# 2. Verifier threshold is 4 not 3
echo "=== Verifier threshold ==="
grep -n "4 of 6\|3 of 6" plugins/agent-agentic-os/skills/os-evolution-verifier/SKILL.md

# 3. PARTIAL=FAIL is enforced in verifier
echo "=== Verifier PARTIAL clause ==="
grep -n "PARTIAL.*FAIL\|PARTIAL counts as FAIL" \
  plugins/agent-agentic-os/skills/os-evolution-verifier/SKILL.md

# 4. Deleted diagrams are gone
echo "=== Confirming deleted diagrams are gone ==="
ls plugins/agent-agentic-os/assets/diagrams/ | grep -E "headless|triple-loop-learning|session-memory|agentic-os-system"

# 5. ADK diagrams deleted from agent-loops
echo "=== Confirming ADK diagrams gone ==="
ls plugins/agent-loops/assets/diagrams/ | grep "_adk"

# 6. No broken symlinks in either plugin
echo "=== Symlink check agent-agentic-os ==="
find plugins/agent-agentic-os -type l | while read link; do
  [ -e "$link" ] && echo "OK   $link" || echo "BROKEN $link -> $(readlink $link)"
done

echo "=== Symlink check agent-loops ==="
find plugins/agent-loops -type l | while read link; do
  [ -e "$link" ] && echo "OK   $link" || echo "BROKEN $link -> $(readlink $link)"
done

# 7. JSON files still valid
python3 -c "import json; json.load(open('plugins/agent-agentic-os/.claude-plugin/plugin.json')); print('agentic-os plugin.json OK')"
python3 -c "import json; json.load(open('plugins/agent-loops/.claude-plugin/plugin.json')); print('agent-loops plugin.json OK')"
```

---

## Output Contract

Write a summary to `temp/copilot_output_0027.md` with:
- List of each FIX applied: file modified, what changed (1-2 lines each)
- Files deleted (list)
- Output of all verification commands
- Any content that was ambiguous (document the decision made and why)
- Any FIX skipped and why (e.g. if a diagram had a symlink pointing to it)

Do NOT write a HANDOFF_BLOCK — this is a direct cleanup task, not an architect session.
