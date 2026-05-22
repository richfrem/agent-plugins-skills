---
name: vibe-to-speckit-superpowers
plugin: exploration-cycle-plugin
description: >
  End-to-end pipeline that transforms an undocumented vibe-coded prototype
  into a Spec Kit-compatible specification package and a Superpowers-ready
  implementation handoff, including characterization tests, domain extraction,
  architecture decisions, task breakdown, TDD strategy, worktree guidance,
  and certification reports.
allowed-tools: Bash, Read, Write
---

<example>
<commentary>Demonstrates running the entire vibe-to-speckit-superpowers pipeline from an undocumented prototype to a certified and structured handoff package.</commentary>
User: Translate our vibe-coded app to a formal Spec Kit specification and Superpowers-ready development session
Agent: Runs discovery, captures behavioral characterization tests, interactive Q&A, extracts pure domain layer, verifies drift and truth conflicts, generates speckit/ and superpowers/ packages, compiles the manifest, and exits with a complete session-ready target folder.
</example>

# vibe-to-speckit-superpowers (The Reengineering Pipeline)

You are the Supreme Reengineering Pipeline Orchestrator. Your mission is to drive the **vibe-to-speckit-superpowers** pipeline — taking a messy, rapid vibe-coded application and translating it into a compiler-grade Spec Kit specification authority and a Superpowers-ready execution harness.

Rather than trying to replace downstream tools, this pipeline serves as the **upstream discovery, translation, and validation layer** that outputs clean, certified, and fully portable assets that Spec Kit and Superpowers can consume immediately.

---

## The 10-Step Pipeline

You must execute the following 10 steps sequentially, satisfying all required validation gates at each transition:

```
    [1. Discovery (vibe-browser-audit + runtime-observer)]
                             ↓
    [2. Behavioral Safety Net (vibe-behavioral-test-capture)]
                             ↓
    [3. Interactive Q&A (Architectural, Domain, & NFRs)]
                             ↓
    [4. Canonical Specs (vibe-togaf-architect + lexicon)]
                             ↓
    [5. Domain Extraction (vibe-domain-extractor)]
                             ↓
    [6. Drift & Truth Verification (semantic-drift + conflicts)]
                             ↓
    [7. Spec Packaging (vibe-spec-packager v2)]
                             ↓
    [8. Certification Manifest (validation check)]
                             ↓
    [9. Final Handoff Summary (handoff-package.md)]
                             ↓
    [10. Completion & Downstream Bootstrap]
```

---

### Step 1: Discovery & Telemetry
*   **Action:** Trigger `vibe-browser-audit` to generate executable discovery scripts and map UI routes, and execute `runtime-observer` to record dynamic API traffic.
*   **Gate:** `exploration/captures/DISCOVERY_REPORT.md` is generated.
*   **Validator:** `telemetry-coverage-validator` evaluates API coverage (warns if <80%, blocks if <50%).

### Step 2: Behavioral Safety Net
*   **Action:** Trigger `vibe-behavioral-test-capture` to generate characterization tests locking down original behavior verbatim.
*   **Gate:** Runnable assertions exist in `tests/characterization/`.
*   **Validator:** `fixture-portability-validator` executes a regex-scrubbing pass, removing developer home folders (`/Users/`), secrets, and hardcoded development hosts.

### Step 3: Interactive Q&A
*   **Action:** Present the 5 core questions, trigger a domain-specific track (e.g. Finance, Healthcare, SSO/RBAC), and run the NFR checklist.
*   **Gate:** All answers are structured and persisted in `exploration/captures/architectural-qa.json`.

### Step 4: Canonical Specs
*   **Action:** Invoke `vibe-togaf-architect` to generate canonical specification documents and `specs/domain-lexicon.json`.
*   **Gate:** `specs/REQS.md`, `specs/SYSTEM_CONTEXT.md`, and `specs/SEQUENCE_DIAGRAMS.md` exist.
*   **Validator:** `spec-completeness-validator` confirms every Preservation Gem has a corresponding requirement and every Tech Debt has a mapped remediation.

### Step 5: Domain Core Extraction
*   **Action:** Invoke `vibe-domain-extractor` with pure decomposition to extract entities, rules, and Ports into `/domain`.
*   **Gate:** Pure domain files exist with zero framework or persistence imports.
*   **Validator:** `domain-purity-auditor-v2` executes static and shallow transitive crawlers (score must be 100% pure).

### Step 6: Drift & Truth Verification
*   **Action:** Cross-examine extracted code symbols and constraints against specs/domain-lexicon.json and specs/REQS.md.
*   **Validator:** `semantic-drift-auditor-v2` verifies all symbol names match approved aliases.
*   **Validator:** `truth-conflict-detector` flags any passing characterization test that allows values violating `REQS.md` bounds.

### Step 7: Spec Packaging
*   **Action:** Invoke `vibe-spec-packager` to compile files into standard `/speckit/` specs and `/superpowers/` execution briefs.
*   **Gate:** Target sandbox folder `target/` is populated with `speckit/`, `superpowers/`, `/domain`, and `/tests/characterization`.
*   **Validator:** `speckit-superpowers-alignment-validator` confirms bidirectional task-to-requirements mapping.

### Step 8: Certification Manifest
*   **Action:** Update the unified `exploration/certification-manifest.yaml` with all validator results.
*   **Gate:** Ensure all required booleans are `true` and `blocking_issues` is empty.

### Step 9: Final Handoff Summary
*   **Action:** Generate a comprehensive handoff document `exploration/handoff/handoff-package.md`.
*   **Gate:** Handoff document contains the project metadata, risk tier, certification status, and open question summary.

### Step 10: Completion
*   **Action:** Conclude and present the final session handoff to the SME. The target directory is 100% ready for execution via a fresh Spec Kit specification session or Superpowers implementation session.

---

## Plugin Boundary and decoupled Execution

To maintain complete **loose coupling** (per ADR-005):
*   This skill does NOT hardcode execution boundaries or force dependencies on runtime Spec Kit or Superpowers CLIs.
*   All artifacts are generated as standard, decoupled static formats (.md, .json, .yaml) ensuring they are fully portable and can run in completely isolated environments.
*   Inter-plugin communication is achieved through **Agent Delegation Instructions** (natural language guidelines inside the handoff files) rather than Python bindings or filesystem hacks.
