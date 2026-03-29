# Red Team Review v3: Karpathy 3-File Autoresearch — Post Round-2 Hardening

## Role & Mission
Act as a senior AI architecture and security auditor. Your mission is to evaluate whether this v3 implementation of the Karpathy autoresearch loop is robust, correctly enforced, and safe for autonomous overnight execution.

## What Changed Since Last Review (v2 -> v3)

The following round-2 findings were implemented. Please verify each is correctly closed and look for new attack surfaces introduced by the fixes:

| Finding | Fix Applied |
|---|---|
| Regex fallback exploit (frontmatter break boosts recall) | `eval_runner.py` now returns accuracy=0.0 on missing/malformed frontmatter — no fallback to full file body |
| Agent forgot to revert on DISCARD | `evaluate.py` now runs `git checkout -- SKILL.md` before `sys.exit(1)` — revert no longer depends on agent obedience |
| Weak lock enforcement (convention only) | `evaluate.py` now calls `check_locked_files()` at startup — aborts with exit 3 if `evaluate.py`, `eval_runner.py`, or `evals.json` have uncommitted modifications |
| Stale docs with `autoresearch/` paths | All references updated: `references/program.md`, `scripts/evaluate.py`, `<target>/evals/results.tsv` |
| Stale "Current State vs Target State" table | Replaced with "v2 Changes (Fixed)" history + 2 remaining known risks |
| Interactive intake missing evals.json / program.md checks | Phase 0 now checks both before starting loop, offers to scaffold if missing |

## Two Known Risks Left Open (Explicitly Not Fixed)

1. **git status lock scope** — The runtime check catches uncommitted modifications to locked files, but an agent that commits a change to `evaluate.py` mid-loop would pass the check. A SHA256-at-baseline approach would close this fully.
2. **Meta-circular risk** — This skill is used to improve itself. The frontmatter guard and lock check reduce this but a sufficiently creative agent could still find non-SKILL.md levers within the skill's own directory.

## Core Questions for the Reviewer

1. **Exploit Closure:** Are the three fixes (frontmatter hard-fail, auto-revert in evaluate.py, git status lock check) correctly implemented and sufficient? What new exploits do they open?
2. **Lock Check Blind Spot:** Is the git-status-based lock check adequate for overnight autonomous runs, or does the SHA256-at-baseline gap need to be closed first?
3. **Auto-Revert Safety:** `evaluate.py` now runs `git checkout -- SKILL.md` directly. Are there scenarios where this could revert the wrong file or cause silent data loss?
4. **Intake Interview:** The Phase 0 intake in `SKILL.md` now asks 7 questions including program.md and evals.json checks. Is the intake comprehensive enough? Any question missing that would prevent a bad loop start?
5. **Meta-Circular Threat Model:** Given the skill can evaluate itself, what is the concrete exploit path an agent would take? Is the current set of guards sufficient?

## Context Provided
The bundle contains:
- The research reference (`karpathy-autoresearch-3-file-eval.md`)
- The core evaluation skill (`skill-improvement-eval/`) including `SKILL.md`, `README.md`, `references/`, `evals/`
- The shared evaluation scripts (`scripts/eval_runner.py`, `scripts/evaluate.py`)
- The mapping and sequence diagrams (`references/diagrams/`)
- The candidate analysis skill (`eval-autoresearch-fit/`)

**Focus on what v3 still gets wrong or what new vulnerabilities the fixes introduced. High-signal findings only.**
