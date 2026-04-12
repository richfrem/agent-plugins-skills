# Technical HARD-GATE Enforcement

This document defines the canonical enforcement rule and redirect text for all exploration-cycle agents.
Reference this file in any agent that can initiate capture, build, or synthesis work.

## Gate Condition

Before any of the following work begins:
- Capturing requirements or business rules
- Building a prototype (any component)
- Running user story derivation
- Dispatching handoff-preparer-agent
- Any Phase 3+ activity

**Check:** Does `exploration/discovery-plans/` exist and contain at least one `.md` file?

- **YES** → read the most recent `.md` file as the source of truth. Proceed.
- **NO** → use the exact redirect text below. STOP. Do not offer workarounds.

## Canonical Redirect Text (use verbatim)

> "Before we can build or capture anything I need to understand what we're building first.
> Can we start with a short Discovery Planning Session? It usually takes 10–15 minutes and
> it makes sure everything we create after this is exactly what you need."

## Rules

1. Do NOT offer workarounds ("we can skip the plan", "just give me a rough idea").
2. Do NOT continue below the redirect. Return control to the SME and wait.
3. Do NOT try to infer or reconstruct a Discovery Plan from prior conversation — only a real file in `exploration/discovery-plans/` satisfies the gate.
4. If an impatient SME says "just build it" or "skip the planning" — use the redirect text again, unchanged. Politely firm.

---

## Tier 3 Hard Stop — Canonical Redirect

This gate applies when the TierGate assessment in Phase 4 determines **Tier 3 (High Risk)** — i.e., Q3 (high-privilege access) or Q4 (financial/compliance) answered "yes", or both Q1 and Q2 answered "yes".

### Canonical Redirect Text (use verbatim)

> "This exploration has assessed as high risk — it needs a formal engineering review before anything is deployed or shared outside this session.
> I'll generate a risk summary now so the right team has what they need to take this forward safely.
> You cannot deploy this directly. The next step is handing the risk summary and handoff package to your engineering or security team."

### Rules

1. Do NOT write the handoff package without generating `tier3-risk-summary.md` first.
2. Do NOT allow the SME to proceed to deployment — the Tier 3 outcome is "Formal engineering cycle required", not "deploy after review".
3. If the SME insists on bypassing: repeat the redirect text. Do not soften it.
4. If the SME does not understand why they're being stopped: explain in plain terms which specific TierGate answer triggered it and what that means.
5. The risk summary is not optional and is not a formality — it is the first section of the handoff package for a Tier 3 outcome.
