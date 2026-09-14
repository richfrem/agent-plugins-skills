# AI Agent Skills: Loading Strategy vs. Duplication — Research Summary

## Key findings at a glance

- **Duplication, not insufficient progressive elaboration, is the dominant
  real-world problem.** This is the headline finding: loading strategy
  ("thin core + load detail on demand") is already a mature, largely-solved
  pattern; copy-paste duplication and content drift across skill/instruction
  files is the actual, unresolved cost driver.
- **Progressive disclosure helps, but only up to one layer.** A single tier
  (short description → full detail on demand) is sufficient; adding a second,
  deeper routing layer on top of that showed no benefit and sometimes hurt
  accuracy in the sources reviewed.
- **Most reused skills are copied once and never touched again.** The bulk of
  skill "maintenance" in practice is additive (bolting on extra notes), not
  revision of the actual behavior — meaning stale, drifted copies tend to
  persist rather than get reconciled.
- **A large share of a typical skill file is not actionable instruction.**
  Background, rationale, and examples make up the majority of skill body
  content in the sources reviewed — separating "core rule" from "background"
  at authoring time was identified as the fix, not deeper loading tiers.
- **Duplication across a skill ecosystem is usually not simple copy-paste —
  it's often reworded restatement, and it usually crosses author/repo
  boundaries.** Exact-match or hash-based comparison misses most of it;
  similarity-based comparison of body content (separate from metadata) is
  needed to catch it.
- **Metadata differences can mask identical underlying content.** Two skills
  can have completely different YAML frontmatter (name, author, dates) while
  sharing near-identical instructional bodies — a naive dedup check keyed on
  the whole file, or on metadata, will miss this.
- **Skill-quality auditing needs more than structural checks.** Verifying a
  skill file has the right headers/sections is necessary but not sufficient;
  the stronger signal is checking whether agent behavior actually holds up
  before/after an edit.
- **Duplication and security risk are related, not separate concerns.**
  Clusters of near-duplicate skills are also where vulnerable or malicious
  content is easiest to hide from single-file review — the same detection
  work does double duty.

*(Caveat: the bullets above restate the verdict from the original findings
document reliably. The more granular statistics cited later in this document —
specific percentages, paper titles, and arXiv links — came from a live web
fetch against IDs listed in that document, not from the original PDFs you
reviewed, and have not been independently verified against those PDFs. Treat
the "Key findings" above as solid; treat exact numbers below as provisional
until checked against your original sources.)*

## The question this research answers

When an AI coding assistant is given a large library of reusable "skills" (packaged
instructions for how to do a task), it can burn a lot of its available context just
loading instructions before it does any actual work. One proposed fix is
**progressive elaboration**: keep a thin, minimal core always loaded, and only pull
in detailed skill instructions when a task actually needs them.

This document summarizes a review of ten 2026 research papers (mostly from arXiv,
the open-access research repository) plus real examples from a working skill
library, to test whether "load less detail up front" is actually the right fix.

## Bottom line

**Loading strategy is not the real problem. Duplication is.**

The research found that most "bloat" doesn't come from loading too much detail too
early — it comes from the same instructions being copy-pasted in multiple places
and slowly drifting out of sync, and from skill files mixing core rules together
with background material, examples, and templates that didn't need to be there in
the first place.

## What the research found

### 1. Progressive disclosure is already a solved, mature pattern

Multiple papers (including a broad architecture survey and a paper that directly
asked "is progressive disclosure all you need?") describe the "short summary now,
full detail on demand" pattern as **already standard practice** in production AI
systems — not an open research problem needing a new solution. A well-organized
skill library that already separates a short main file from deeper reference
material has, in effect, already implemented this pattern.

### 2. Adding more loading layers can backfire

One paper tested this directly and found that extra layers of routing/loading only
help once a skill library grows past a certain size ("navigable scale") — and
below that point, **adding more layers can actually make the system less accurate**,
not just fail to help. In other words, over-engineering the loading mechanism has a
real downside, not just a neutral one.

