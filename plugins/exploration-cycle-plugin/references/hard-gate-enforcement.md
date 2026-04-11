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
