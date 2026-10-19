# Evolution Log — Agent Loops

| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |
|------|------|-------------------|-------|-----------|---------|
| 2026-10-04 | Tier 1 | Need deterministic DAG runner and graph planner with join barriers, transactional worktrees, and pure stdlib schema validation. | Added graph_runner.py, validate_manifest.py, graph-planner and graph-execution skills. | Feature + tests + docs | RESOLVED — 100% test pass rate with full schema parity and process-group signal handling. |
| 2026-10-04 | Tier 1 | Strategy selection relied on keyword guessing and fragile regex parsing without validation or explicit answers. | Implemented deterministic select_strategy.py with explicit answers, 72-combination table-driven test, and canonical patterns.json catalog with symlink parity verification. | Feature + tests + docs | RESOLVED — All 72 diagnostic combinations covered, invalid inputs fail closed. |
| 2026-10-04 | Tier 1 | Swarm execution lacked path containment, dry-run state safety, and post-command synchronization. | Hardened swarm_run.py with stdlib frontmatter, directory traversal guards, serial post-command locks, external state directories, and PATTERN_GUIDE alignment. | Hardening + tests | RESOLVED — All safety checks and isolation tests pass. |
| 2026-10-18 | Tier 1 | Review of graph-planner/graph-execution found verifier-hash bypass, no-op mutation failure, unexpressible mutation fallbacks, destructive rollback in --no-workspace runs, and wrong reference files. | Fixed runner and validator, added test_graph_fixes.py (12 regression tests), per-skill acceptance criteria and fallback tree, corrected topology rules, schema descriptions, SKILL.md files, and evals. | Fix + tests + docs | RESOLVED - 71 orchestration tests and 14 strategy-artifact tests pass. |


