# BAE Quick Start: Guided Exploration

A short how-to for Business Area Experts (BAEs) starting a guided exploration session. No technical background required.

## How to start

Say it in plain language, depending on where you are.

**Path 1, clean-sheet discovery (no code yet):**
- "Let's explore [your idea]." (the canonical phrase)
- "I have an idea I want to explore."
- "Let's think through this before building anything."
- "Help me figure out what we should build."

**Path 2, prototype rescue (you or a developer already built something):**
- "Harden our local prototype."
- "I have a running prototype at localhost:3000 that needs an architecture spec."
- "Take this vibe-coded app and prepare it for enterprise delivery."

> **Automatic rescue safeguard.** If you start on Path 1 and mention that you already have a mock or running prototype, the assistant redirects you to Path 2 to save time and keep your progress.

**Technical discovery** ("diagnose this part of the codebase before we change it") also has its own route; the assistant sets it up for you.

## What happens next

You only move forward when you say so.

### Path 1: clean-sheet discovery

- **Phase 1, Problem Framing.** Guided questions, one at a time: what problem, who is affected, whether software is even the right answer. Produces a Discovery Plan **you approve before anything else happens.**
- **Phase 2, Visual Blueprinting** *(optional for some session types)*. You see layout or structure options in plain language and pick one. Nothing is built until you confirm.
- **Phase 3, Build** *(skipped for docs and analysis sessions).* The AI builds what you agreed, one part at a time, checking each against the plan. You get a walkthrough before anything is locked in.
- **Phase 4, Handoff.** A risk check and a packaged output for whoever is next: you deploying it, a security team reviewing it, or an engineering team building from the spec.

### Path 2: prototype rescue

1. **Browser discovery.** An automated reviewer audits your running prototype. It lists **Preservation Gems** (business logic, designs and calculations worth keeping) and **Risky or Brittle Areas** (security gaps, fragile code). Result: a Discovery Report.
2. **Interactive interview.** Five quick questions, one at a time: scale, audience, sensitive data, external connections, hosting.
3. **Architectural blueprinting.** Plain-language blueprints under `/specs` (system map, data flows). **Nothing proceeds without your explicit sign-off.**
4. **Specification packaging.** A neutral specification package and a clean, isolated target workspace that houses the gems and leaves the risky parts behind.
5. **Isolated migration and safety verification.** All rewrite work happens in an isolated workspace, never on your main branch. Each migrated piece is checked by an independent reviewer; if the same issue blocks it two or three times, the assistant stops and asks you. At the end the full safety-net test suite must pass, then you choose to merge, open a PR, keep the branch, or discard it.

## The session types

Tell the assistant which fits, or it will ask:

| Type | Use when | Phases |
|---|---|---|
| New app | Building from scratch | Path 1, all 4 |
| Feature for an existing app | Adding to something that exists | Path 1, phase 1 and 4 required |
| Analysis or documentation | No code: requirements, process maps, policies, reports | Path 1, phases 1, 2 and 4 |
| Spike | Exploring a question or technology | Path 1, phase 1 required, flexible |
| Prototype rescue | Cleaning, auditing and hardening a vibe-coded prototype | Path 2 |

## How the AI handles the heavy lifting

Early on the assistant picks how to handle bigger tasks: through an external CLI you have set up (its model and cost choices are handled for you), through in-session helpers, or all in this session. If you are unsure, choose all in this session; you can change later.

## Gates and approvals

The session never moves on without your sign-off:

- **Discovery Plan approval.** Phase 1 cannot finish until you say it looks good. A draft does not count, and nothing is built before approval.
- **Layout confirmation.** Phase 2 needs you to choose a direction.
- **Blueprint sign-off (Path 2).** You review the architectural blueprints before the target workspace is created.
- **Phase completion.** After each phase you get a plain summary and confirm.

If you say "this isn't going to work", the session closes cleanly, keeps what was learned, and that is a valid outcome.

## Risk check at handoff

Before packaging, the assistant asks five yes/no questions:

1. Does it handle personal or sensitive data?
2. Will people outside your team use it, or is it public-facing?
3. Does it need production systems or high-privilege tools?
4. Does it involve financial transactions or regulatory compliance?
5. Does it make decisions about people (hiring, eligibility)?

Your answers decide the path:

- **All no:** deploy it yourself; no formal engineering needed.
- **Yes on 1, 2 or 5:** security review (plus an ethics review for 5) before deployment.
- **Yes on 3 or 4, or yes on both 1 and 2:** a formal engineering cycle; a risk summary is written first and you cannot deploy directly.
- **Idea proved unworkable:** the session closes and the learning is kept.

## Re-entry: when engineering hits a blocker

If engineering finds an ambiguous requirement, a missed edge case or a shift in scope, say: "We hit a blocker and need to loop back to discovery." The assistant opens a focused re-entry session for that gap, then hands you back to engineering.

## Pre-flight check

At the start of each session the assistant silently checks that an isolated workspace is possible (needed for builds into existing code) and that your chosen way of delegating work is available. If something is missing you get one clear message with what to do.

## Key files

- `exploration/exploration-dashboard.md`: your session state (a read-only view of the state engine)
- `exploration/discovery-plans/`: approved Discovery Plans (the hard gate)
- `exploration/captures/`: requirements, stories, workflow maps, prototype notes
- `exploration/handoffs/handoff-package.md`: the final output
- `exploration/planning-drafts/`: optional pre-drafts for engineering
- `DISCOVERY_REPORT.md`, `specs/`: Path 2 audit findings and blueprints

## Best practices

- Let the assistant lead with one question at a time; resist explaining everything upfront.
- Answer the risk questions honestly and specifically; the route depends on them.
- Keep a session name short ("staff onboarding tool", "invoice approval flow").
- A "don't build this" outcome after Phase 1 is a win: you saved weeks.

## Need a walkthrough?

Say: "Walk me through an exploration session for [your idea]."
