Here's a real-world assignment that will stress-test the plugin end-to-end across its z## Assignment: Waitlist & Early Access System for a Developer Tool

**Trigger phrase to kick off the session:**

> "I want to build a waitlist and early access system for a new developer CLI tool we're launching. People can sign up, we manually review and admit them in batches, they get an invite code to activate their account, and we need a basic admin view to manage the queue. We have an existing users table in Postgres. I need to understand what we're actually building before writing any specs."

---

**Why this is a good test:**

It's the exact canonical scenario the optimizer was tuned on (`baseline-001-waitlist`), which means you'll immediately see whether the real system matches the 11-iteration optimization results. You'll know very quickly if the Decision Pre-fills rule and Gap Consolidation Rule are actually working as the evals claimed.

**What to watch for at each phase:**

**Phase 0 — intake-agent.** Does it correctly classify this as `brownfield` (existing users table) rather than `greenfield`? Does it ask about the existing system before drafting the brief? Does it fill the `Decision Pre-fills` section or leave it blank? A blank Decision Pre-fills section is the single biggest predictor of downstream gap inflation per the eval history.

**Phase 1 — capture passes.** After Pass 2 (BRD), run `check_gaps.py --threshold 3` manually and count the `[NEEDS HUMAN INPUT]` markers. The eval history baseline was 6 across captures; post-optimization was 0. If you get more than 3 on a first real run, the gap consolidation rule isn't transferring from simulated to real sessions.

**Phase 2b — business rule audit.** This is the first real-world test of the rewritten audit agent. Give it a prototype that deliberately introduces one clear violation: something like "the invite code field has no expiry" when the BRD should say invites expire after 7 days. Watch whether it catches it, correctly marks it CONTRADICTED, and emits the exact `[NEEDS HUMAN INPUT]` marker that triggers the `check_gaps.py --threshold 0` hard stop.

**Phase 3 — Narrowing Gate.** The fifth readiness check ("Remaining unknowns are acceptable — Evidence: [rationale]") requires human judgment. This is where you'll find out whether the system actually helps you make a decision or just generates paperwork.

**Phase 4 — handoff.** The real quality signal. Read it as if you were a spec author who wasn't in the room for the exploration session. Ask yourself: could you write a formal spec from this handoff without scheduling another meeting?

---

**Introduce this deliberate complication mid-session:**

After Pass 2 produces the BRD, tell the agent:

> "Actually, we also need to support team-based signups — a company signs up as a unit, not just individual developers."

This tests whether the gap checker correctly fires on Pass 3 (the brief changed scope mid-session), whether the orchestrator follows the recovery procedure Step 4 exception (scope boundary changed → re-run Pass 1), and whether the handoff correctly captures the team/individual split as a consolidated open decision rather than a `[NEEDS HUMAN INPUT]` scattered across every section.

---

**Success criteria for the test:**

The session is a pass if the handoff you receive at the end is something you'd actually hand to a spec author — problem clear, constraints listed, key decisions either resolved or explicitly flagged as open, no invented requirements. It's a fail if the handoff is a polished-looking document that a spec author would immediately ask follow-up questions about that should have been answered during exploration.