---
name: dependency-analysis
description: Map relationships between Forms, generate dependency graphs, and retrieve direct/indirect dependency chains. Includes Discovery mechanisms and Dependency Severity Routing.
disable-model-invocation: false
tier: 1
---

# Dependency Analysis

## Overview

This skill maps the complex web of relationships in the Oracle Forms ecosystem, enforcing safe impact analysis before major architectural changes.

## Phase-Based Execution

### Phase 1: Guided Discovery Interview (Intent Classification)
Do not immediately run scripts. Start by gathering context:
1. **Target Identification**: Are we analyzing a single Form, a Library, or an entire module subdirectory?
2. **Depth Intent**: Are we looking for direct (Level 1) callers, or a deep recursive impact graph?
3. **Outcome Goal**: Are we verifying safe deletion, planning a migration, or tracing a bug?

Proceed to script execution ONLY when the goal is verified.

### Phase 2: Action Execution
Choose your script based on the discovery intent:
- `/dependency-analysis_retrieve-dependency-graph`: Generate or retrieve the full network graph for deep impact traces.
- `/dependency-analysis_investigate-direct-dependencies`: Extract immediate callers (Level 1) for rapid impact assessment.

## Dependency Severity Framework (Graduated Autonomy)
As you evaluate the returned dependency graphs, classify the discovered nodes using caller count (`C`) and outbound call count (`O`):
- **ORPHANED**: If `C == 0 AND O == 0`. Safe to mark for deletion or aggressive refactoring. (Autonomy: Execute implicitly).
- **STANDARD**: If `(0 < C <= 5) AND (Module(Caller) == Module(Target))`. Proceed with standard impact analysis. (Autonomy: Execute and report).
- **CRITICAL**: If `(C > 5) OR (Module(Caller) != Module(Target))`. High risk of regression. (Autonomy: STOP. Ask User for explicit consent before proposing any code deletions or changes).
- **CIRCULAR**: If a path exists where Target calls Node `N` and Node `N` calls Target. Severe architectural code smell. (Autonomy: STOP. Flag immediately to the user as a primary risk).

## Source Transparency & Next Actions
Conclude execution by listing:
**Sources Checked:** [List of forms analyzed]
**Sources Unavailable:** [List of unparsed binary components]

**Next Action Menu:** 
1. Proceed with modification
2. Trace a specific caller deeper
3. Export graph to Markdown/Mermaid
