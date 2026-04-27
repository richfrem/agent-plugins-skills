# Copilot Prompt — 0026: agent-loops Simplification

**Model:** claude-sonnet-4.6
**Status:** PHASE 3 ACTIVE — Phase 1+2 committed as v2.1.0; Phase 3 now executing
**Plan reference:** tasks/todo/0026-agent-loops-simplification-plan-v1.2.md
**Triggered by:** agent-agentic-os simplification (boundary enforcement — execution substrate must be OS-clean)

---

## Context

You are implementing a planned simplification of the `agent-loops` plugin. This is NOT a ground-up
rewrite. It is a set of targeted cuts and a boundary scrub on a working execution library.

The 5 execution primitives are kept intact:
- `learning-loop` — single-agent linear research/synthesis
- `red-team-review` — adversarial review loops
- `dual-loop` — sequential manager/worker delegation
- `agent-swarm` — parallel concurrent execution
- `triple-loop-learning` — hierarchical meta-loop (outer/mid/inner)

Everything else — specifically the `personas/` directory, opinionated domain templates, and
OS-level infrastructure references embedded in the skills — is being removed.

Read the full plan before writing any files:
```bash
cat tasks/todo/0026-agent-loops-simplification-plan-v1.2.md
```

Also read `references/phases.md` before starting Phase 2 (you will need it for WS-2B):
```bash
cat plugins/agent-loops/references/phases.md
```

All file paths are relative to the repo root:
`/Users/richardfremmerlid/Projects/agent-plugins-skills`

---

## PHASE 1 — Extraction & Pruning (execute in full)

### WS-1A: Delete the personas directory

The `personas/` directory contains 38 highly specific system prompts that account for over 50%
of the plugin's token footprint. They violate the "framework-agnostic" design goal — a loop
execution library should not dictate agent personality.

```bash
rm -rf plugins/agent-loops/personas/
```

Verify removal:
```bash
ls plugins/agent-loops/
```

Expected: `personas/` does NOT appear in the listing.

---

### WS-1B: Delete opinionated domain templates

These two templates hardcode references to a specific user's legacy domain workflow
(`QEC-AI hypothesis`, `DrHall`, `Containment Trauma`). They are not portable.

```bash
rm plugins/agent-loops/assets/templates/learning_audit_template.md
rm plugins/agent-loops/assets/templates/sources_template.md
```

Verify:
```bash
ls plugins/agent-loops/assets/templates/
```

Expected: `learning_audit_template.md` and `sources_template.md` do NOT appear.
The remaining templates (`loop_retrospective_template.md`, `strategy-packet-template.md`) stay.

---

### WS-1C: Scrub loop_retrospective_template.md — surgical edit only

File: `plugins/agent-loops/assets/templates/loop_retrospective_template.md`

Read the file first. The four-question "Red Team Meta-Audit" section structure (Blind Spot Check,
Verification Rigor, Architectural Drift, Seal Integrity) is domain-neutral and valuable — **keep it**.
Only the hardcoded example string needs replacing.

**Make exactly one change:**

Find the line containing `"The new ADR 088 worked perfectly"` (or a close variant referencing ADR 088).
Replace it with:
```
"[What worked well this loop — cite specific evidence]"
```

No other changes to this file.

---

### WS-1D: Bump plugin.json version

File: `plugins/agent-loops/.claude-plugin/plugin.json`

Read the file first and verify it is already clean (no persona-related keywords, no references to
`personas/` in capabilities). Then bump the version:

**Change version:** `2.0.0` → `2.1.0`

This signals the architectural cleanup boundary.

Verify valid JSON and version:
```bash
python3 -c "
import json
p = json.load(open('plugins/agent-loops/.claude-plugin/plugin.json'))
print('version:', p.get('version'))
persona_leak = [k for k in ['persona','frontend-developer','graphql-architect'] if any(k in str(v) for v in p.values())]
print('persona keywords leaked:', persona_leak or 'NONE — clean')
"
```

Expected: version `2.1.0`; persona keywords leaked: NONE — clean.

---

### WS-1E: Fix red-team-review dependencies

File: `plugins/agent-loops/skills/red-team-review/SKILL.md`

