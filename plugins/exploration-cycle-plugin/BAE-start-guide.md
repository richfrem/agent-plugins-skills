# BAE Quick Start — Guided Exploration Process

Purpose
-------
A concise how-to for Business Area Experts (BAEs) to start a guided exploration session using the exploration-cycle-plugin. No technical background required.

---

How to start
------------
Just say it in plain language depending on your starting point:

### Path 1: Clean-Sheet Discovery (No code yet)
If you have a fresh idea but haven't built anything yet, say:
- **"Let's explore [your idea]."** (canonical)
- "I have an idea I want to explore"
- "Let's think through this before building anything"
- "Help me figure out what we should build"

### Path 2: Prototype Rescue & Hardening (Existing code)
If you or a developer already built a rapid or vibe-coded prototype (e.g. running on localhost:3000 or sitting in a repository) and you want to clean it up and prepare it for production-grade engineering:
- **"Harden our local prototype."**
- "I have a running prototype at localhost:3000 that needs an architecture spec"
- "Take this vibe-coded app and prepare it for enterprise delivery"
- "Rescue our local mockup and clean it up"

> [!TIP]
> **Automatic Rescue Safeguard**: If you start in Path 1 but mention during conversation that you already have a mock codebase or running prototype, the assistant will automatically redirect you to Path 2 to save you time and preserve your progress.

---

What happens next
-----------------
The session runs in four structured steps. You only move forward when you say so.

### Path 1 — Clean-Sheet Discovery Steps

**Phase 1 — Problem Framing**
Five guided questions that establish what problem you're solving, who's affected, and whether building software is even the right answer. Produces a Discovery Plan you approve before anything else happens.

**Phase 2 — Visual Blueprinting** *(optional for some session types)*
You see layout or structure options in plain language before anything is built. You pick one. Nothing gets built until you confirm.

**Phase 3 — Build** *(skipped for docs/analysis sessions)*
The AI builds what was agreed in Phase 1 and Phase 2. Each component is checked against the plan before moving to the next. You get a walkthrough before anything is locked in.

**Phase 4 — Handoff**
The session wraps up with a risk check (four yes/no questions) and a packaged output ready for whoever needs it next — whether that's you deploying it directly, a security team reviewing it, or an engineering team building from the spec.

---

### Path 2 — Prototype Rescue Steps

**Phase 1 — Browser Discovery**
An automated browser reviewer runs a visual and functional audit of your running prototype. It lists **Preservation Gems** (important business logic, interface designs, or calculations to keep) and identifies **Risky/Brittle Areas** (security gaps or fragile code to clean up). Produces a clear Discovery Report.

**Phase 2 — Interactive Interview**
The assistant asks you 5 quick questions (one at a time) about aspects code alone cannot tell us: scaling needs, target audience, sensitive data, external connections, and hosting targets.

**Phase 3 — Architectural Blueprinting**
The assistant creates formal architectural blueprints under `/specs` (including user system maps and data sequence flows in plain language). You review these and must provide your explicit sign-off to continue. **Nothing proceeds past this gate without your approval.**

**Phase 4 — Specification Packaging**
The assistant packages the final blueprints into a formal specification kit and sets up a clean, production-ready target isolated workspace (removing the risky, brittle parts while cleanly housing your preserved gems).

**Phase 5 — Isolated Migration & Safety Verification**
All rewrite work happens in an isolated workspace, not on your main branch. Each migrated piece goes through an independent quality check before it's accepted; if the same issue comes up 2-3 times, the assistant stops and brings it to you for a decision instead of retrying indefinitely. When migration is done, the assistant verifies the full safety-net test suite passes, then walks you through merging, opening a PR, keeping the branch as-is, or discarding it.

---

The five session types
----------------------
Tell the assistant which type fits, or it will ask:

