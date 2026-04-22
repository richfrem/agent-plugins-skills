---
name: exploration-handoff
description: >
  Interactive co-authoring skill for the narrow end of the exploration funnel.
  Synthesizes session briefs, BRDs, story sets, and prototype notes into a
  structured handoff package targeted at the correct downstream consumer
  (e.g., formal software specs, strategic roadmaps, or process documentation).
allowed-tools: Bash, Read, Write
---

## Dashboard Intercept

Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

- **If the file EXISTS:** Read it silently and check the `**Status:**` line.
  - If `**Status:** Complete` → the prior session has ended. Proceed with this skill's
    standalone flow as normal.
  - Otherwise → an active session is in progress. Stop immediately. Do not continue here.
    Announce to the user:
    > "It looks like you have an active Exploration Session in progress. Let me take you back
    > to your session dashboard so we can keep your progress on track."
    **Return to the orchestrator.** Use the Skill tool: `skill: "exploration-workflow"`.
    After invoking it, stop generating output from this skill — do not continue below.

- **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.

<example>
<commentary>User has finished exploration and wants to produce a handoff package.</commentary>
User: I finished my exploration session, help me write the handoff package.
Agent: [invokes exploration-handoff, synthesizes session artifacts into structured handoff]
</example>

<example>
<commentary>User wants to synthesize all exploration artifacts for a specific downstream consumer.</commentary>
User: Synthesize our session captures into a handoff for the engineering team.
Agent: [invokes exploration-handoff, targets handoff at engineering/spec downstream]
</example>

<example>
<commentary>Starting a new session routes to exploration-session-brief, not this skill.</commentary>
User: Let's kick off a new exploration session.
Agent: [invokes exploration-session-brief, NOT exploration-handoff]
</example>

# Exploration Handoff (Interactive Co-Authoring)

> **Note:** This skill runs fully interactively via Claude — no script needed. `execute.py` is a planned batch-mode convenience wrapper that hasn't been built yet, but the core skill works now. The [handoff-preparer-agent](../../agents/handoff-preparer-agent.md) provides an alternative agentic dispatch path.

## When This Phase Is Required vs Optional

- **Greenfield (Type 1):** Always required — the handoff package is how the engineering team knows what to build.
- **Brownfield (Type 2):** Optional — if the same person/agent is doing both exploration and implementation, formal handoff may be unnecessary. The SME decides during session setup.
- **Analysis/Docs (Type 3):** Always required — the handoff IS the primary output of the session (requirements, process maps, analysis reports, stories, rules, workflow diagrams, or whatever the non-software deliverable is).
- **Spike (Type 4):** Optional — depends on whether findings need to be communicated to others.

If this phase was skipped during session setup, it will be marked `- [~]` in the dashboard and the orchestrator will not route here.

This skill provides a structured, 3-stage interactive workflow for synthesizing exploration artifacts into a concise Handoff Package.

**Important Note for Agents:** Do NOT passively run a bash script or dump a massive block of markdown. You must guide the user through the following 3 stages.

## Stage 0: Scribe Activities (Automated Capture Before Synthesis)

First, read the dashboard `**Session Type:**` field. This determines what Stage 0 does.

**Non-software sessions** (session type contains "process", "strategic", "risk/compliance", or "legacy analysis"):
- Skip prototype-related captures.
- Check whether `exploration/captures/` contains any of: problem-framing.md, brd-draft.md, workflow-diagram.md.
- If captures are missing, announce: *"Before I package the handoff, let me capture the key outputs from our session."* Then invoke `business-requirements-capture` using the Discovery Plan as input. Skip `user-story-capture` unless the SME specifically wants user stories as an output.
- Proceed to Stage 1.

