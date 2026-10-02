# Discovery Planning Reference & Question Tracks

Deep reference for `discovery-planning` providing session type routing, question tracks, and the discovery plan specification.

## Contents

- [Session Type Fork](#session-type-fork)
- [Assumptions Check](#assumptions-check)
- [Legacy / Brownfield Track](#legacy--brownfield-track)
- [Feature Addition Track](#feature-addition-track)
- [Process Intervention Track](#process-intervention-track)
- [Strategic Planning Track](#strategic-planning-track)
- [Risk Assessment Track](#risk-assessment-track)
- [Open Exploration Track (Spike)](#open-exploration-track-spike)
- [Standard Greenfield Track](#standard-greenfield-track)
- [Discovery Plan Specification](#discovery-plan-specification)
- [Gotchas & Edge Cases](#gotchas--edge-cases)

---

## Session Type Fork

Check in this order:
1. `## Session Context` block passed by the orchestrator (`Session type:`).
2. `**Session Type:**` field in `exploration/exploration-dashboard.md`.
3. If neither is available, ask the user.

| Session Type | Question Track |
|---|---|
| Greenfield / website / new app | **Standard Track** |
| Brownfield — feature addition | **Feature Addition Track** |
| Brownfield — legacy analysis / replatforming | **Legacy/Brownfield Track** |
| Analysis/Docs — process | **Process Intervention Track** |
| Analysis/Docs — strategic | **Strategic Planning Track** |
| Analysis/Docs — risk/compliance | **Risk Assessment Track** |
| Spike | **Open Exploration Track** |

---

## Assumptions Check

Ask before the first track question:
1. Have you already checked whether something like this exists in your current systems or tools?
2. Is this about access to information that's hard to find, or information that genuinely doesn't exist yet?

---

## Legacy / Brownfield Track

- **LQ1**: What does the current system do that people genuinely depend on — the things that would break something if they disappeared?
- **LQ2**: What's broken, missing, or causing pain right now? What makes people frustrated with it today?
- **LQ3**: Who are the people who truly understand how this works — and are they still here?
- **LQ4**: What other systems, tools, or processes does this connect to? What would break if we changed or removed it?
- **LQ5**: What's the goal — replacing it, supplementing it, documenting it for safety, or planning a migration?
- **LQ6**: Are there hard constraints on the path forward — compliance, surviving integrations, external deadlines?

---

## Feature Addition Track

- **FQ1**: Tell me about the system we're adding to — what does it do today and who uses it?
- **FQ2**: What's the feature or change you want to add? What problem or opportunity is driving this now?
- **FQ3**: Who will use this new feature and what does success look like for them?
- **FQ4**: Are there things the current system does that this change must not break?
- **FQ5**: Are there any technical constraints or integration requirements I should know about?

---

## Process Intervention Track

- **PQ1**: Walk me through how the process works today — step by step. Where does it break down or create the most friction? (Evaluate software vs process/people issue).
- **PQ2**: Who is affected by this process — both doing the work and waiting for the outcome?
- **PQ3**: What does "fixed" look like?
- **PQ4**: Are there constraints on what can change (regulatory, organizational)?
- **PQ5**: Has anyone tried to fix this before? What happened?

---

## Strategic Planning Track

- **SQ1**: What decision needs to be made, and when? What happens if it isn't made?
- **SQ2**: Who are the key stakeholders with a say or who are affected?
- **SQ3**: What constraints are non-negotiable?
- **SQ4**: What does a good outcome look like in 12–24 months?
- **SQ5**: What's the risk of doing nothing, or delaying?

---

## Risk Assessment Track

- **RQ1**: What's the risk or compliance gap we're assessing?
- **RQ2**: What regulations, standards, or internal policies apply?
- **RQ3**: What controls exist today and where are the gaps?
- **RQ4**: What would a regulator, auditor, or risk committee need to see to sign off?
- **RQ5**: Are there constraints on the remediation path?

---

## Open Exploration Track (Spike)

- **OQ1**: What's the question or hypothesis we're investigating?
- **OQ2**: What do we already know — data, context, prior attempts?
- **OQ3**: What would a useful answer look like at the end of this session?
- **OQ4**: Are there boundaries on the investigation?

---

## Standard Greenfield Track

- **Q1**: What problem are we trying to solve for the people we serve?
- **Q2**: Who's involved — who uses this, who gives the final say, who else is affected?
- **Q3**: What does a great outcome look like when this is working the way you imagined?
- **Q4 (Intervention Check)**: Is this genuinely a new tool need, or a process/policy simplification?
- **Q5**: If we had to pick the three most important things this must deliver — what would they be?
- **Q6**: Are there any hard rules, limits, or things we absolutely cannot do?

---

## Discovery Plan Specification

Target: `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`

```markdown
# Discovery Plan — [Date]
**Session type:** [Greenfield / Brownfield / Analysis / Spike]

## Problem Statement
[2-3 plain language sentences]

## Intervention Type
- Primary: [Software / Process / Policy / Communication / Strategic / Legacy]
- Supporting: [Secondary intervention, if mixed]
- Software needed: yes / no / not yet determined

## Stakeholders
- Users: [...]
- Decision maker: [...]
- Affected parties: [...]

## Success Criteria
[Plain language criteria]

## Must-Have Requirements
[Numbered list]

## Constraints and Rules
[Numbered list]

## Open Questions
[Numbered list]
```

---

## Gotchas & Edge Cases

- **Assumptions Check is not a gate**: If unsure, note as open question and continue.
- **Legacy skips Intervention Check**: LQ5 covers intervention intent.
- **Spikes need prior plan context**: Do not discard prior iteration notes.
