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