Read the file. Find the Dependencies section (or any section listing required files/inputs). It
currently references the `personas/` directory (which is being deleted in WS-1A) as a required
source for adversarial personas.

**Update the personas dependency statement** to:
```
Adversarial personas: user-supplied system prompt, or from an installed CLI agent plugin
(e.g., agent-personas). The `personas/` directory is no longer bundled with agent-loops.
```

Remove any file path reference to `personas/` or `.agents/skills/claude-cli-agent/personas/`.

---

## PHASE 2 — Architecture Realignment (OS Decoupling)

**Prerequisites:** Phase 1 complete and verified. Read `plugins/agent-loops/references/phases.md`
in full before starting WS-2B — its Phase V framework is the replacement template for the
contaminated closure phases.

---

### WS-2A: Fix broken cross-references in learning-loop

File: `plugins/agent-loops/skills/learning-loop/SKILL.md`

There are two broken references that are live bugs (not simplification work — fix regardless):

**Fix 1 — Wrong skill name (around line 85):**
Find any reference to `triple-loop` used as a standalone skill name (not `triple-loop-learning`).
Change it to `triple-loop-learning`.

Example: if the file says "see triple-loop for multi-tier execution" → "see triple-loop-learning
for multi-tier execution".

**Fix 2 — Broken file path (around line 204):**
Find a markdown link that reads approximately `[dual-loop SKILL](../triple-loop/SKILL.md)`.
The path `../triple-loop/` does not exist (the directory is `../triple-loop-learning/`).

Read the surrounding context to determine the intent:
- If the link is inside a "Related Skills" or "See Also" section and is meant to point to the
  dual-loop skill, change to: `[dual-loop SKILL](../dual-loop/SKILL.md)`
- If it is actually meant to reference triple-loop-learning, change to:
  `[triple-loop-learning SKILL](../triple-loop-learning/SKILL.md)` (and fix the link text too)

Fix whichever is correct based on context. Do not guess — read the surrounding paragraph first.

---

### WS-2B: Scrub learning-loop and dual-loop of OS-level infrastructure

These two skills are heavily contaminated with OS-specific infrastructure references that make
them dependent on `agent-agentic-os` internals. The fix is to remove the OS infrastructure
calls and replace the closure phases with a framework-agnostic protocol.

#### Part 1: learning-loop/SKILL.md

File: `plugins/agent-loops/skills/learning-loop/SKILL.md`

Read `plugins/agent-loops/references/phases.md` first. It contains a clean, framework-agnostic
Phase V (closure protocol) that explicitly defines what a loop MUST NOT do. Use it as the
blueprint for the replacement closure phases.

**Remove these specific contamination patterns (search and remove each):**

1. Any line containing `${CLAUDE_PROJECT_DIR}/context/memory/retrospectives/`
   → Remove the entire instruction. Replace with a generic local output path:
   `Save the retrospective to a local file (e.g., \`./retrospective-[date].md\`) or stdout.`

2. Any line containing `python context/kernel.py emit_event`
   → Remove the entire line. Do not replace (this is OS-internal telemetry, not loop behavior).

3. Any line containing `python "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/post_run_metrics.py"`
   → Remove the entire line. Do not replace.

4. Any line containing `session-memory-manager`
   → Remove the OS promotion instruction. Replace with:
   `Memory promotion is the responsibility of the calling system (e.g., agent-agentic-os).`

5. Any phase block (Phase V through Phase VIII) that prescribes saving to `context/memory/`
   paths, running kernel.py, or promoting to OS-level memory:
   → Replace the entire block with the framework-agnostic Phase V from `references/phases.md`.
   Keep Phases I–IV intact — only the closure phases (V onward) change.

**Do not remove:** Phases I–IV (orientation, planning, execution, synthesis). These are correct.

#### Part 2: dual-loop/SKILL.md

File: `plugins/agent-loops/skills/dual-loop/SKILL.md`

Apply the same pattern removals:
1. Any line containing `context/kernel.py` → remove entirely
2. Any line containing `${CLAUDE_PROJECT_DIR}/context/memory/` → replace with generic local path
3. Any line containing `python context/kernel.py emit_event` → remove entirely
4. Any line containing `session-memory-manager` → replace with:
   `Memory promotion is the responsibility of the calling system.`