**Software sessions where Phase 3 ran** (Greenfield, Brownfield — feature, website):
- Silently check for `exploration/prototype/`.
- If the prototype directory exists, run the following in sequence. Announce each briefly:
  > "Capturing [activity name] first — this gives us the raw material for the handoff."

  1. **Business Requirements Capture** (invoke `business-requirements-capture`)
     - Extract business rules and functional requirements from Discovery Plan and prototype
     - Output: `exploration/captures/business-requirements.md`

  2. **User Story Capture** (invoke `user-story-capture`)
     - Translate validated prototype behaviours into user stories
     - Output: `exploration/captures/user-stories.md`

  3. **Business Workflow Doc** (invoke `business-workflow-doc` — **only** if the Discovery Plan describes a process flow with sequential steps or decision branches)
     - Output: `exploration/captures/workflow-diagram.md`

  Once complete, announce: *"Requirements and stories captured. Now let's put together your handoff package."*

**Software sessions where Phase 3 was skipped** (discovery-only, analysis, or spike with no build):
- Skip Stage 0 entirely. Proceed to Stage 1.

The Stage 0 outputs are now available as source artifacts for synthesis.

## Stage 1: Context Gathering (Routing)
Before synthesizing anything, establish what you're working with and where it's going. Ask both questions in a single message:

1. **Target audience:** Who receives this handoff and what will they do with it?
   - *Engineering team (internal AI harness)* — feeding into Spec-Kitty, Superpowers, or similar AI-assisted engineering workflow
   - *Engineering team (traditional SDLC)* — a dev team who will scope, estimate, and build using standard project management
   - *Executive or sponsor* — making a go/no-go or budget decision
   - *Operations or process team* — implementing a process change or updating a workflow or policy
   - *Architecture or platform team* — planning a modernisation, replatforming, or migration
   - *Security team* — reviewing before deployment
   - *Product or design team* — scoping a discovery sprint or next prototype iteration
   - *Other* — describe briefly

2. **Available artifacts:** Which exploration documents exist? (Check `exploration/` directory — list what you find.) Common sources: session brief, BRD draft, prototype notes, user story set, business-workflow diagrams.

After the user responds: read each artifact file they identify. If a file doesn't exist, note it explicitly and ask whether to proceed without it or pause until it's available. Do not invent content for missing artifacts.

## Stage 1.5: Risk & Rigor Assessment (TierGate)

Before synthesis, perform a mandatory structured risk assessment. The result determines the **delivery path** — not every exploration routes to formal engineering.

**Work through the following checklist with the SME. Ask each question and require a yes/no answer plus one sentence of evidence before moving on. Do not accept "maybe" or "it depends" — help the SME reach a concrete answer.**

> "Before we finalize the handoff, I need to ask you four quick questions to figure out what happens next. Answer yes or no for each:"

| # | Question | SME Answer | Evidence (one sentence) |
|---|----------|-----------|------------------------|
| 1 | Does this handle personal information or sensitive data (names, emails, health, financial)? | yes / no | |
| 2 | Will it be used by people outside your immediate team, or is it public-facing? | yes / no | |
| 3 | Does it require access to production systems or high-privilege tools (admin, payment, auth)? | yes / no | |
| 4 | Does it involve financial transactions or regulatory compliance? | yes / no | |
| 5 | Does this system make or influence decisions about people — hiring, performance, access, eligibility — or could it reflect or amplify bias in historical data? | yes / no | |

**Tier determination (based on filled checklist):**
- All "no" → **Tier 1 (Low Risk)** — direct deployment, lightweight self-assessment
- Any "yes" on Q1 or Q2 → **Tier 2 (Moderate Risk)** — security review required before deployment
- "yes" on Q1 + Q2, or any "yes" on Q3 or Q4 → **Tier 3 (High Risk)** — mandatory formal engineering cycle
- Any "yes" on Q5 → **Tier 2 minimum** — an ethics review (fairness, bias, and people-impact assessment) is required in addition to any security review. Q5 alone does not trigger Tier 3, but combined with any "yes" on Q3 or Q4 it does.
- SME explicitly says the idea isn't viable → **Throwaway / Fail Fast**

Record the tier in the handoff package under a `## Risk Assessment` section using this exact format:

```
## Risk Assessment

**Tier:** [1 / 2 / 3 / Throwaway]
**Checklist answers:**
- PII or sensitive data: [yes/no] — [evidence]
- External users or public-facing: [yes/no] — [evidence]
- High-privilege access: [yes/no] — [evidence]
- Financial or compliance: [yes/no] — [evidence]
- People decisions or bias risk: [yes/no] — [evidence]
**Rationale:** [one sentence from SME]
**Delivery Path:** [exact text: "Direct deployment" / "Security review before deployment" / "Ethics + security review before deployment" / "Formal engineering cycle (Opportunity 4)" / "Session closed — learning preserved"]
```

