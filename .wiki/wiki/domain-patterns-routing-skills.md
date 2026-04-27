---
concept: domain-patterns-routing-skills
source: plugin-code
source_file: agent-agentic-os/references/domain-patterns/routing-skill.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.692937+00:00
cluster: skill
content_hash: d7091ee6fbecd0aa
---

# Domain Patterns: Routing Skills

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Domain Patterns: Routing Skills

Skills evaluated primarily on routing accuracy (correct trigger/no-trigger given a user prompt).
Use when `--primary-metric` is `quality_score`, `f1`, `precision`, or `recall`.

## When to use this file

Check this file at Phase 1 Step A before formulating a hypothesis. If the failure matches
a known pattern, apply that pattern's documented escape as the Step B proposal.

---

## Known Successful Mutations

### Pattern 1: Adversarial Negative Sharpening

**Failure type:** `false_positive` — skill triggers on prompts that are adjacent but should not trigger.

**Root cause:** Description or example block uses generic verbs ("improve", "optimize", "check") that overlap with unrelated tasks.

**Escape:**
- Add a `<negative-example>` block explicitly showing 2–3 prompts that look similar but must NOT trigger.
- Tighten the description to name the exact domain (e.g. "evaluates routing accuracy of SKILL.md files" not "evaluates skill quality").
- Add a `## When NOT to use` section listing the most common false-positive patterns by name.

**Confirmed KEEP iterations:** 6+ across multiple skills.

---

### Pattern 2: Keyword Scope Tightening

**Failure type:** `false_negative` — skill fails to trigger on valid prompts because phrasing varies.

**Root cause:** Trigger phrases in the description enumerate a narrow vocabulary. Users rephrase the intent using synonyms not covered.

**Escape:**
- Expand the description's trigger phrase list with synonym clusters (e.g. "run / execute / kick off / start / launch").
- Add 2–3 new `<example>` blocks that use the missing phrasing verbatim.
- Avoid over-specifying the object of the verb — "evaluate [skill]" is more robust than "evaluate the SKILL.md file for [skill]".

**Confirmed KEEP iterations:** 4+ across multiple skills.

---

### Pattern 3: Example Block Expansion for Boundary Cases

**Failure type:** Mixed — ambiguous boundary cases produce both false positives and false negatives in the same eval set.

**Root cause:** The eval set contains prompts in the grey zone (close-but-not-quite vs. close-but-yes). The SKILL.md examples only show clear positives, leaving the model to guess at boundaries.

**Escape:**
- Identify the 2–3 hardest boundary cases from `evals/results.tsv` (lowest confidence or most inconsistent).
- Add one `<example>` per boundary case — one `should_trigger: true` and one `should_trigger: false` that differ by only one key phrase.
- In the description, explicitly name the distinguishing criterion: "only triggers when X is present, not when X is merely implied."

**Confirmed KEEP iterations:** 5+ across multiple skills.

---

## Novel Candidates (awaiting 2nd KEEP confirmation)

[Empty — orchestrator appends here when a novel KEEP hypothesis is flagged as "Novel failure — tracking as candidate pattern." and then confirmed on a second iteration]


## See Also

- [[domain-patterns]]
- [[domain-patterns-exploration-cycle]]
- [[domain-patterns-exploration-session-failures]]
- [[architectural-patterns-adapted-from-obrasuperpowers-mit-httpsgithubcomobrasuperpowers]]
- [[fix-patterns-like-or]]
- [[handle-nested-skills-eg-skillsdeferredskill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/references/domain-patterns/routing-skill.md`
- **Indexed:** 2026-04-27T05:21:03.692937+00:00
