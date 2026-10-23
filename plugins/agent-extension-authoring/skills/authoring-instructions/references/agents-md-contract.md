# Root Instruction File Contract (`AGENTS.md` / `CLAUDE.md`)

## 1. Overview & Purpose
This contract governs root instruction files across all agent ecosystems. It establishes `AGENTS.md` as the single canonical source of truth for repository instructions, with platform files (`CLAUDE.md`) acting as minimal bridges to avoid duplication and context bloat.

## 2. Line Ceilings & Budgets
Root instruction files are loaded into agent context at session start. To maximize prompt efficiency and instruction adherence:
- **Target Budget**: `<= 100 lines`
- **Advisory Threshold (WARN)**: `> 120 lines`
- **Hard Policy Ceiling (FAIL)**: `> 200 lines` (vendor guideline ceiling)

> Note: The budget evaluates the **transitive eager payload**: root file plus recursively resolved `@imports` or eager includes.

## 3. Five-Category Content Classification
Root files must follow a strict separation of concerns:

| Content Type | Definition & Criteria | Canonical Home | Audit Invariant |
|:---|:---|:---|:---|
| **Invariants** | Non-negotiable MUST / NEVER constraints (1 line each) | Root file (`AGENTS.md`), inline | Invariant statement must be fully readable inline using uppercase modal constraint tokens (`MUST`, `NEVER`, `ALWAYS`, `DO NOT`, `REQUIRED`, `PROHIBITED`); link points to rationale/examples in `.agent/rules/`. Never hide the invariant itself behind an unread link. |
| **Orientation** | Essential build/test commands, environment quirks, key paths (<= 16 lines total across Architecture and Commands) | Root file, inline | Minimal commands only; no multi-step walkthroughs. |
| **Scoped Conventions** | Style rules or constraints applying only to specific languages or subdirectories | Path-scoped rules (`.claude/rules/*.md` with `paths:`, or nested `AGENTS.md` in subdirectories) | Must not bloat the global root context. |
| **Procedures** | Workflows requiring multi-step sequential actions (>3 steps or branching logic) | Specialized Skills (`SKILL.md` in client harness or global profile) | No inlined execution guides in root file. |
| **Reference Material** | Schemas, detailed catalogs, historical records, pitfall lists | Reference documents (`references/` or `docs/architecture/`) | Referenced via lazy pointers with clear "Read when..." triggers. |

## 4. Canonical Authority & Platform Bridges
1. **Single Source of Truth**: `AGENTS.md` is the primary and authoritative instruction file.
2. **Platform Bridges (`CLAUDE.md`)**:
   - `CLAUDE.md` must be a minimal bridge pointing to `AGENTS.md` (e.g., `Read [AGENTS.md](AGENTS.md).` or `@AGENTS.md`).
   - Hard limit: `<= 5 lines`.
   - Never duplicate full-text rules or instructions across `CLAUDE.md` and `AGENTS.md`.

## 5. Timelessness & Environment Agnosticism
Root files are long-lived instructions:
- **Zero Historical Calendar Dates**: No timestamps, changelogs, post-mortem dates (e.g. `YYYY-MM-DD`).
- **Zero Machine Paths**: No absolute developer paths (e.g. `/Users/`, `/home/`, `C:\`). All paths must be repository-relative.
- **Zero ASCII Directory Trees**: Repository architecture belongs in `architecture.md` or scoped docs.

## 6. Skeleton Order for Root Files
When generating (`create-agents-md`) or auditing (`audit-agents-md`), enforce this fixed skeleton:
1. `# AGENTS.md` (with `## Overview` paragraph describing stack and purpose)
2. `## Architecture & Layout` (high-level pointer to `architecture.md` / key subdirectories, <= 8 lines)
3. `## Core Commands` (essential build, test, and dev commands, <= 8 lines)
4. `## Non-Negotiable Rules / Invariants` (concise 1-line uppercase MUST/NEVER statements linking to detailed rules)
5. `## On-Demand Skills & Reference Index` (lazy pointers with "Read when..." triggers)