**If any TierGate answer is missing or vague:** insert `[NEEDS HUMAN INPUT]` in that row and do NOT finalize the handoff until resolved.

**If the SME selects Throwaway:** Skip synthesis (Stages 2–4). Instead, write a brief `exploration/handoffs/handoff-package.md` documenting: what was explored, what was learned, and why the idea was killed. This is the "fail fast and cheap" outcome — preserve the learning.

**For Tier 2 and Tier 3 projects**, note in the handoff package that a deeper risk and
harm assessment may be required by the organization's security team. Reference:
`AI-Security-and-Safety-Lab/Mitigations/enterprise-governance-and-education/risk-and-harm-assessment/`
for the full enterprise assessment workflow (taxonomy mapping, control selection, sign-off).
The inline assessment here is a lightweight first pass — it determines the delivery path,
not the full security posture.

**For Q5 "yes" (people decisions or bias risk):** Add a specific note to the handoff:
> "This system makes or influences decisions about people. Before deployment, an ethics review is required in addition to any security review — specifically covering fairness, potential for bias in historical data, unintended use cases, and applicable legal constraints (e.g., labor law, anti-discrimination regulations). A security review alone is not sufficient."

**Tier 3 hard stop:** If Tier 3 is determined, do not finalize or write the handoff package silently. Follow the Tier 3 Hard Stop protocol in `agents/handoff-preparer-agent.md` — generate a `tier3-risk-summary.md` first, then include it as the opening section of the handoff package.

## Stage 2: Synthesis and Iterative Refinement
Your job is to extract the signal relevant to the target audience — not to copy-paste source documents.

**Signal** = confirmed decisions, hard constraints, and questions that block the next phase.
**Noise** = background context, rationale already obvious to the audience, and anything marked `[UNCONFIRMED]` in source documents.

1. **Outline First:** Propose a numbered list of items that *must* be communicated to this specific audience. For each item, state whether it is a confirmed decision, a constraint, or an open question. Ask the user: *"Does this outline reflect what we confirmed? Anything missing or wrong?"*
2. **Curate:** Apply changes. If the user promotes an `[UNCONFIRMED]` item, ask them to confirm it first before including it as fact.
3. **Draft section by section:** For each section, write a concise draft (3–6 sentences or a short list). Cite the source artifact for any major claim (e.g., "per session brief"). Ask: *"Accurate? Anything to add or cut?"* Apply edits before moving on.

## Stage 3: Reader Testing (Consumer Validation)
Ensure the handoff gives the downstream consumer what they need to act:

1. **Predict blockers:** Based on the target audience type, predict exactly 3 questions they will ask after reading this document that are NOT answered by it. Use audience-specific framing:
   - *Engineering (AI harness)*: spec questions ("What are the exact acceptance criteria for story X?", "What's the data model?")
   - *Engineering (traditional SDLC)*: scoping questions ("How many story points is this?", "What are the external dependencies?", "Who is the product owner?")
   - *Executive/sponsor*: decision questions ("What's the fallback if this fails?", "What does it cost to build vs. not build?")
   - *Operations/process team*: ownership questions ("Who owns step 3?", "What's the escalation path?", "What training is needed?")
   - *Architecture/platform team*: technical questions ("What integrations must survive?", "What's the data migration path?")
   - *Security team*: risk questions ("What data is stored and where?", "Who has admin access?")
   - *Product/design*: scope questions ("What's explicitly out of scope?", "Which user type is primary?")

2. **Surface gaps:** Present the 3 questions: *"If [audience] reads this, they'll immediately ask: [Q1], [Q2], [Q3]. Are these answered?"*
3. **Resolve:** For each unanswered question, ask whether to (a) answer it inline, (b) add it to `## Unresolved Ambiguity` for the execution phase to own, or (c) confirm it's intentionally out of scope.

## Stage 4: Delivery Path Formatting

