---
name: bundle-context-full
description: Aggregates full monorepo bundle with structured segmentation for deep reasoning audits.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Purpose

Prepare a **structured, lossless context bundle** optimized for deep reasoning models.

---

# Bundling Rules

## 1. Segment by domain

Split into:

- /agents
- /skills
- /evals
- /scripts
- /docs
- /prompt.md (contract)

---

## 2. Extract critical layers

For each plugin:

- SKILL.md
- evals.json
- scripts/
- agents/
- dependencies

---

## 3. Highlight enforcement artifacts

Explicitly tag:

- ADR enforcement logic
- mutation loop definitions
- sandbox paths
- halt conditions

---

## 4. Build index

Produce:

- plugin map
- dependency graph
- orchestration map

---

# Output

Return:

- structured bundle
- audit-ready segmentation
- enforcement map