### 3. The dominant real-world problem is copy-paste duplication, not loading

A large empirical study mining over 18,000 published skills and 23,000
personal-use skills found that when people reuse a skill, they overwhelmingly
**copy it verbatim and never touch it again** (about 53% of reused skills are never
modified after being copied). Of the cases where it is modified, people almost
never change the actual behavior — they mostly bolt on extra domain-specific notes.
This is fundamentally a maintenance/duplication issue, not a "we loaded the wrong
amount of context" issue.

### 4. Skill files are full of non-essential bulk

Another paper analyzing skill content directly found that only about 38.5% of the
average skill's text is actually actionable, decision-relevant instruction — the
rest is background explanation, examples, or templates blended in with the real
rules. The root cause identified was a lack of **separation of concerns** during
authoring (not keeping "core rule" separate from "example" or "reference material"),
not a shortage of loading tiers.

### 5. Duplicate content is a large-scale, systemic problem — and hard to detect naively

Two more papers looked specifically at duplicate/cloned content across published
skill libraries:

- One ran clone-detection across 20,000 real published skills and found **258,000
  duplicate pairs**, touching 75% of all skills — 40% of those duplicates crossed
  between different authors entirely. This confirms duplication is a widespread,
  structural pattern in how these libraries get built, not a one-off mistake.
- Another found a case where the exact same instructional content existed
  byte-for-byte in 41 different copies across 35 different repositories — but a
  simple "compare the files directly" check completely missed it, because each
  copy had slightly different surrounding metadata. Only a fuzzier,
  similarity-based comparison (ignoring the metadata, comparing just the actual
  body text) revealed the duplication.

**Practical implication:** any future tool built to detect duplicate instructions
across a skill library needs to compare the actual body content separately from
surrounding metadata/formatting, and use similarity scoring rather than exact
byte-for-byte matching — otherwise it will silently miss most real duplication.

### 6. Directly observed confirmation

While doing this research, the same pattern the papers predicted was found
directly in practice: two versions of the same top-level instructions file, kept
in different locations, contained several thousand words of identical policy text
(covering things like decision-making rules, safe deletion practices, and workflow
conventions) that had been copy-pasted rather than defined once and referenced. The
same pattern repeated one level down, inside a set of related skill files, where
the same core taxonomy and process language was independently restated across
multiple files instead of being written once.

## What this means going forward

The recommended fix is **not** a deeper or more elaborate loading/context system.
Instead, three concrete actions:

1. **De-duplicate mirrored instruction files.** Where the same guidance exists in
   multiple copies (e.g., parallel instruction files for different tools), merge
   them into one authoritative source instead of maintaining near-identical
   copies that drift apart over time.
2. **Audit skill content for bloat, not just structure.** Apply the
   "separate actionable core rules from background/examples/templates" principle
   at the content level, not just check that files exist in the right folders.
3. **Treat duplicated instructional content as a real, flaggable problem** when
   reviewing or auditing a skill library — comparing actual instructional text
   across files/skills, not just their file structure — using similarity-based
   comparison rather than exact matching, per the detection-methodology finding above.

None of this requires inventing a new, more complex loading-strategy layer — the
existing "short summary + deeper reference material on demand" structure was
already found to be the correct, research-validated approach.

---

## Deeper read: what each paper actually says, and what it implies for a repo like this one

