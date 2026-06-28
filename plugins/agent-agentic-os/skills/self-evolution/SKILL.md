---
name: self-evolution
plugin: agent-agentic-os
version: 1.0.0
description: >
  Self-healing and self-evolving pattern for agents operating against repo capabilities,
  scripts, skills, sub-agents, selectors, workflows, and external systems. Classifies
  evolution events into four tiers — Friction/Workaround, Gap, Failure, Regression —
  applies repo-profile-gated edits with appropriate autonomy, verifies the fix, and
  updates domain reference files ("The Map, not the Diary"). Invoke whenever a tool call,
  subprocess, or workflow returns a failure OR whenever the agent used a workaround,
  bypass, guess, or manual substitute for an existing repo capability.
model: inherit
color: orange
tools: ["Bash", "Read", "Write", "Edit"]
trigger: >
  self-heal, self-evolving, friction, workaround used, bypassed existing capability,
  manual workaround, guessed because unclear, ambiguous instruction, friction encountered,
  system did not improve, stale selector, DOM changed, element not found,
  selector not found, script broken, helper broken, CDP failure, automation failure,
  evolve skill, patch helper, update reference, domain playbook, map not diary,
  fix broken script, regression detected
---

# Self-Evolution Skill

**Trigger:** Any tool call, subprocess, workflow, skill, sub-agent, helper, or documented
repo capability fails, behaves ambiguously, or is bypassed through a workaround, guess,
or manual substitute — and the fix or Map Debt entry is within allowed boundaries.

**Core principle:** The agent does not just retry — it learns. Every fix either patches
a helper (so the failure can't recur) or updates a reference file (so future agents
avoid the same dead end). Fixes that aren't recorded are not fixes; they are patches
waiting to become the same bug again.

---

## Phase 0 — Read the Repo Profile

Before doing anything else, locate and read the repo's self-evolution profile:

```
<repo-root>/plugins/<plugin>/references/self-evolution-profile.md
```

If no profile exists for the current repo/plugin, create a conservative default one now
using the template in Phase 0.1 below, then continue — but only proceed if the target
edit is inside the default allowed directories.

Also read `<plugin>/references/map-debt.md` if it exists. Surface any open entry that
matches the current friction — if `Repeat: YES`, escalate immediately (go to Phase 6)
instead of deferring again.

The profile defines:
- **Allowed edit directories** — the only dirs the agent may edit autonomously
- **Error pattern → tier classification table** — maps known error signatures to tiers
- **Domain playbook location** — where reference files ("The Map") live
- **Evolution log path** — where to append the fix record

### Phase 0.1 — Bootstrap Profile (if missing)

If no profile exists, write one at `<plugin>/references/self-evolution-profile.md`:

```markdown
# Self-Evolution Profile — <Plugin Name>

## Allowed Edit Directories

- plugins/<plugin>/skills/
- plugins/<plugin>/scripts/
- plugins/<plugin>/references/

## Explicit Confirmation Required

- plugin.json
- CLAUDE.md
- .agent/rules/
- ADRs/
- docs/
- repository root files
- any file outside this plugin
- any rename, move, or deletion

## Error Pattern Classification
| Pattern | Tier |
|---------|------|
| workaround used / bypassed capability | Friction |
| element not found / selector missing | Regression |
| function not exported / module not found | Gap |
| TypeError / syntax error | Failure |
| subprocess timeout | Regression |
| JSON parse error | Failure |

## Domain Playbook Location
plugins/<plugin>/references/

## Evolution Log
plugins/<plugin>/references/evolution-log.md

## Map Debt
plugins/<plugin>/references/map-debt.md
```

---

## Phase 1 — Classify the Evolution Event

**First ask:** did the task succeed only because of a workaround, bypass, guess, or manual
substitute for an existing repo capability? If yes → classify as **Tier 0** directly.

Otherwise, using the error message, stack trace, and context, classify into exactly one tier:

### Tier 0 — Friction / Workaround
> "The task completed, but the system did not improve."

**Definition + signals:** see `.agent/rules/self-evolution-policy.md` § Tier 0.

