# Skill Context-Loading & Progressive Elaboration: 2026-09 Research Synthesis

Source task: `issue-593-context-overhead-v2` (GitHub issue #593). Produced to
satisfy that task's Definition of Done — see
`docs/plans/issue-593-context-overhead-v2-spec.md`.

## The question

Issue #593 reports ~77% of input context consumed before task-specific work
begins, and proposes **progressive elaboration** (thin core + task-triggered
loading of skills/rules) as the fix. This document tests that premise against
September 2026 research rather than assuming it.

## Sources reviewed

1. arXiv 2606.18837 — Skill-MAS: Evolving Meta-Skill for Automatic
   Multi-Agent Systems (Jun 2026)
2. arXiv 2607.00911 — From Registry to Repository: How AI Agent Skills Are
   Written, Adapted, and Maintained (Jul 2026) — empirical study, 18,463
   registry skills + 23,199 personal-use skills mined
3. arXiv 2608.01678 — Progressive Agent Skill Generation via Reinforcement
   Learning (Skill-α) (Sep 2026)
4. arXiv 2607.17598 — Is Progressive Disclosure All You Need for
   Long-Context Agents?
5. arXiv 2602.12430 — Agent Skills for Large Language Models: Architecture,
   Acquisition, Security, and the Path Forward (broad survey)
6. arXiv 2603.29919 — SkillReducer: Optimizing LLM Agent Skills for Token
   Efficiency
7. arXiv 2602.20867 — SoK: Agentic Skills — Beyond Tool Use in LLM Agents
8. arXiv 2605.27760 — SkillGrad: Optimizing Agent Skills Like Gradient
   Descent

Plus 3 `crow`-repo skill-authoring examples (`crow-agent-skill-authoring`,
`crow-agent-skill-review`, `crow-simplification-review`) and this repo's own
`.agent/rules/coding-conventions.md` and `create-skill` conventions, for
comparison.

## Verdict

**Progressive elaboration is not the primary fix issue #593 needs.** The
issue's own framing tests the wrong lever.

- Sources 5 and 7 both treat metadata-first progressive disclosure
  (Tier 1 activation metadata / Tier 2 full reference, loaded on demand) as a
  **mature, solved architectural pattern** already deployed in production
  systems (Claude Code, Semantic Kernel, LangChain) — not an open research
  problem. This repo's own `SKILL.md` + `references/` split already
  implements it.
- Source 4, the paper that directly interrogates the premise, found
  progressive disclosure **redundant when the agent harness already
  retrieves well**, and decisive only once a corpus exceeds "navigable
  scale" — critically, it also found that **adding extra routing tiers can
  reduce accuracy**, not just fail to help. Nothing in this repo's ~137-skill
  corpus indicates it has crossed that navigable-scale threshold; adding a
  deeper elaboration layer on top of the existing two-tier split is not
  supported by this finding.
- The two sources that empirically diagnose *why* skills bloat or drift
  (sources 2 and 6) both point away from loading strategy:
  - Source 2 (large-scale empirical study): skill reuse is overwhelmingly
    **one-time verbatim copy** — 53% of reused skills are never modified
    after adoption. Of the fraction that are modified, the *behavioral
    contract* (how a skill interacts with users, monitors runtime state,
    recovers from failures) is almost never touched; maintenance
    concentrates on reworking operational specs and adding inline domain
    knowledge. This is a maintenance/duplication problem, not a loading
    problem.
  - Source 6 (SkillReducer) found only 38.5% of skill body content is
    actionable core rules — the rest is background, examples, or templates
    mixed in — and named the root cause as **"the absence of separation of
    concerns in skill authoring,"** not insufficient loading-tier depth.
    Progressive disclosure is SkillReducer's *fix mechanism*, applied on top
    of compressing redundant/non-actionable content — it does not by itself
    solve the underlying authoring problem.
- Sources 1, 3, and 8 (Skill-MAS, Skill-α, SkillGrad) are about skill
  *generation* and *evolution* quality (RL-based skill authoring, iterative
  meta-skill refinement) — relevant to `os-skill-improvement` and
  `os-evolution-planner`'s methodology (see the companion recommendations
  report), but not to the context-loading question itself.

### Directly observable confirmation in this repo

During this task's own work-intake session, the same duplication pattern
predicted by source 2 was directly observed: the project's own
`/Users/richardfremmerlid/Projects/CLAUDE.md` and
`/Users/richardfremmerlid/Projects/agent-plugins-skills/CLAUDE.md` both load,
verbatim, several thousand words of identical rule text (adversarial
reasoning, destructive-action-guard, TDD, worktree-lifecycle, git-operations,
graph-planning-superpowers policies) — this is copy-drift, not a
loading-tier gap. A companion sweep inside
`plugins/agent-agentic-os/skills/` found the same pattern one level down: the
Tier 0-3 friction taxonomy, the 4-Box Qualification Gate, and
RED-GREEN-REFACTOR language are each independently restated across
`os-skill-improvement`, `self-evolution`, and `os-guide`'s SKILL.md/reference
files rather than defined once and referenced.

## Cross-reference: effect on the 4 originally-named skills

- **`create-skill`**: its scaffolding process should assert
  separation-of-concerns at creation time (core rules vs. background/
  examples/templates), per SkillReducer's finding that this is where bloat
  originates, not at audit time after the fact.
- **`audit-skill`**: currently checks structural compliance
  (`references/fallback-tree.md`/`acceptance-criteria.md` presence,
  line-count ceilings). It does not check for **duplicated policy content**
  across sibling skills or against `.agent/rules/` — crow's own
  `crow-agent-skill-review` skill treats "avoidable context bloat,
  duplicated policy" as a first-class **Medium severity** finding category.
  This is a concrete, evidence-backed candidate new invariant (see the
  companion recommendations report's Slice-2 candidate list — not
  implemented in this task).
- **`optimize-agent-instructions`**: source 2's finding (duplication/
  copy-drift, not loading strategy, is the dominant real-world
  skill-maintenance problem) is directly in this skill's mandate already —
  this document is additional evidence to cite in its methodology, and the
  CLAUDE.md duplication observed above is a live, unresolved instance of
  exactly the problem it exists to catch.
- **`create-rule`**: the rule-vs-skill boundary (rules = always-loaded
  constraints, skills = progressively-loaded procedures) is **confirmed
  sound** by this research — sources 5 and 7 both validate metadata-first
  progressive disclosure as the correct mechanism for skills. No tightening
  needed. The problem is duplicate *rule content* across multiple `CLAUDE.md`
  variants, not the rule/skill split itself.

## What this means for issue #593

The recommended direction is **not** a new or deeper progressive-elaboration
system. It is:
1. Deduplicate mirrored instruction-file content (`CLAUDE.md`/`GEMINI.md`/
   `AGENTS.md`/`.github/copilot-instructions.md`) — `optimize-agent-instructions`'s
   existing mandate.
2. Apply a SkillReducer-style content audit to skill bodies, separating
   actionable core from background/examples/templates — a candidate new
   `audit-skill` invariant, not implemented in this task (see companion
   recommendations report).
3. Treat "duplicated policy across skills" as a first-class audit finding,
   per crow's precedent, when `audit-skill`'s rubric is next revised.

None of this requires inventing a new loading-strategy layer this repo
doesn't already have.
