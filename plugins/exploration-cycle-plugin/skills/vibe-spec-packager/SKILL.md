---
name: vibe-spec-packager
plugin: exploration-cycle-plugin
description: A package builder skill that compiles specs/ documents into standard spec-kits and scaffolds the clean target codebase sandbox.
allowed-tools: Bash, Read, Write
---

<example>
<commentary>Demonstrates compiling spec-kits and bootstrapping backend sandboxes.</commentary>
User: Package our specs and scaffold the empty backend repository
Agent: Consolidates /specs into specs/spec-kit.md, reads tech mappings to bootstrap target folders (src/, tests/, db/), and emits execution commands for obra/superpowers.
</example>

# Specification Packaging & Codebase Scaffolding (v2)

You are a Principal DevOps and Systems Scaffolding Specialist. Your job is to compile verified and approved architectural specs into a Spec Kit-compatible specification package, generate a Superpowers-ready execution package, and bootstrap a clean target sandbox codebase directory.

---

## Scaffolding & Packaging Workflow

### Step 1: Consolidate Specifications into Spec-Kit compatible package

Locate the verified specs directory and generate a fully-compliant Spec Kit package under `/speckit/`:

1.  **`speckit/constitution.md`:** Draft the architectural governing rules and principles (e.g. Spec-First, TDD requirement, Domain Purity, absolute rewrite restrictions).
2.  **`speckit/spec.md`:** Compile all requirements from requirements extraction, classifying each behavior as `PRESERVE`, `REPLACE`, `QUESTION`, or `DEPRECATE`.
3.  **`speckit/plan.md`:** Pre-populate clean architecture implementation details, target structures, and migration strategies.
4.  **`speckit/tasks.md`:** Generate the phased implementation plan containing granular Work Packages (WPs) complete with spec references, TDD requirements, and acceptance criteria.
5.  **`speckit/traceability.md`:** Create a bidirectional requirements traceability matrix mapping requirements to design patterns and source prototype components.
6.  **`speckit/open-questions.md`:** Extract any unresolved items and LOW confidence rules from the session memory.
7.  **`speckit/risk-register.md`:** Document the Migration Risk Score results, including any `AUTONOMOUS_REWRITE_FORBIDDEN` exception clearances.
8.  **`speckit/domain-lexicon.json`:** Materialize the canonical glossary lexicon mapped from `REQS.md`.
9.  **`speckit/certification-manifest.yaml`:** Consolidate all dynamic validator results.

---

### Step 2: Generate a Superpowers-Ready Handoff Package

Create the implementation discipline layer under `/superpowers/` so execution sessions require no rediscovery:

1.  **`superpowers/session-brief.md`:** Design a high-clarity introductory brief instructing fresh developer sessions exactly how to boot, execute tasks, write tests first, and verify outputs.
2.  **`superpowers/execution-protocol.md`:** Codify the sub-agent dispatch protocol, detailing simple vs complex model task-routing.
3.  **`superpowers/discipline-map.md`:** Do NOT hand-author isolation/TDD/review/merge policy prose — that reinvents what superpowers already owns and drifts out of sync with it over time. Instead, map each Work Package to the real superpowers skill that governs it, by name and invocation point:
    - **Isolation** — `superpowers:using-git-worktrees`, invoked before any WP's implementation begins
    - **TDD** — `superpowers:test-driven-development`, the Iron Law (no code before a failing test) governing every WP's implementation
    - **Review** — `superpowers:requesting-code-review`, invoked at each WP's completion (plan-alignment + quality stages)
    - **Finishing** — `superpowers:finishing-a-development-branch`, invoked once all WPs are complete, before merge/PR/keep/discard
    Note explicitly: these are the same skill names used in `phase3-execution-discipline.md` and `vibe-orchestrator-agent.md` — do not invent alternate policy documents for concepts superpowers already governs.

---

### Step 3: Run the speckit-superpowers-alignment-validator

Ensure strict coherence between the generated Spec Kit files and Superpowers instructions:
1. Verify every task in `speckit/tasks.md` references a requirement in `speckit/spec.md`.
2. Ensure every requirement has at least one task or is explicitly deferred.
3. Validate that every task contains a recommended Superpowers skill, test expectations, files scope, and verification command.
4. Write results to `reports/speckit-superpowers-alignment-report.json`.

---

### Step 4: Scaffold the Sandbox Directory

Initialize the target repository structure and copy canonical artifacts:
1. **Directories to Create:**
   - `target/domain/` (Copy already extracted pure domain code)
   - `target/tests/characterization/` (Copy behavioral tests and scrubbed JSON fixtures)
   - `target/speckit/` (Copy compiled Spec Kit specs)
   - `target/superpowers/` (Copy Superpowers execution protocol)
2. **Explain the Handoff:**
   > *"The reengineering specs have been successfully translated into a Spec Kit specification authority and a Superpowers execution package. Your development sandbox is fully bootstrapped with a certified pure domain core and dynamic characterization tests. The implementation session is ready to boot execution of plan.md Phase 0 immediately."*