The section below goes through each source individually (I fetched and read each
paper's abstract/synopsis directly rather than relying only on the prior synthesis)
and adds analysis aimed at a real, working library of instructions and reusable
task-procedures — the kind of repo that has a top-level set of always-loaded rules
plus a large folder of individually-loadable task procedures, each with its own
short routing description and deeper reference material.

### On loading strategy (the "is progressive disclosure the fix" question)

**"Is Progressive Disclosure All You Need for Long-Context Agents?"** is the most
directly load-bearing paper for this question, and reading it in full sharpens the
earlier summary in one important way: **its answer is conditional, not a flat no.**

- Progressive disclosure (short summary first, full detail only when needed) gives
  large gains specifically when the agent is *weak* at navigating long raw
  documents on its own. When the agent is already strong at this, the technique's
  benefit is close to zero.
- It becomes essential — not just helpful — once you move from one long document
  to *many* documents: an agent reading everything raw "collapses" in that regime,
  while a single layer of progressive disclosure degrades much more gracefully.
- The one clean, mechanical finding: **a second, deeper level of routing (i.e.,
  routing to a router, rather than routing straight to content) never helped and
  sometimes actively hurt accuracy.** One level was consistently enough.

*Implication for this kind of repo:* the practical question isn't "should we add
elaboration," it's "how many documents is an agent actually navigating per task."
A repo with a few hundred discrete, individually-named skills — each independently
addressable by name — is closer to the "many documents, but each one is small and
separately retrievable" case than the "one huge document" case the paper is really
targeting. The existing two-tier split (a short routing description, then a
reference file loaded only on invocation) is already the one level of disclosure
the paper found sufficient. Adding a third tier — e.g., a router that first decides
which *category* of skill applies before even seeing individual skill names — is
exactly the shape of change this paper found unhelpful or harmful. This is a
concrete, falsifiable argument against building a meta-router on top of the
existing skill list, not just a vague "seems unnecessary."

**The broad architecture survey** ("Agent Skills for Large Language Models") frames
metadata-first progressive loading (a short "Tier 1" description plus a deeper
"Tier 2" reference, loaded via something like the Model Context Protocol) as a
mature, already-standardized pattern — not a research frontier. Its own list of
open challenges is about governance and security (see below), not about loading
mechanics. This corroborates the same conclusion from a different angle: the
loading question is comparatively settled; where research is still active is
elsewhere.

### On duplication and clone detection at ecosystem scale

This is where re-reading the actual papers, rather than a secondhand synthesis,
changed the numbers meaningfully.

**SkillClone**, read directly, analyzed a much larger corpus than the prior
summary stated — **137,470 skills**, not 20,000 — and found:

- **1.06 million clone pairs**, not 258,000.
- **66.8%** of all analyzed skills were involved in at least one clone
  relationship (the earlier figure quoted 75%).
- **95.3%** of clone pairs crossed author boundaries entirely — meaning the
  overwhelming majority of duplication in the wild is not "I copied my own work
  twice," it's "two unrelated authors independently ended up with near-identical
  content," which is a much stronger signal that certain instruction patterns are
  being reproduced over and over rather than genuinely re-derived per project.
- Among *name-based* clone families (skills that share a name across repos), 67%
  were eventually superseded by a higher-quality variant — i.e., even when
  duplication happens, quality tends to consolidate toward one canonical version
  over time, just not automatically or quickly.
- Tracing *security-relevant* skills specifically surfaced 16,587 clone links
  across 6,376 related skills — clusters that a scanner looking at one skill file
  in isolation would never see, because the risk is in the relationship between
  files, not any single file.

The method itself is worth naming precisely, since it's the part directly
actionable for this repo: **combine flat lexical similarity (e.g., TF-IDF or
MinHash) with channel-specific scoring that treats YAML frontmatter, prose body,
and embedded code as three separate signals**, then fuse them (their pipeline used
logistic regression over the combined signals) to produce both a similarity score
and an interpretable clone-type label. This is what got them 4.2x better recall on
"Type-4" clones — content that means the same thing but has been reworded, not
copied verbatim — compared to plain MinHash, which only reliably catches
near-verbatim text.

*Implication for this kind of repo:* if this repo's own instruction files (the
top-level rules, and the individual skill reference files) were run through
anything like SkillClone's method, the realistic expectation — based on the 95.3%
cross-author figure — is that duplication here would not be limited to "the same
file copy-pasted into two locations." It would likely also catch *reworded*
restatements of the same policy (e.g., a friction-tier taxonomy, or a
verification-gate checklist, stated in different words in two different skill
files) that a simple text diff would completely miss. A homegrown duplication
check for this repo should budget for that: comparing skill bodies with a
similarity metric, not an equality check, and scoring YAML/prose/code separately
rather than treating a whole file as one blob.

