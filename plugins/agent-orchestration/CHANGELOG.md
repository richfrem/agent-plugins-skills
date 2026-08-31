# Changelog - agent-orchestration/

All notable changes to this project will be documented in this file.

## [2.3.0] - 2026-08-30

### Added
- New skill `graph-execution`: Deterministic state machine (DAG) execution primitive with formal node lifecycle, Proposal Mode invariants, transactional worktree sandboxing, Verifier Sovereignty, and Asymmetric Persistence via worktree knowledge export.
- New skill `select-loop-strategy`: Master 6-gate decision tree helping agents evaluate task characteristics and pick the optimal execution topology (solo, dual-loop, swarm, red-team, meta-learning, or graph-execution).
- Unit test suite `tests/test_loop_strategies.py` verifying pattern contracts, line budgets, and frontmatter standards across all skills.
- Progressive disclosure references directory and symlinks for `triple-loop-learning`.

### Changed
- Streamlined `orchestrator`: Integrated `graph-execution`, cross-linked `select-loop-strategy`, and removed dead CLI warnings for unfulfilled `scan` and `bundle` subcommands.
- Updated `PATTERN_GUIDE.md`: Documented complete 8-pattern matrix including deterministic graph execution and strategy routing.
- Standardized `co-pilot-loop/evals/evals.json` to canonical root JSON list format.

### Fixed
- Fixed copy-paste typo in `learning-loop/SKILL.md:L88` where Option B (Dual Loop) erroneously directed agents to `triple-loop-learning` instead of `dual-loop`.

## [2.2.0] - 2026-06-28

### Added
- Standardized `evolution-log.md` and `map-debt.md` registration hooks.
- Parametrization unit tests for engine models.

### Fixed
- Silently broken YAML split handling in `swarm_run.py`.
- Deprecated standalone `gemini` CLI engine mappings.
- Brittle regex frontmatter parser in `closure_guard.py`.
- Bidirectional symlink loops and broken persona references.