The formatting depends on both the Risk Tier from Stage 1.5 and the session type from the dashboard. Check both before formatting.

---

**Step 4a — Detect the output type:**

Read `**Session Type:**` from the dashboard (or infer from the artifacts). Apply the matching format:

| Session type | Output format |
|---|---|
| Greenfield / Brownfield — feature / Website | Software handoff (see Tier-based formats below) |
| Brownfield — legacy analysis | Legacy analysis format (see below) |
| Analysis — process | Process change recommendation format (see below) |
| Analysis — strategic | Strategic recommendation format (see below) |
| Analysis — risk/compliance | Risk and compliance format (see below) |
| Spike | Summary of findings + decision recommendation |

---

**Tier 1 (Low Risk — Direct Deployment):**
Format as a lightweight deployment brief:
- What was built and what it does
- How to deploy or run it
- What to watch for in the first week
- Self-assessment checklist the BAE can complete independently

---

**Tier 2 (Moderate Risk — Security Review):**
Format with a security-review-ready section:
- Data flows and what data is touched
- Access patterns and authentication/authorisation requirements
- Known risks and mitigations already in place
- Red team checklist: questions the security team will ask
The primary consumer is the security team, not an engineering team.

---

**Tier 3 (High Risk — Formal Engineering SDLC):**
This package goes to a development team. It must be complete enough for them to scope and begin a formal engineering project without needing to re-interview the SME.

Ask the user if they use a specific engineering harness:
1. **Spec-Kitty / Superpowers** → format for the AI engineering harness (spec.md, plan.md structure)
2. **External / traditional dev team** → use the SDLC package format below

**Tier 3 — SDLC package (for an external or traditional dev team):**

Produce a single handoff document containing all of the following sections. Mark any section that could not be filled from session artifacts as `[NEEDS HUMAN INPUT]`:

```
## 1. Executive Summary
[2-3 sentence problem statement and proposed solution — written for a PM or tech lead]

## 2. Business Context
[Why this matters, who asked for it, what happens if it isn't built]

## 3. User Stories
[Full story set from exploration — As a / I want / So that format with acceptance criteria]

## 4. Business Rules
[Numbered list of rules the system must enforce — sourced from BRD]

## 5. Process Flows
[Key workflows the system supports — reference workflow-diagram.md if it exists]

## 6. Functional Requirements
[Numbered list — what the system must do]

## 7. Non-Functional Requirements
[Performance, accessibility, security, compliance requirements]

## 8. Constraints
[Hard limits — technology choices already made, integrations required, data residency, etc.]

## 9. Prototype Notes
[What the SME validated, surprises found, corrections made — from prototype-notes.md]

## 10. Risk Assessment
[The completed TierGate checklist and rationale — verbatim from Stage 1.5]

## 11. Open Questions / Unresolved Ambiguity
[Decisions the engineering team must make before they can begin — consolidated from all captures]

## 12. Out of Scope
[Explicitly what this project does NOT cover]
```

After producing the package, ask the SME:
> "Is there an AI engineering harness your team uses — like Spec-Kitty or Superpowers? If so, I can reformat this into the structure it expects."

---

**Legacy Analysis Handoff (Brownfield — legacy analysis):**
The consumer is an architecture or engineering team planning modernisation. Format as:

```
## 1. System Overview
[What the system does, how old it is, what technology it runs on]

## 2. Current Capabilities
[What the system does well and must be preserved in any replacement]

## 3. Known Pain Points
[What it does poorly, what causes the most friction]

## 4. Integration Map
[What other systems it connects to and how]

## 5. Data and Storage
[What data it holds, estimated volume, sensitivity]

## 6. Modernisation Options Considered
[What approaches were discussed — rewrite, replatform, re-host, retire, replace]

## 7. Recommended Path
[The SME-approved recommendation — with rationale]

## 8. Open Questions for Architecture
[Decisions the engineering team needs to make before planning begins]

## 9. Risk Assessment
[From TierGate — verbatim]
```

---

**Process Change Recommendation (Analysis — process):**
The consumer is the team or person responsible for changing the process. Format as:

