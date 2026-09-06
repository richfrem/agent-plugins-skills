# ADR-007: MAF as Optional Certified Runtime Adapter

## Status
Accepted — 2026-05-31

## Context

A theoretical assessment (2026-05-30) recommended against adopting Microsoft Agent Framework (MAF), concluding that the plugin architecture's standalone Python enforcement scripts provided equivalent capabilities without framework lock-in.

Following that assessment, 12 working C# experiments were built against MAF 1.6.1 using Gemini (free tier, no Azure). Those experiments were then submitted to five independent frontier model reviewers (Opus 4.6, Gemini, GPT-4o, GPT-5.5, Grok) as an adversarial red team. All five independently reached the same verdict: **PARTIAL OVERTURN**.

Key findings from the red team:

1. **Experiment 12 is decisive.** The real `exploration-cycle-plugin` agent manifests loaded into MAF without modifying a single `.md` file — with per-agent skill scoping, alias resolution, handoff routing, and session continuity. MAF is a host for the `.md` architecture, not a replacement for it.

2. **The custom Python stack has become framework-sized.** `dispatch.py` + `state_engine.py` + `sandbox_runner.py` + `kernel.py` totals ~1,090 lines of custom orchestration infrastructure solving problems MAF + AGT solve with vendor-maintained, 13,000-test-backed code. The original recommendation said "avoid framework overhead" but produced equivalent overhead internally.

3. **The assessment was based on MAF 1.0.** The experiments ran on 1.6.1. MAF 1.7.0 shipped May 28, 2026 with `HarnessAgent` (native equivalent to `dispatch.py`'s subprocess pattern) and A2A `AgentSession` improvements (native equivalent to `state_engine.py` task leasing). The framework is releasing weekly.

4. **"Manifest first, runtime second" is the correct principle — and it supports MAF adoption.** The `.md` manifest files are the portable interface definition. Every reviewer arrived at: MAF should be one certified runtime adapter alongside Claude Code CLI, Copilot CLI, and Gemini CLI. Adding MAF increases portability; it does not reduce it.

5. **Critical security defects found in the custom stack.** The red team identified a path traversal bypass (`startswith` without boundary enforcement, bypassable with sibling paths), `check_dispatch_authorization()` defined but not wired into `dispatch.py main()`, and a `MAX_PREMIUM_CALLS_PER_PHASE` counter that is per-session rather than per-phase.

## Decision

**MAF is not adopted as the primary orchestration kernel. It is adopted as an optional certified runtime adapter.**

The architecture principle is formalized as:

> **Portable manifest protocol first. Multiple runtime adapters second.**

Specifically:

1. **`.md` agent manifests remain the source of truth.** The same files work in Claude Code CLI, Copilot CLI, Gemini CLI, and MAF. No format change required.

2. **`SKILL.md` remains the portable capability format.** Validated across all four runtimes.

3. **The Python control plane (`kernel.py`, `state_engine.py`, `dispatch.py`, `sandbox_runner.py`) remains the authoritative runtime kernel** — after the security defects identified by the red team are patched (see ADR-007 implementation plan).

4. **MAF is a certified host for `.md` manifests.** The C# harness from Experiment 12 is the reference implementation. It can be used for .NET/enterprise contexts, cross-runtime demonstrations, and structured multi-agent composition where typed handoffs and compile-time validation are needed.

5. **Selected MAF patterns are ported to the Python control plane** regardless of MAF adoption status:
   - Three-way alias index for agent resolution (stem / stem-without-`-agent` / frontmatter `name:`)
   - Handoff envelope standardization (last 8 turns, 300 chars/turn)
   - Per-agent skill scoping with character budget cap
   - OpenTelemetry instrumentation
   - AGT (`agent-governance-toolkit`) as the governance layer

6. **AGT is adopted immediately** (framework-agnostic, no MAF dependency). It replaces the custom `check_dispatch_authorization()` with 13,000-test-backed deterministic policy enforcement.

7. **MAF 1.7.0 `HarnessAgent` is evaluated** as a potential replacement for `dispatch.py`'s subprocess orchestration in a future phase.

## Consequences

**Positive:**
- The `.md` manifest architecture gains a fourth certified runtime (MAF) without any format changes
- Critical security defects in the custom stack are formally identified and tracked
- AGT adoption replaces ~60 lines of custom auth with vendor-maintained governance
- OpenTelemetry adoption eliminates production blindness
- The architectural principle ("manifest first, runtime second") is durable regardless of which runtimes survive

**Negative:**
- The custom Python control plane must be maintained and hardened rather than replaced
- MAF adoption as a secondary runtime adds a .NET dependency for that adapter (C#)
- The "one more runtime to test against" burden increases proportionally with the number of certified adapters

**Constraints:**
- ADR-004 (self-contained plugins) still applies: no runtime cross-plugin paths
- ADR-005 (loose coupling) still applies: skills must not hard-depend on whether MAF is the active runtime
- The Python control plane security patches (path traversal, dispatch authorization wiring, premium call counter) are prerequisites before the control plane can be considered equivalent in rigor to framework middleware

## Reassessment Triggers

Revisit this ADR if any of the following conditions become true:

1. MAF 1.7.0 `HarnessAgent` prototype evaluation shows it reduces dispatch complexity by >50% with acceptable provider capability loss
2. AGT adoption reveals governance gaps in the current Python control plane that AGT cannot cover without MAF middleware
3. A second team member joins and the maintenance asymmetry argument changes materially
4. MAF's provider capability matrix reaches full parity (Background Responses, File Search available for Anthropic provider)
5. Build 2026 announcements (June 2–3, 2026) materially change the frontier SDK landscape

**Review cadence:** On each MAF major release. Current release velocity is weekly — quarterly review is too slow.