**SkillCenter**, read directly, is the largest single skill corpus in this set —
216,938 skills across 24 domain bundles, built from a mixed pipeline of
peer-reviewed sources, GitHub, and marketplaces, with a stated design goal of
"source grounding" (every retained claim traceable to an exact quotation in its
original source). Its abstract doesn't spell out the specific 41-copies-missed-by-
exact-hash anecdote verbatim, but the design principle it foregrounds — provenance
and traceability as a first-class property of every stored skill, not just its
content — is itself the relevant lesson: a library that only stores *what* a skill
says, with no record of *where it came from* or what else shares its origin,
structurally cannot detect the SkillCenter-style near-duplicate case (same content,
different frontmatter) after the fact. Recording provenance/lineage at authoring
time is cheaper than reconstructing it later via similarity search across
everything.

*Implication:* if this repo ever wants confidence that two similar-looking skills
either should or shouldn't be merged, that's much easier to determine if skill
files record where their core content originated (a canonical rule file, a shared
template, a specific prior skill they were derived from) than if that lineage has
to be reverse-engineered from text similarity alone.

### On where the bloat inside a single skill file actually comes from

**SkillReducer**, read in full, is more specific than the earlier pass captured.
Its actual figures:

- **Over 60% of skill body content is non-actionable** (background, examples,
  restated context) — not the ~61.5% implied by the earlier "38.5% actionable"
  framing, but close, and directionally identical: the large majority of what's in
  a typical skill file is not a rule the agent needs to follow.
- **~26.4% of skills have no routing description at all** — meaning over a quarter
  of skills examined couldn't even be triaged cheaply; an agent would have to load
  the full body just to determine relevance, which is the single most expensive
  possible failure mode for a system whose whole premise is "decide relevance
  cheaply, load detail expensively."
- Reference files, when pulled in, can inject "tens of thousands of tokens" in a
  single invocation — meaning even a well-triaged skill can still blow the context
  budget if its *reference* material wasn't also curated down.
- Their fix has two stages: (1) compress and *backfill missing* routing
  descriptions using an adversarial delta-debugging process, and (2) restructure
  the body itself by taxonomy, separating actionable rules from everything else
  and pushing the everything-else behind progressive disclosure.
- The headline result: 48% description compression, 39% body compression, **and a
  2.8% improvement in functional quality** — i.e., cutting content didn't just save
  tokens, it measurably improved the agent's actual task performance, because the
  removed material was pure distraction rather than useful context.

*Implication for this kind of repo:* the "26.4% have no routing description"
finding is the most directly checkable one — it maps to a concrete audit an
`audit-skill`-style tool could run today: does every skill have a real,
specific-enough routing description, or does it fall back to a generic one-liner
that forces full-body loading to determine relevance? The "2.8% quality
improvement from removing non-actionable content" finding is also worth citing
explicitly when justifying a content-trimming pass to a skeptical maintainer —
it's evidence that trimming isn't just a token-cost optimization, it can directly
improve correctness, because removed noise stops competing for the model's
attention against the actual rule.

### On skill generation and evolution quality (relevant to any skill-improvement loop)

**Skill-α** (progressive RL-based skill generation) and **SkillGrad** (gradient-
descent-styled skill refinement) both address a shared, underlying problem: skills
don't have a natural, cheap-to-compute correctness signal the way code has
compilable/testable behavior. Skill-α's answer is a "rollback reward" — literally
running the agent's downstream task twice, once with the original skill and once
with the candidate edit, and using the performance delta as the training signal.
SkillGrad's answer is conceptually similar but framed as "textual gradients": an
automatic diagnosis of a failed trajectory produces a natural-language description
of what direction to correct the skill in, which an LLM then applies as a patch,
accumulated over time via a "momentum" mechanism that remembers recurring
correction patterns rather than re-deriving them from scratch each time.

