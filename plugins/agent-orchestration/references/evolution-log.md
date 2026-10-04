# Evolution Log — Agent Loops

| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |
|------|------|-------------------|-------|-----------|---------|
| 2026-10-04 | Tier 1 | Need deterministic DAG runner and graph planner with join barriers, transactional worktrees, and pure stdlib schema validation. | Added graph_runner.py, validate_manifest.py, graph-planner and graph-execution skills. | Feature + tests + docs | RESOLVED — 100% test pass rate with full schema parity and process-group signal handling. |
| 2026-10-04 | Tier 1 | Strategy selection relied on keyword guessing and fragile regex parsing without validation or explicit answers. | Implemented deterministic select_strategy.py with explicit answers, 72-combination table-driven test, and canonical patterns.json catalog with symlink parity verification. | Feature + tests + docs | RESOLVED — All 72 diagnostic combinations covered, invalid inputs fail closed. |
| 2026-10-04 | Tier 1 | Swarm execution lacked path containment, dry-run state safety, and post-command synchronization. | Hardened swarm_run.py with stdlib frontmatter, directory traversal guards, serial post-command locks, external state directories, and PATTERN_GUIDE alignment. | Hardening + tests | RESOLVED — All safety checks and isolation tests pass. |

