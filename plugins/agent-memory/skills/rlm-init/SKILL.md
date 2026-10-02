---
name: rlm-init
plugin: agent-memory
description: Interactive RLM cache initialization for setting up a project semantic cache or adding a profile.
allowed-tools: Bash, Read, Write
---

# RLM Cache Initialization (`rlm-init`)

Initializes a new Recursive Language Model (RLM) semantic cache for zero-dependency high-speed memory.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Setup Modes](#setup-modes)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Zero-Dependency**: Uses standard library Python 3.8+ only; no external databases or daemons required.
2. **Profile Storage**: Profiles default to `.agent/learning/rlm_profiles.json`.
3. **Scripted Writes**: Never create cache markdown files manually; use `scripts/inject_summary.py`.

## Quick start

Check existing coverage or initialize a profile:

```bash
python3 scripts/inventory.py --profile project
```

## Setup Modes

- **Mode A (Standalone)**: RLM only. Fast keyword lookup across dense file summaries.
- **Mode B (RLM + vector-db)**: RLM keyword pre-filter into vector semantic search.
- **Mode C (RLM + obsidian-wiki-engine)**: RLM as wiki concept distiller.
- **Mode D (Super-RAG)**: Full stack combining RLM, vector store, and wiki concept nodes.

## Workflow

1. **Requirements Discovery**: Select target directories, file types, and cache destination.
2. **Profile Configuration**: Define profile entry in `.agent/learning/rlm_profiles.json`.
3. **Manifest Creation**: Define include/exclude patterns in `<name>_manifest.json`.
4. **Audit Gaps**: Run `python3 scripts/inventory.py --profile <name>` to list uncached files.
5. **Initial Distillation**: Deep read and inject summaries via `python3 scripts/inject_summary.py`.
6. **Report Readiness**: Confirm initialized profile paths and ready state to the user.

## Verification

Confirm 100% cache coverage with the inventory script:

```bash
python3 scripts/inventory.py --profile project
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for RLM cache bootstrapping.
- [rlm-bootstrap-guide.md](references/rlm-bootstrap-guide.md) — Comprehensive bootstrap manual and mode details.