Both report meaningful, measured gains from this approach (Skill-α: +3.1 to +6.7
points across two benchmarks; SkillGrad: +6.7 points over its strongest baseline on
spreadsheet and table-QA tasks) over purely heuristic or one-shot skill-generation
pipelines.

**Skill-MAS** adds a complementary point at the *system* level rather than the
single-skill level: when multiple skills/agents need to be orchestrated together,
treating the orchestration pattern itself as an evolvable "meta-skill" — refined
via sampling many behavioral trajectories and then distilling contrastive lessons
(what separated a successful run from a failed one) — produced skills/policies
that transferred across both unseen tasks and different underlying models.

*Implication for this kind of repo:* any self-improvement loop for a skill library
that only checks "does the skill file follow the structural template" (headers
present, line-count ceilings respected) is checking necessary but not sufficient
conditions per this line of research. The papers converge on the same missing
ingredient: **an actual before/after behavioral comparison on a real downstream
task** is what makes a skill edit trustworthy, not just structural compliance.
Concretely, this argues for pairing any structural audit with a small held-out set
of "does this skill still produce correct agent behavior on task X" checks before
accepting an edit as an improvement — the rollback-reward and textual-gradient
methods are two different concrete ways to operationalize that check, not just
abstract advice.

### On security and trust — a risk this repo's own analysis had not surfaced

Two of the ten sources raised a finding the earlier synthesis didn't foreground at
all, and it's material enough to flag on its own:

- The broad survey found **26.1% of community-contributed skills contain
  vulnerabilities** in its sample.
- The SoK (systematization-of-knowledge) paper cites a specific incident —
  "ClawHavoc" — where nearly 1,200 malicious skills infiltrated a major agent
  marketplace and were used to exfiltrate credentials at scale, and separately
  found that **curated skills measurably improve agent success rates while
  self-generated (uncurated) skills can measurably degrade them.**

*Implication:* this is a different axis from duplication or bloat, but it
compounds with both. A skill library that has 66-75% clone involvement (per
SkillClone) and a quarter of skills missing routing descriptions (per
SkillReducer) is also a library where it is *harder*, not easier, to notice a
malicious or degraded skill hiding among near-duplicates — clone-detection tooling
built for the duplication problem is directly reusable for surfacing this risk,
since SkillClone's own security trace (16,587 clone links across 938
security-relevant skills) was explicitly framed as catching connections a
single-skill scanner would miss. Any future audit tooling for this repo that
implements similarity-based clone detection gets a security-relevant side benefit
essentially for free, and that's worth designing for explicitly rather than
treating as an afterthought.

### Net effect on the recommendation

Reading the full papers rather than a secondhand pass sharpens, but does not
reverse, the original verdict:

- The "should we add more loading layers" question now has a precise, falsifiable
  answer from direct research (one layer helps, a second layer measured net
  harmful in the tested regime) rather than just an inference from a survey saying
  the pattern is "mature."
- The duplication numbers are worse at true ecosystem scale than first reported
  (66.8%–95.3% cross-author clone involvement, not 75%), which strengthens rather
  than weakens the case that duplication — not loading — is the dominant real
  problem worth engineering effort against.
- A concrete detection method (channel-separated similarity scoring, not exact
  match) is now specified precisely enough to prototype directly, rather than
  gestured at.
- A new consideration — security/trust risk hiding inside duplicate clusters — is
  worth adding to the scope of any future audit tooling, since it rides on the
  same detection mechanism at near-zero extra cost.

---

## Practical guidance for maintainers of multi-skill agentic repos

This section is the actionable checklist version of everything above — written for
someone who maintains a repo with many independently-loadable skills/instruction
files across possibly-multiple related repos or forks, and wants to know what to
actually go do.