| Type | Use when | Path / Phases |
|------|----------|---------------|
| **New app** | Building something from scratch | Path 1 (All 4 phases) |
| **Feature for existing app** | Adding to something that already exists | Path 1 (Phase 1 required, rest flexible) |
| **Analysis or documentation** | No code — requirements, process maps, policies, reports | Path 1 (Phases 1 & 4, Phase 2 optional) |
| **Spike** | Exploring a question or technology | Path 1 (Phase 1 required, rest flexible) |
| **Prototype Rescue** | Cleaning, auditing, and hardening a vibe-coded prototype | Path 2 (All 4 rescue phases) |

---

Choosing how the AI handles the heavy lifting
----------------------------------------------
Early on, the assistant will ask how to handle complex tasks. Three options:

1. **I have GitHub Copilot Pro** — uses `gpt-5-mini` for mechanical tasks (paid AI Credits — see `references/cheapest_models.md`), one premium request for complex ones (batched for value)
2. **No Copilot** — uses `haiku` for simple tasks, `sonnet` for complex ones
3. **I'll handle it myself** — everything happens in this session directly

If you're unsure, choose option 3. You can change later.

---

Gates and approvals
--------------------
The session will never move forward without your explicit sign-off. You'll see these checkpoints:

- **Discovery Plan approval** — Phase 1 cannot complete until you say "looks good". Nothing gets built before this.
- **Layout confirmation** — Phase 2 requires you to choose a direction before building starts.
- **Architectural blueprint sign-off (Path 2 only)** — Phase 3 requires you to review C4 context specs and give formal approval before the specifications sandbox is created.
- **Phase completion gates** — after each phase, the assistant presents a plain-language summary and waits for your confirmation before marking it complete.

If you say "this isn't going to work" at any point — the session closes cleanly, saves what was learned, and that's a valid outcome.

---

Risk check at handoff (Phase 4)
--------------------------------
Before packaging the final output, the assistant asks four yes/no questions:

1. Does this handle personal information or sensitive data?
2. Will it be used by people outside your team, or be public-facing?
3. Does it require access to production systems or high-privilege tools?
4. Does it involve financial transactions or regulatory compliance?

Based on your answers, the session determines what happens next:

- **All no** → deploy it yourself. No formal engineering needed.
- **Any yes on 1 or 2** → security review required before deployment.
- **Yes on 3 or 4** → formal engineering cycle with architectural review.
- **Idea proved unworkable** → session closes, learning preserved.

---

Re-entry: when engineering hits a blocker
------------------------------------------
If you're already in an engineering cycle and hit an "unknown unknown" — ambiguous requirements, a missed edge case, a shift in scope — say:

> "We hit a blocker and need to loop back to discovery."

The assistant opens a focused re-entry exploration session to resolve the specific gap, then hands you back to the engineering work.

---

Pre-flight environment check
-----------------------------
At the start of each session, the assistant silently checks:
- Whether the `orba/superpowers` plugin is available (required for Phase 3 build sessions)
- Whether your chosen dispatch strategy (Copilot CLI / Claude sub-agents / direct) is accessible

If anything is missing, you'll see a clear message with what to do before the session continues.

---

Key files and locations
------------------------
- `exploration/exploration-dashboard.md` — your session state; tracks which phases are done
- `exploration/discovery-plans/` — approved Discovery Plans (the hard gate)
- `DISCOVERY_REPORT.md` — Path 2 visual and functional review findings
- `specs/` — Path 2 user system context maps, sequence blueprints, and requirements
- `exploration/captures/` — requirements, stories, workflow maps, prototype notes
- `exploration/handoffs/handoff-package.md` — final output of the session
- `exploration/planning-drafts/` — optional pre-draft specs for engineering handoff (if applicable)

---

Best practices
--------------
- Let the assistant lead with one question at a time — resist the urge to explain everything upfront.
- Answer the four risk questions honestly and specifically — the session routes itself to the right delivery path based on your answers.
- If the assistant asks for a "session name", keep it short (e.g., "staff onboarding tool", "invoice approval flow").
- A "don't build this" outcome after Phase 1 is a win. You saved weeks of work.

---

Need a walkthrough?
-------------------
Say: "Walk me through an exploration session for [your idea]" and the assistant will guide you step by step.