---

### WS-2C: Strip triple-loop-learning of OS terminology

File: `plugins/agent-loops/skills/triple-loop-learning/SKILL.md`

This skill's mermaid diagram and Dependencies section have leaked OS-level concepts.

**1. Mermaid diagram cleanup:**
Find the mermaid diagram (usually a `flowchart` or `graph` block). Look for node labels
containing any of these OS-level terms:
- `"Friction Aggregation"` or `Friction Aggregation`
- `"Keep/Discard & L3 Memory"` or `L3 Memory`
- `"Headless Scoring"`
- Any node labelled with eval, scoring, or memory promotion operations

Remove those specific nodes and their edges from the diagram. The diagram should show only
execution structure (Outer/Mid/Inner loop flow) — not evaluation or memory operations.

**2. Dependencies section cleanup:**
Find any line referencing `eval_runner.py` in the Dependencies, Required Scripts, or similar section.

Replace with:
```
Evaluation gate: NOT included in this primitive. The calling system (e.g., agent-agentic-os
os-improvement-loop) is responsible for wrapping this skill with an eval gate and experiment log.
```

Also remove any reference to `context-bundler` as a dependency if present.

---

### WS-2D: Fix orchestrator sanctuary commands

File: `plugins/agent-loops/skills/orchestrator/SKILL.md`

Read the file. Find the "Chained Command Handoff" block (around lines 177-178). It currently
instructs the user to run specific slash commands:
- `/sanctuary-seal`
- `/sanctuary-persist`

These are OS-environment-specific commands not available in any generic project.

**Replace the entire sanctuary command block** with:
```markdown
**Session Closure**

Execution complete. Run your environment's standard session closure sequence. If you are
using `agent-agentic-os`, trigger `os-improvement-loop` closure. If you are in a standalone
project, save any outputs to your preferred persistence location and close the session.
```

---

### WS-2E: Rewrite cli-agent-executor.md persona tables

File: `plugins/agent-loops/references/cli-agent-executor.md`

Read the file. It currently contains tables or examples that hardcode:
- The `personas/` directory path (`.agents/skills/claude-cli-agent/personas/`)
- Specific persona file names (`frontend-developer.md`, `graphql-architect.md`, etc.)
- Commands of the form `cat <PERSONA_PROMPT>` piped into CLI agents

**Replace persona-specific examples with generic equivalents.** The purpose of this reference
doc is to explain the CLI execution pattern, not to enumerate specific personas.

Replace hardcoded persona examples like:
```bash
cat .agents/skills/claude-cli-agent/personas/frontend-developer.md | claude -p "Review this PR" < pr.md
```

With generic equivalents:
```bash
cat system_prompt.md | claude -p "Review this PR" < pr.md
# or, if no system prompt is needed:
claude -p "Analyze this code for security issues" < input.md
```

Remove all tables that enumerate specific persona names (frontend-developer, graphql-architect,
postgres-pro, etc.). Keep the doc's explanation of the execution pattern itself.

---

## PHASE 3 — Script Hardening & Evals [EXECUTE NOW]

These sections are finalized. Do NOT implement until Phase 2 changes are committed and verified.

---

### WS-3A: Verify script docs [EXECUTE]

Files: `plugins/agent-loops/scripts/swarm_run.py`, `plugins/agent-loops/scripts/agent_orchestrator.py`

Read both scripts. Verify:
1. The `--help` output (or module docstring) accurately reflects the current API — no references to
   deleted personas or OS-specific hooks
2. Any path examples in comments do not reference `personas/` or OS-internal paths
3. The README.md description of these scripts calls them "standalone LEGO bricks" (decoupled from OS)

If any of the above are stale, make the minimum targeted update.

---

### WS-3B: Audit evals for all 5 primitives [EXECUTE]

For each of the 5 primitives, audit its `evals/evals.json`:

Primitives to check:
- `plugins/agent-loops/skills/learning-loop/evals/evals.json`
- `plugins/agent-loops/skills/red-team-review/evals/evals.json`
- `plugins/agent-loops/skills/dual-loop/evals/evals.json`
- `plugins/agent-loops/skills/agent-swarm/evals/evals.json`
- `plugins/agent-loops/skills/triple-loop-learning/evals/evals.json`

For each file:
1. Confirm it uses `should_trigger: true` or `should_trigger: false` (boolean schema)
2. If any entries use the legacy `expected_behavior` field instead, replace with `should_trigger`
3. Confirm there are at least 6 routing scenarios per primitive (target: 3 `should_trigger: true`,
   3 `should_trigger: false`)
4. If a file has fewer than 6 entries, add realistic scenarios based on the skill's SKILL.md trigger phrases

Run this audit script to get a baseline:
```bash
python3 - <<'EOF'
import json, os, pathlib

primitives = [
    "learning-loop", "red-team-review", "dual-loop", "agent-swarm", "triple-loop-learning"
]
base = pathlib.Path("plugins/agent-loops/skills")

for p in primitives:
    evals_path = base / p / "evals" / "evals.json"
    if not evals_path.exists():
        print(f"MISSING: {evals_path}")
        continue
    data = json.load(open(evals_path))
    entries = data if isinstance(data, list) else data.get("evals", [])
    legacy = [e for e in entries if "expected_behavior" in e]
    true_count = sum(1 for e in entries if e.get("should_trigger") is True)
    false_count = sum(1 for e in entries if e.get("should_trigger") is False)
    print(f"{p}: {len(entries)} entries | true={true_count} false={false_count} legacy={len(legacy)}")
EOF
```

Fix any file showing legacy entries or fewer than 6 total entries.

---

## Verification Steps (run after Phase 1 complete)

```bash
# 1. personas/ is gone
ls plugins/agent-loops/ | grep personas
# Expected: no output

# 2. Domain templates are deleted
ls plugins/agent-loops/assets/templates/
# Expected: learning_audit_template.md and sources_template.md do NOT appear

# 3. No sanctuary commands in active skill files
grep -r "sanctuary-seal\|sanctuary-persist" plugins/agent-loops/skills/ 2>/dev/null
# Expected: no output

# 4. No OS-level infrastructure in skill files (Phase 2 check)
grep -r "context/kernel.py\|session-memory-manager\|post_run_metrics.py\|CLAUDE_PROJECT_DIR" \
  plugins/agent-loops/skills/ 2>/dev/null
# Expected: no output after Phase 2 is complete

# 5. No broken symlinks
find plugins/agent-loops -type l | while read link; do
  [ -e "$link" ] && echo "OK   $link" || echo "BROKEN $link -> $(readlink $link)"
done
# Expected: all OK

# 6. plugin.json is valid, v2.1.0
python3 -c "
import json
p = json.load(open('plugins/agent-loops/.claude-plugin/plugin.json'))
print('version:', p.get('version'))
"
# Expected: version 2.1.0

# 7. ADR 088 reference is gone from templates
grep -r "ADR 088" plugins/agent-loops/assets/templates/ 2>/dev/null
# Expected: no output

# 8. Triple-loop cross-reference fix confirmed
grep -n "triple-loop\b" plugins/agent-loops/skills/learning-loop/SKILL.md | grep -v "triple-loop-learning"
# Expected: no output (all references now say triple-loop-learning, not triple-loop)
```

---

## Output Contract

After completing Phase 1, write a summary to `temp/copilot_output_0026_phase1.md` with:
- List of files deleted (WS-1A, WS-1B)
- List of files modified with brief description of each change (WS-1C through WS-1E)
- Output of all Phase 1 verification commands above (checks 1, 2, 5, 6, 7)
- Any anomalies found (broken refs, unexpected content, JSON parse errors)

After completing Phase 2, append to the same file (or write `temp/copilot_output_0026_phase2.md`):
- List of files modified with brief description of OS-scrub changes (WS-2A through WS-2E)
- Output of Phase 2 verification commands above (checks 3, 4, 8)
- Any content that was ambiguous (e.g., the line 204 link fix — document what decision was made and why)

Do NOT write a HANDOFF_BLOCK — this is a direct implementation task, not an architect session.