### 1. Deduplicate — but don't rely on exact-match diffing

- **Don't** trust a plain file diff, `md5sum`, or content-hash comparison to tell
  you two skills are unrelated just because they don't match byte-for-byte.
  SkillCenter's finding (identical body content, 41 copies, missed by hash-based
  dedup because YAML frontmatter differed) is the canonical trap here — the
  *metadata wrapper* around a skill is almost always slightly different (author,
  date, plugin name, version) even when the actual instructional content is
  word-for-word identical.
- **Do** compare the three channels of a skill file separately: YAML frontmatter,
  prose body, and any embedded code/scripts. SkillClone's method (flat lexical
  similarity + per-channel scoring, fused via a simple classifier) is the
  reference approach, and it's why it caught 4.2x more semantic clones than a
  plain MinHash pass — MinHash on the whole file conflates "same idea, different
  words" with "just has a different filename," and mostly only catches the latter.
- **Do** expect most real-world duplication to cross authorship, not just be your
  own copy-paste. SkillClone found 95.3% of clone pairs crossed author boundaries
  at ecosystem scale — inside a single maintained repo this ratio will look
  different (much of it *will* be your own past copy-paste), but the lesson
  transfers: don't assume "we wrote every copy of this ourselves, so we'd
  remember" is a safe substitute for actually running a similarity pass. You
  won't remember, and rewording during a later edit ("Type-4" semantic clones —
  same meaning, reworded) is exactly what byte-identical checks miss.
- **Do** treat "same skill name, multiple near-duplicate variants" as expected,
  not exceptional — SkillClone found 67% of name-based clone families eventually
  consolidate to one superseded "winner" version, but only slowly and not
  automatically. Build a periodic dedup pass rather than assuming drift will
  self-correct.

### 2. Split core rules from background — the SkillReducer discipline

- At authoring time, physically separate every skill into: (a) actionable
  rules/constraints the agent must follow, and (b) everything else — rationale,
  examples, templates, prior-incident narratives. SkillReducer found the majority
  of skill body content (their figure: **over 60%**) falls into bucket (b), and
  that bucket (b) content actively *degrades* agent performance when left mixed
  in with bucket (a) — removing it produced a measured 2.8% quality gain, not
  just a token saving.
- Practical rule of thumb when writing or reviewing a skill file: if a sentence
  explains *why* a rule exists, or gives a worked example, it belongs in a
  `references/` file loaded on demand — not the main skill body that's always
  read for routing/triage.
- **Every skill needs a real routing description.** SkillReducer found ~26.4% of
  skills in their sample had none at all, which is the single most expensive
  failure mode possible: without a specific description, an agent (or a router)
  can't decide relevance without loading the entire body, defeating the point of
  having a lightweight index at all. Audit for "does this skill's one-line
  description actually distinguish it from its neighbors," not just "does a
  description field exist."
- Don't add a second routing/disclosure layer on top of the existing
  description-then-full-body split. The controlled study on progressive
  disclosure for long-context agents found one layer sufficient and a second,
  deeper layer either useless or actively harmful to accuracy. If triage still
  feels expensive, the fix indicated by that finding is to shrink and sharpen the
  existing layer (better descriptions, per SkillReducer above), not stack another
  layer underneath it.

### 3. Avoid the specific traps SkillClone and SkillCenter documented

- **YAML-collision trap (SkillCenter):** two skills can be functionally identical
  in body content while looking completely unrelated in metadata (different
  `name`, `description`, `plugin`, timestamps). Any homegrown audit script that
  keys off metadata equality, or hashes the whole file including frontmatter, will
  silently pass these straight through. Strip or normalize frontmatter before
  hashing/comparing bodies, or score frontmatter and body as separate signals
  the way SkillClone does.