```
## 1. Problem Summary
[What's broken, for whom, and what it costs them]

## 2. Root Cause
[From the Intervention Check — what's actually causing the problem]

## 3. Recommendation
[The specific change proposed — plain language, actionable]

## 4. How to Implement
[Step-by-step or role-by-role — who does what differently starting when]

## 5. What Success Looks Like
[How you'll know the change worked — measurable if possible]

## 6. Risks and Considerations
[What could go wrong, what resistance to expect, dependencies]

## 7. Related Software Needs (if any)
[If a technology component is also needed, describe it here — separate from the process change]
```

---

**Strategic Recommendation (Analysis — strategic):**
The consumer is a decision maker or leadership team. Format as:

```
## 1. The Question
[The decision or strategic question that was explored]

## 2. Context
[Why this matters now, what triggered the exploration]

## 3. What We Know
[Confirmed facts and evidence from the session]

## 4. What We Don't Know
[Unresolved uncertainties that may affect the decision]

## 5. Options Considered
[The alternatives that were weighed]

## 6. Recommendation
[The preferred path — with rationale]

## 7. Next Steps
[Concrete actions, owners, and timing]

## 8. Open Questions
[What leadership or stakeholders need to decide]
```

---

**Throwaway (Fail Fast):**
Already handled in Stage 1.5 — no further formatting needed.

## Gotchas

- **TierGate Q5 (bias/people decisions) does not trigger Tier 3 alone**: Q5 "yes" → Tier 2 minimum, plus ethics review. Only combined with Q3 or Q4 "yes" does it escalate to Tier 3. Agents sometimes over-escalate Q5-only cases.
- **Stage 0 runs twice if child skills also run it**: `business-requirements-capture` and `user-story-capture` are invoked in Stage 0 but they also have their own session-type detection. Pass the session type explicitly in the invocation instruction to avoid double-questioning.
- **Reader Testing question 3 is often skipped**: Stage 3 says predict 3 questions — in practice agents predict 1–2 and move on. Enforce all 3 before asking the SME if they're answered.
- **Throwaway path skips Anti-Hallucination Rules**: When the SME selects Throwaway in Stage 1.5, the skill jumps to write a brief handoff. This brief still must not invent content — apply Anti-Hallucination Rules even for the throwaway path.
- **Return to orchestrator after standalone use**: If the dashboard does NOT exist (standalone use), the skill must not attempt to invoke `exploration-workflow`. Check for the dashboard before emitting the return signal.

## Anti-Hallucination Rules
- Do NOT invent requirements or rules that were not present in the Stage 1 input sources.
- Maintain traceability: When stating a major constraint or rule, briefly mention which exploration source it came from.
- Be explicitly clear about what is a confirmed decision versus what is an optimistic assumption.

## Final Output Destination
Write the approved markdown content to: `exploration/handoffs/handoff-package.md` (or a timestamped equivalent).

## Completion — Return to Orchestrator

Once the handoff package is approved and written to `exploration/handoffs/handoff-package.md`:
1. Announce: "Your handoff package is complete — Phase 4 is done."

Output this machine-readable block so the orchestrator can parse phase completion:

~~~
## HANDOFF_BLOCK
PHASE: 4
STATUS: COMPLETE
OUTPUT: exploration/handoffs/handoff-package.md
RISK_TIER: [1 / 2 / 3 / Throwaway]
DELIVERY_PATH: [Direct deployment / Security review before deployment / Ethics + security review before deployment / Formal engineering cycle (Opportunity 4) / Session closed — learning preserved]
CONSOLIDATED_GAPS: [count of [NEEDS HUMAN INPUT] markers in handoff]
~~~

2. If operating within an active Exploration Session (i.e., `exploration/exploration-dashboard.md`
   exists and `**Status:**` is not `Complete`):
   1. Say to the user:
      > "Returning to your session dashboard now."
   2. **Return to the orchestrator.** Use the Skill tool: `skill: "exploration-workflow"`.
      After invoking it, stop generating output from this skill.
      If the Skill tool is not available in your harness, tell the user:
      *"Please run `/exploration-workflow` to continue your session."*

If operating standalone (no dashboard file, or `**Status:** Complete`), the skill is complete.
