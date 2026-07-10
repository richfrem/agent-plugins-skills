---
description: Hard gate preventing agents from deleting skill directories based on consolidation or absorption reasoning. Covers the specific failure mode where an agent incorrectly concludes a skill's function has been absorbed by another skill.
globs: ["plugins/**/skills/**", "plugins/**/SKILL.md"]
---

# Rule: Skill Deletion Guard — No Absorption Deletions

## The Failure Mode This Rule Prevents

An agent reviews two skills, concludes that skill A's "functionality is covered by" or "has been absorbed into" skill B, then **deletes skill A's directory**. This is always wrong without explicit user instruction.

This exact incident occurred in April 2026: `os-skill-improvement` was deleted because an agent concluded its methodology was "absorbed" by `os-improvement-loop`. It was not. Recovery required `git show` from history and manual restoration.

---

## Iron Law

**Never delete a skill directory, its SKILL.md, or its evals because you believe the skill is redundant, absorbed, consolidated, or superseded.**

This is a hard gate. No amount of reasoning makes autonomous deletion acceptable.

---

## Why "Absorption" Is Always a Rationalization

Even when two skills appear to overlap in body content, they are never interchangeable because each skill has three components that are always unique:

1. **Routing identity** — the `trigger:` field and `description:` in frontmatter. Two skills that do similar things still have different routing signatures. Deleting one breaks all prompts that relied on its specific triggers.

2. **Eval contract** — `evals/evals.json` contains should_trigger test cases specific to this skill's domain boundary. These cases define where the skill starts and its neighbors end. No other skill has the same eval contract.

3. **Methodology** — the skill body may encode a distinct protocol, phase sequence, or heuristic that the "absorbing" skill does not replicate verbatim, even if the overall goal is similar.

---

## What to Do Instead of Deleting

| Situation | Correct action |
|---|---|
| Skill seems redundant with another | Flag it to the user: "I noticed overlap between X and Y — do you want to consolidate?" |
| Skill directory exists but SKILL.md is missing | Report it as a zombie directory. Do NOT delete. Ask user. |
| Skill was renamed or moved | Update references. Do NOT delete the original until user confirms. |
| Consolidation task in progress | Move files, update symlinks. The delete step requires explicit user confirmation for each directory. |

---

## Permitted vs Prohibited

| Action | Permitted without user confirmation? |
|---|---|
| Adding content to a skill | Yes |
| Editing SKILL.md | Yes |
| Adding evals | Yes |
| Renaming a skill directory | No — requires explicit confirmation |
| Deleting a skill directory | **No — hard gate, always requires explicit user instruction naming the exact skill** |
| Deleting a skill because it "looks absorbed" | **Never — not even with user permission phrased as "clean up redundant skills"** |

The last row is intentional: "clean up redundant skills" is not explicit permission to delete. The user must name the specific skill: "delete `os-skill-improvement`."

A user request to "clean up", "deduplicate", "merge", "simplify", or "consolidate" skills is **not** deletion permission. These words describe intent, not authorization. Deletion permission must name the exact path or skill slug.

---

## Zombie Directory Protocol

A zombie is a skill directory that exists but has no `SKILL.md`. Zombies are created when:
- A consolidation move was interrupted
- A skill was accidentally deleted mid-migration
- A directory was created for a skill that was never completed

**Do not delete zombie directories.** Instead:
1. Check `git log -- plugins/<plugin>/skills/<name>/` to see the last known state
2. Report to user: "Found zombie directory at `<path>` — no SKILL.md. Last commit: `<sha>`. Restore or delete?"
3. Wait for explicit instruction

---

## For Audit Tools

When auditing a plugin, check for:

```bash
# Zombie skill directories (no SKILL.md)
for dir in plugins/<plugin>/skills/*/; do
    [ -f "${dir}SKILL.md" ] || echo "ZOMBIE: $dir"
done

# Skills listed in CLAUDE.md Plugin State but missing from plugins/
# (cross-reference CLAUDE.md skill lists against actual filesystem)
```

Report zombies as **Critical** findings — they indicate either data loss or an interrupted migration.

---

## Cleanup After Self-Evolution — Also Gated

Accidental deletion often happens during "cleanup after improvement" — an agent self-evolves a
skill, then tries to simplify or tidy surrounding artifacts. This is a common deletion vector.

Any "simplification", "tidying", "removal of overlap", or "cleanup" that occurs during or after
a self-evolution run is subject to the same hard gate as any other deletion. Self-evolution does
not grant additional deletion authority. The classification of a repair as Tier 0 (friction) does
not authorize removing the thing that caused friction.