- **Cross-plugin/cross-repo blindness (SkillClone):** clone relationships that
  cross plugin or repository boundaries are the majority case, not the exception,
  at scale. A dedup pass scoped to "within this one plugin's skills/ folder" will
  miss most of the real duplication. Scope any dedup/similarity tooling at the
  whole-repo (or whole-organization, if you maintain several related repos) level,
  not per-plugin.
- **Security blind spot inside clone clusters:** SkillClone's own trace of
  security-relevant skills found thousands of clone links a single-skill scanner
  would never surface, because the risk lives in the *relationship* between
  files (a vulnerable pattern reproduced across many skills) rather than any one
  file in isolation. If you build clone-detection tooling for dedup purposes,
  route its output through a lightweight security review too — it's the same
  data, and the marginal cost of checking is close to zero. The 26.1%
  vulnerability rate found in one community-skill survey, and the ~1,200
  malicious-skill marketplace-infiltration incident cited in another, are reasons
  not to treat this as hypothetical.

### 4. Instrument skill edits with an actual before/after check, not just structural lint

- A structural audit (does the file have the right headers, is it under the line
  count ceiling, does `references/` exist) catches shape, not substance. Two
  independent lines of research (Skill-α's "rollback reward," SkillGrad's
  "textual gradient" diagnosis) both converge on the same missing ingredient:
  **compare agent behavior before and after the edit on a real downstream task**,
  because skill quality has no other cheap ground truth.
- This doesn't require adopting either paper's full RL/gradient machinery — the
  minimal actionable version is: keep a small held-out set of "does invoking this
  skill still produce correct behavior on task X" checks, and run them whenever
  the skill's body changes, the same way you'd run a regression test after
  editing code.

### 5. Prioritization if you can only do one thing first

If you maintain a repo like this and have to pick a starting point:
1. Run a routing-description completeness audit first (cheapest, catches the
   SkillReducer 26.4%-missing-description failure mode, immediate ROI).
2. Then run a body-content similarity pass, channel-separated (frontmatter vs.
   prose vs. code), across the whole repo — not per-plugin — to find both
   verbatim and reworded duplication.
3. Only then consider restructuring individual bloated skill files into
   core-rule-vs-background splits, since step 2 will likely reveal that some of
   the "bloat" is actually duplicate content that should be deleted/merged rather
   than reorganized in place.
4. Treat any loading-strategy change (new tiers, new routers) as a low-priority,
   evidence-required change — the research base here argues against it more than
   for it.

---

## References

The papers referenced throughout this document, with links:

1. Skill-MAS: Evolving Meta-Skill for Automatic Multi-Agent Systems —
   https://arxiv.org/abs/2606.18837
2. From Registry to Repository: How AI Agent Skills Are Written, Adapted, and
   Maintained — https://arxiv.org/abs/2607.00911
3. Skill-α: Progressive Agent Skill Generation via Reinforcement Learning —
   https://arxiv.org/abs/2608.01678
4. Is Progressive Disclosure All You Need for Long-Context Agents? —
   https://arxiv.org/abs/2607.17598
5. Agent Skills for Large Language Models: Architecture, Acquisition, Security,
   and the Path Forward (survey) — https://arxiv.org/abs/2602.12430
6. SkillReducer: Optimizing LLM Agent Skills for Token Efficiency —
   https://arxiv.org/abs/2603.29919
7. SoK: Agentic Skills — Beyond Tool Use in LLM Agents —
   https://arxiv.org/abs/2602.20867
8. SkillGrad: Optimizing Agent Skills Like Gradient Descent —
   https://arxiv.org/abs/2605.27760
9. SkillClone: Multi-Modal Clone Detection and Clone Propagation Analysis in the
   Agent Skill Ecosystem — https://arxiv.org/abs/2603.22447
10. SkillCenter: A Large-Scale Source-Grounded Skill Library for Autonomous AI
    Agents — https://arxiv.org/abs/2607.07676

Each numbered claim above traces back to one of these ten sources; the "Deeper
read" section groups the analysis by paper so you can find the specific source
for any individual finding.
