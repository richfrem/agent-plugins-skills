# MAF Research — Decision Record

**Closed:** 2026-05-31  
**Authoritative decision:** ADR-007 (`ADRs/007_maf_adapter_runtime_decision.md`)

This file is the narrative bridge across all MAF research artifacts in this directory.

---

## Research Timeline

| Date | Artifact | Purpose |
|------|----------|---------|
| 2026-05-30 | `initialresearch.md` | Raw MAF v1.0 component inventory — 12 areas, all providers, AGT, A2A, FIDES |
| 2026-05-30 | `microsoft-agent-framework-assessment.md` | Theoretical red team — Opus 4.6 + GPT-5.5. Verdict: do not adopt MAF. |
| 2026-05-31 | `maf-hands-on-experiment-analysis.md` | 12 working C# experiments on MAF 1.6.1, Gemini free tier. Key finding: Experiment 12 runs real plugin manifests in MAF without changes. |
| 2026-05-31 | `decision-record.md` (this file) | Five-reviewer red team synthesis. Verdict: PARTIAL OVERTURN → ADR-007. |

---

## The Pivot

The theoretical assessment concluded "do not adopt MAF." The hands-on experiments produced evidence that materially weakened that conclusion. The synthesis of five independent frontier model reviews (Opus 4.6, Gemini, GPT-4o, GPT-5.5, Grok) produced a unanimous PARTIAL OVERTURN.

**The single most important finding:** Experiment 12 proved that real `exploration-cycle-plugin` `.md` agent manifests load and run inside MAF without modifying a single file. This reframes MAF from "replacement framework" to "additional runtime adapter" — a fundamentally different architectural relationship.

**The second most important finding:** The custom Python control plane (`dispatch.py` + `state_engine.py` + `sandbox_runner.py` + `kernel.py`, ~1,090 lines) solves the same problems MAF solves, with different trade-offs. The original assessment said "avoid framework overhead" but produced equivalent overhead internally. The honest comparison is Microsoft-maintained framework vs. single-maintainer framework.

---

## What Changed vs. What Held

### Original assessment findings that still hold

- AGT is framework-agnostic — adopt it independently (now formally adopted in ADR-007)
- SKILL.md portability is real — validated across MAF, Claude Code, Copilot CLI, Gemini CLI
- Claude Code IS the Claude Agent SDK — the runtime relationship is already there
- Provider capability matrix IS lossy — stripped to intersection for Anthropic provider
- MAF's provider abstraction extension points allow routing around specific losses (Gemini `thought_signature` workaround confirms this)

### Original assessment claims overturned or materially weakened

| Original Claim | Revised Assessment |
|---------------|-------------------|
| "MAF would require abandoning the `.md` architecture" | False — Experiment 12 proves `.md` files are MAF's input, not its casualty |
| "No Azure required" was theoretical | Confirmed empirically — all 12 examples ran on Gemini free tier |
| "A local plugin architecture provides equivalent capabilities" | True, but costs ~1,090 lines of custom infrastructure vs. maintained framework |
| "MAF 1.0 assessment is current" | MAF is on 1.7.0 (shipped 3 days before this review); several "MAF doesn't do X" claims are stale |
| "`dispatch.py` subprocess pattern is the right orchestration approach" | MAF 1.7.0 `HarnessAgent` is a native equivalent — evaluation required |

### Security defects found in the custom stack (red team only)

These were not in scope for the original assessment but emerged from adversarial code review:

| Defect | Severity | File | Fix |
|--------|----------|------|-----|
| Path traversal bypass — `startswith` without boundary | Critical | `sandbox_runner.py`, C# `WorkspaceTools` | Replace with `full.relative_to(allowed_root)` |
| `check_dispatch_authorization()` not wired into `dispatch.py main()` | Critical | `dispatch.py` | Wire as fail-closed gate; add test |
| `MAX_PREMIUM_CALLS_PER_PHASE` is per-session not per-phase | High | `state_engine.py` | Track per-phase counter separately |
| No WAL checkpoint management | High | `state_engine.py` | Add periodic `PRAGMA wal_checkpoint` |
| Container runs as root | Medium | `sandbox_runner.py` | Add `--user` flag to `run_containerized()` |
| No observability anywhere | Medium | All Python control plane | Adopt OpenTelemetry (~20 lines) |

---

## Final Decision (Summary)

> **Portable manifest protocol first. Multiple runtime adapters second.**
>
> MAF is one certified adapter. Claude Code / Copilot CLI / Gemini CLI are the other adapters. The Python control plane remains the kernel after its security defects are patched to the same standard being demanded of Microsoft.

Full decision with rationale and consequences: **ADR-007**.  
Implementation work: `docs/superpowers/specs/2026-05-31-maf-synthesis-v1.4-spec.md` and `docs/superpowers/plans/2026-05-31-maf-synthesis-v1.4-plan.md`.