**Response:** If small + inside allowed edit boundaries — patch now, update The Map. If not safe or small — log as Map Debt (see Phase 7). If repeated or blocking — escalate.

### Tier 1 — Gap
> "The capability doesn't exist yet."

**Signals:**
- No code handles this action at all
- `function not found`, `is not a function`, `module has no export`
- Agent is at the boundary of what the codebase supports
- No evidence this ever worked

**Response:** Build the missing piece. No evidence collection needed.

### Tier 2 — Failure
> "Code exists but is broken."

**Signals:**
- `TypeError`, `SyntaxError`, `ReferenceError` inside our own code
- Logic bug producing wrong output (wrong JSON shape, wrong return value)
- Wrong arguments passed to an existing function
- No external system change implied

**Response:** Debug the code. Read the relevant source, identify the bug, patch it.

### Tier 3 — Regression
> "This worked before. Something external changed."

**Signals:**
- Selector that previously matched now returns null/empty
- Subprocess timeout on an operation with known prior success
- `element not found`, `cannot read property of null` on a well-used DOM path
- git log or session memory confirms prior success

**Response:** Collect evidence first (screenshot + DOM snapshot), then patch with a
fallback selector or updated timing. Document the change in The Map.

**If ambiguous between Failure and Regression:** default to Regression and collect
evidence — the cost of a screenshot is lower than patching the wrong layer.

---

## Phase 2 — Collect Evidence

Evidence collection is tier-dependent:

| Tier | Evidence to collect |
|------|-------------------|
| Friction / Workaround | Intended capability, what was bypassed, workaround used, why the intended path was not used, reproduction step |
| Gap | None — log the capability boundary in the evolution log |
| Failure | Error message + stack trace (last 20 lines of stderr) + relevant source lines |
| Regression | Screenshot of current UI state + DOM snapshot of the failing selector area + `git log --oneline -5` on the affected file |

For Regression, run the DOM snapshot before touching any code:
```javascript
// Inline Node snippet to dump selector context
const els = document.querySelectorAll('[data-name]');
console.log(JSON.stringify([...els].map(e => e.getAttribute('data-name')).filter(Boolean)));
```

Save evidence to `temp/self-evolution/<timestamp>-evidence/`.

---

## Phase 3 — Plan the Repair

Based on tier and evidence:

**Gap:** Identify the exact file and function to create. Check the allowed edit
directories from the profile. If the target file is outside those dirs, escalate
to the user (Phase 6).

**Failure:** Read the failing function. Identify the minimal fix. Prefer adding a
guard or correcting an argument over rewriting logic.

**Regression:** Identify the old selector/timing from git history or the domain
playbook. Find a new stable selector from the DOM snapshot. Plan a two-path patch:
primary (new selector) + fallback (broader query with filter).

Write the plan as 3–5 bullet points before touching any file.

---

## Phase 4 — Execute with Permission Gates

Check the **edit type** before writing:

| Edit type | Gate |
|-----------|------|
| Add new function / export | Auto-approved — proceed |
| Add new selector / fallback path | Auto-approved — proceed |
| Modify existing function logic | Auto-approved — append git diff to evolution log after edit |
| Rename or move a file | Confirm with user: "About to rename X → Y. Confirm?" |
| Delete any file or function | **Hard stop** — always confirm with user before proceeding |

Steps:
1. Verify target file is inside an allowed edit directory (from profile).
2. Apply the edit.
3. If edit type is "modify existing": immediately run `git diff <file>` and save output to evolution log.
4. Do not make multiple independent changes in a single Phase 4 pass — one logical fix at a time.

---

## Phase 5 — Verify the Fix

Re-run the exact operation that originally failed:

```bash
# Re-run the specific command / test that triggered self-evolution
```

**Pass:** Proceed to Phase 6.

**Fail (attempt 1):** Return to Phase 3, reconsider the diagnosis. Try a different
repair approach.

**Fail (attempt 2):** Return to Phase 3, broaden evidence collection.

**Fail (attempt 3 — final):** Escalate to user (Phase 6, escalation path). Do not
make further edits. Present the full evidence bundle and the three approaches tried.

