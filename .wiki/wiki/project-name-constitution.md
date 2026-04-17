---
concept: project-name-constitution
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/software-dev/command-templates/constitution.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.348388+00:00
cluster: phase
content_hash: 9d13254690fcdb9e
---

# [PROJECT_NAME] Constitution

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Create or update the project constitution through interactive phase-based discovery.
---
**Path reference rule:** When you mention directories or files, provide either the absolute path or a path relative to the project root (for example, `kitty-specs/<feature>/tasks/`). Never refer to a folder by name alone.

*Path: [templates/commands/constitution.md](templates/commands/constitution.md)*

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## What This Command Does

This command creates or updates the **project constitution** through an interactive, phase-based discovery workflow.

**Location**: `.kittify/memory/constitution.md` (project root, not worktrees)
**Scope**: Project-wide principles that apply to ALL features

**Important**: The constitution is OPTIONAL. All spec-kitty commands work without it.

**Constitution Purpose**:
- Capture technical standards (languages, testing, deployment)
- Document code quality expectations (review process, quality gates)
- Record tribal knowledge (team conventions, lessons learned)
- Define governance (how the constitution changes, who enforces it)

---

## Discovery Workflow

This command uses a **4-phase discovery process**:

1. **Phase 1: Technical Standards** (Recommended)
   - Languages, frameworks, testing requirements
   - Performance targets, deployment constraints
   - ≈3-4 questions, creates a lean foundation

2. **Phase 2: Code Quality** (Optional)
   - PR requirements, review checklist, quality gates
   - Documentation standards
   - ≈3-4 questions

3. **Phase 3: Tribal Knowledge** (Optional)
   - Team conventions, lessons learned
   - Historical decisions (optional)
   - ≈2-4 questions

4. **Phase 4: Governance** (Optional)
   - Amendment process, compliance validation
   - Exception handling (optional)
   - ≈2-3 questions

**Paths**:
- **Minimal** (≈1 page): Phase 1 only → ≈3-5 questions
- **Comprehensive** (≈2-3 pages): All phases → ≈8-12 questions

---

## Execution Outline

### Step 1: Initial Choice

Ask the user:
```
Do you want to establish a project constitution?

A) No, skip it - I don't need a formal constitution
B) Yes, minimal - Core technical standards only (≈1 page, 3-5 questions)
C) Yes, comprehensive - Full governance and tribal knowledge (≈2-3 pages, 8-12 questions)
```

Handle responses:
- **A (Skip)**: Create a minimal placeholder at `.kittify/memory/constitution.md`:
  - Title + short note: "Constitution skipped - not required for spec-kitty usage. Run /spec-kitty.constitution anytime to create one."
  - Exit successfully.
- **B (Minimal)**: Continue with Phase 1 only.
- **C (Comprehensive)**: Continue through all phases, asking whether to skip each optional phase.

### Step 2: Phase 1 - Technical Standards

Context:
```
Phase 1: Technical Standards
These are the non-negotiable technical requirements that all features must follow.
This phase is recommended for all projects.
```

Ask one question at a time:

**Q1: Languages and Frameworks**
```
What languages and frameworks are required for this project?
Examples:
- "Python 3.11+ with FastAPI for backend"
- "TypeScript 4.9+ with React 18 for frontend"
- "Rust 1.70+ with no external dependencies"
```

**Q2: Testing Requirements**
```
What testing framework and coverage requirements?
Examples:
- "pytest with 80% line coverage, 100% for critical paths"
- "Jest with 90% coverage, unit + integration tests required"
- "cargo test, no specific coverage target but all features must have tests"
```

**Q3: Performance and Scale Targets**
```
What are the performance and scale expectations?
Examples:
- "Handle 1000 requests/second at p95 < 200ms"
- "Support 10k concurrent users, 1M daily active users"
- "CLI operations complete in < 2 seconds"
- "N/A - performance not a primary concern"
```

**Q4: Deployment and Constraints**
```
What are the deployment constraints or platform requirements?
Examples:
- "Docker-only, deployed to Kuberne

*(content truncated)*

## See Also

- [[project-name]]
- [[project-name]]
- [[project-name]]
- [[project-ecosystem-constitution-v4]]
- [[feature-specification-documentation-project---project-name]]
- [[project-ecosystem-constitution-v4]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/software-dev/command-templates/constitution.md`
- **Indexed:** 2026-04-17T06:42:10.348388+00:00
