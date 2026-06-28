# Changelog - agent-loops

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-06-28

### Added
- Standardized `evolution-log.md` and `map-debt.md` registration hooks.
- Parametrization unit tests for engine models.

### Fixed
- Silently broken YAML split handling in `swarm_run.py`.
- Deprecated standalone `gemini` CLI engine mappings.
- Brittle regex frontmatter parser in `closure_guard.py`.
- Bidirectional symlink loops and broken persona references.