---

## Phase 6 — Update The Map

Whether or not the fix succeeded, update the domain reference files:

**If fix succeeded:**
- If a selector changed: update the relevant `references/*.md` with the new selector
  and a note: `<!-- updated <date>: old=[...] new=[...] TV regression -->`
- If a new capability was built: create or update a domain playbook in the
  `<playbook-location>` from the profile (see Playbook Format below)
- If a timing constant changed: update comments in the patched file noting the
  observed minimum wait

**If escalating to user:**
- Write a brief summary to the domain playbook with status `UNRESOLVED` and the
  three approaches tried — so the next agent doesn't repeat the same dead ends

### Domain Playbook Format

Create `<playbook-location>/<topic>-playbook.md`:

```markdown
# Playbook: <Topic>

**Status:** ACTIVE | UNRESOLVED
**Last verified:** YYYY-MM-DD
**Relevant files:** list of files

## What This Covers
One sentence.

## The Mechanics
Step-by-step: what works, what the exact selectors/timing are, why.

## Known Failure Modes
| Symptom | Tier | Fix applied |
|---------|------|-------------|

## Change History
| Date | What changed | Tier | Outcome |
```

---

## Phase 7 — Log the Evolution

Append one row to the evolution log (`evolution-log.md` from profile):

```markdown
| <date> | <tier> | <what failed or friction observed (one line)> | <what was patched, OR "Map Debt: <reason>"> | <edit type> | <outcome: FIXED/MAP_DEBT/ESCALATED> |
```

When outcome is `MAP_DEBT`, also append an entry to `<plugin>/references/map-debt.md`
(create with header if missing). Map Debt is a working queue — items are resolved over time;
the evolution log is the immutable audit trail. Do not double-count: one write to each.

```markdown
# Map Debt

| Logged | Cycle ID | Artifact | Friction | Why Not Fixed | Recommended Fix | Severity | Repeat | Status |
|--------|----------|----------|----------|---------------|-----------------|----------|--------|--------|

| <YYYY-MM-DD> | <CID from events.jsonl> | <file path or skill slug> | <friction in one sentence> | <reason> | <recommended fix> | S/M/L | YES/NO | OPEN |
```

**Aging rule:** At Phase 0 read, count completed cycles since the entry's `Cycle ID`. If an
`OPEN` entry is older than 3 completed cycles, auto-escalate before starting new work.
If the Cycle ID is from a prior session (not in current `events.jsonl`), fall back to
the Logged date: auto-escalate if `(today - Logged) > 14 days`.
Set `Status` to `RESOLVED` when fixed, `ESCALATED` when escalated to the user.

If the log file doesn't exist yet, create it with the header:

```markdown
# Evolution Log

| Date | Tier | Failure | Patch | Edit Type | Outcome |
|------|------|---------|-------|-----------|---------|
```

---

## Escalation Template

When escalating to the user after 3 failed attempts:

> **Self-Evolution Escalation — [Tier: Regression/Failure/Gap]**
>
> **Operation that failed:** `<command>`
> **Error:** `<error message>`
> **Evidence:** `temp/self-evolution/<timestamp>-evidence/`
>
> **Three approaches tried:**
> 1. `<approach 1>` → `<result>`
> 2. `<approach 2>` → `<result>`
> 3. `<approach 3>` → `<result>`
>
> **What I need from you:** `<specific question — e.g., "What is the new selector for the Indicators dialog?">`
>
> Once you provide it, I will apply the fix and update The Map.

---

## Rules

1. **Never edit outside the allowed directories.** If the fix requires editing a file
   outside the profile's allowlist, escalate immediately — do not ask forgiveness.
2. **Never delete without confirmation.** Regardless of what the profile says.
3. **Always update The Map.** A fix that isn't recorded is a future regression waiting
   to happen.
4. **One logical change per Phase 4 pass.** Do not bundle multiple fixes.
5. **Evidence before editing on Regression.** Screenshot and DOM snapshot first, always.
6. **Three attempts maximum.** After three failures, escalate with the full evidence
   bundle — do not keep trying different approaches silently.
