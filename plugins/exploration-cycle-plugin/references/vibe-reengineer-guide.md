# Vibe Reengineering Guide & Safety Protocols

Deep reference for `vibe-reengineer` covering truth hierarchy, migration risk scoring, reengineering modes, and the 7-step pipeline.

## Contents

- [Governance & Canonical Truth Hierarchy](#governance--canonical-truth-hierarchy)
- [Reengineering Modes (A through E)](#reengineering-modes-a-through-e)
- [Migration Risk Scoring & Safety Proxies](#migration-risk-scoring--safety-proxies)
- [Forbidden Autonomous Rewrite Categories](#forbidden-autonomous-rewrite-categories)
- [Economic Dispatch & Confidence Tagging](#economic-dispatch--confidence-tagging)
- [The 7-Step Reengineering Pipeline](#the-7-step-reengineering-pipeline)

---

## Governance & Canonical Truth Hierarchy

In any conflict, higher levels take precedence:
1. `specs/REQS.md` (Canonical Business Truth): Equations, constraints, glossary.
2. `tests/characterization/` (Canonical Behavioral Truth): Executable behavior assertions.
3. `/domain` model (Canonical Architectural Truth): Pure domain logic.
4. Handoff / Spec documents: Derived artifacts.
5. Prototype code: Exploratory evidence only.

---

## Reengineering Modes (A through E)

- **Mode A (Preservation)**: Containerize vibe code with characterization tests; keep structure intact.
- **Mode B (Stabilization)**: Add tests, linting, error boundaries, and environment isolation.
- **Mode C (Modularization - Recommended)**: Decouple into `/domain`, `/application`, and `/infrastructure` layers.
- **Mode D (Full Replatform)**: Complete target sandbox rewrite (e.g. Node to Go/Python) from captured business rules.
- **Mode E (Domain Extraction Only)**: Extract pure mathematical rules/schemas into standalone zero-dependency module.

---

## Migration Risk Scoring & Safety Proxies

Score each dimension 1 (Low) to 5 (High):
- **Coupling Proxy**: Count `import`/`require` statements (<2 = 1, 2-5 = 3, >5 = 5).
- **Side Effects Proxy**: Scan for DB queries, network calls, global state (pure = 1, single DB = 3, mixed = 5).
- **Hidden State Proxy**: Scan for mutable closures, cookies, local storage (pure functions = 1, standard classes = 3, mutable closures = 5).
- **Test Coverage Proxy**: Match slice against `/tests/characterization/` (>90% = 1, 40-90% = 3, <40% = 5).
- **Runtime Dynamism Proxy**: Check for reflection, `eval()`, dynamic imports (typed static = 1, dynamic = 5).

### Risk Classification:
- **5–12**: SAFE (proceed autonomously).
- **13–18**: CAUTION (require targeted assertions and observer logs).
- **19–25**: DANGEROUS (require manual review and confirmation).

---

## Forbidden Autonomous Rewrite Categories

**AUTONOMOUS_REWRITE_FORBIDDEN**: The agent must NEVER autonomously refactor:
1. Authentication & authorization logic.
2. Financial billing and payment gateway equations.
3. Cryptography or security hashing schemes.
4. Regulatory compliance logging.

---

## Economic Dispatch & Confidence Tagging

- Tag inferred rules: `[CONFIDENCE: HIGH]`, `[CONFIDENCE: MEDIUM]`, or `[CONFIDENCE: LOW]`.
- Low-confidence rules must be recorded in `session-memory/ambiguity-ledger.md`.
- Route simple discovery/parsing to fast models; reserve deep reasoning models for slice extraction and compilation repair.

---

## The 7-Step Reengineering Pipeline

1. **Step 1: Discovery & Telemetry**: `vibe-browser-audit` & `runtime-observer`.
2. **Step 2: Behavioral Safety Net**: `vibe-behavioral-test-capture`.
3. **Step 3: Consolidate Requirements**: `specs/REQS.md` & `domain-lexicon.json`.
4. **Step 4: Pure Domain Core Extraction**: `vibe-domain-extractor`.
5. **Step 5: Architectural Scaffolding**: `vibe-spec-packager` (ADRs & session memory).
6. **Step 6: Progressive Vertical Slice Migration**: `vibe-slice-migrator` & certification.
7. **Step 7: Final Safety Net Verification**: 100% characterization test parity.
