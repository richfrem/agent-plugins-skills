# os-eval-backport — Phase Guide

A concise reference for the 7 phases of the Lab-to-Master Handoff. For the full
protocol see `SKILL.md`; for the flow diagram see
`assets/diagrams/os-eval-backport-phases.mmd`.

---

## Phase Sequence at a Glance

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → (approval) → Phase 4
                                                          ↓
                                            Phase 5 (interrogate lab agent)
                                                          ↓
                                            Phase 5b (close the loop)
                                                          ↓
                                            Phase 6 (capture learnings) ← MANDATORY
```

---

## Phase 0 — Intake

**Goal:** Establish the three coordinates needed for every subsequent step.

| Question | What you need |
|:---|:---|
| Q1 | Lab repo path (where the eval ran) |
| Q2 | Master plugin path in `agent-plugins-skills` |
| Q3 | Baseline commit SHA (`baseline:` commit in `git log`) |

**Output:** Confirmed intake block shown to user before proceeding.

---

## Phase 1 — Read Run Log & Self-Assessment

**Goal:** Understand what happened before looking at any diffs.

Read `temp/logs/` and `temp/retrospectives/` in full. Note:
- Final quality score vs baseline
- KEEP vs DISCARD iteration count
- Errors, surprises, workarounds
- Agent's own next-step recommendation

---

## Phase 2 — Get the Full Diff

**Goal:** Know every file that changed and why.

```bash
git log --oneline <baseline>..HEAD
git diff <baseline> HEAD --name-only
git diff <baseline> HEAD
```

For each changed file: what changed, why (from log), does it generalize to master?

---

## Phase 3 — Structured Assessment

**Goal:** Get user sign-off before touching master.

Build an assessment table with four possible verdicts:

| Verdict | Meaning |
|:---|:---|
| **ACCEPT** | Apply verbatim to master |
| **ADAPT** | Apply with stated modifications |
| **REJECT** | Do not apply (state why) |
| **REVIEW** | Needs closer inspection first |

**Do not apply any change until the user approves this table.**

---

## Phase 4 — Apply Approved Changes

**Goal:** Deliberately port each approved change to the canonical master source.

1. Read the current master file first (it may have diverged from the lab copy)
2. Make targeted edits — never paste entire file contents
3. Verify the result
4. Commit: `backport(<plugin>): <summary>`

---

## Phase 5 — Interrogate the Lab Agent (Before Closing)

**Goal:** Surface first-hand operational knowledge that diffs and logs can't capture.

Ask the user to relay (or ask directly if in the same session):

**Always:**
1. Which steps in `eval-instructions.md` were unclear or caused improvisation?
2. Paste the full evolved `copilot_proposer_prompt.md`
3. Did the Step A3 trace scan work? Was it useful or too noisy?

**If the loop stalled:**
4. What did web research or Copilot brainstorm find?
5. What bridge words were discovered? (Add to Trap Warning if not already there.)

**If environment was reset mid-run:**
6. Was the Cold Start protocol sufficient to recover?

Incorporate any findings into eval templates/skills before Phase 6.

---

## Phase 5b — Close the Loop

**Goal:** Deliver a clear handoff report to the user.

- Which master files were updated
- Which changes were rejected and why
- Suggested follow-up (next eval round, evals coverage gaps, fixture improvements)

---

## Phase 6 — Capture Learnings (Mandatory)

**Goal:** Preserve non-obvious knowledge for future eval sessions.

### 6a — Dated Session Log

Write `context/memory/YYYY-MM-DD.md` covering:
- Skill, baseline score → final score, iteration count
- Backported changes (accepted)
- Rejected changes with reasons
- Snags, workarounds, open items

Delegate to `os-memory-manager` if the Agentic OS is initialized in master.

### 6b — Persistent Memory (non-obvious filter)

Apply the filter before writing anything:
> "Would a future agent running this workflow get burned without this?"

Write a `feedback` memory entry **only** for:
- Snags that blocked the run
- Scoring footguns
- Non-obvious architectural insights
- Reusable ADAPT patterns

Skip routine score improvements and self-evident changes.

### 6c — Promote to context/memory.md

If OS is present and the filter passed, ask `os-memory-manager` to promote the
finding to `context/memory.md` with a deduplication ID.

---

## Key Invariants

- **Never blind-copy** from lab to master — always read the master file first.
- **Phase 5 must precede Phase 6** — interrogation can produce findings that go into memory.
- **Phase 6 is not optional** — even a clean session with no surprises needs a dated session log.
- **Master uses hub-and-spoke symlinks** — only the canonical source files need updating.
