# Exploration Cycle: Guided Discovery for Business Experts

The **agent-exploration-cycle** plugin puts structured, AI-guided exploration in the hands of Subject Matter Experts (SMEs) and Business Area Experts (BAEs). It bridges the maturity gap between a raw idea (the *vibe*) and a contract an engineering team can build from (the *spec*), and it recognises that **not every problem needs software and not every solution needs formal engineering.**

It implements the GenAI Double Diamond: **Diamond 1** is this plugin (explore, define, prototype, validate); **Diamond 2** is the engineering cycle your team already uses. A risk-tiered handoff sits between them.

## The belief

The people closest to a problem should explore the solution. Today an expert with an idea enters a queue: an analyst translates, a designer interprets, a developer builds what they understood, and every handoff adds translation error. Here:

- **Any expert** can run a structured discovery session with AI guidance, no technical background needed.
- **Cheap AI workers** do the analyst, designer and documentation work.
- **The expert stays in control.** The AI asks, the human decides, and every phase has a gate that needs an explicit yes.
- **The output is what the problem needs**: a prototype, a process map, a policy recommendation, a requirements document, or "don't build this".

## Five skills

| Skill | Use it to |
|---|---|
| `running-exploration-cycle` | Start or resume a session: intake, the Discovery Plan gate, phase routing, state |
| `capturing-business-requirements` | Capture requirements (BRD), user stories, workflow diagrams, prototype observations |
| `building-interactive-prototypes` | Choose a layout, build a clickable prototype component by component, walk through it |
| `handing-off-to-engineering` | Assess risk (tiers 1 to 3), package the handoff, run read-only technical discovery, scope a re-entry |
| `reengineering-vibe-code` | Rescue an existing vibe-coded prototype: audit, safety-net tests, REQS contract, pure domain, certified slices |

Four independent agents stay at plugin level because their value is independence: `business-rule-audit-agent`, `certification-verifier`, `domain-purity-auditor`, `semantic-drift-auditor`.

## Three ways in

1. **Pre-build discovery** (nothing built yet): `running-exploration-cycle`, phases below.
2. **Rescue** (a working prototype exists): `reengineering-vibe-code`. If you start on path 1 and mention existing code, you are redirected here.
3. **Technical discovery** (a refactor, bug or subsystem): read-only diagnosis in `handing-off-to-engineering`, producing a `DIAGNOSTIC_BRIEF.md`.

## The loop

| Phase | What happens | Gate |
|---|---|---|
| 0 Intake | Short interview; session brief | You confirm the brief |
| 1 Discovery Plan | Questions one at a time, with an **Intervention Check**: is software even the right answer? Requirements, stories and workflow maps are captured | You approve the plan (a DRAFT never counts) |
| 2 Visual Blueprinting | Three plain-language layout or structure options | You choose |
| 3 Prototype | Built component by component in an isolated workspace, then a walkthrough | Rules audited against the prototype |
| 4 Handoff | Risk assessment and a packaged output | You approve; validators pass |

Session types change which phases run: **Greenfield** (all), **Brownfield** (1 and 4 required), **Analysis/Docs** (1, 2, 4), **Spike** (1 required, flexible). At any point, "this isn't going to work" closes the session cleanly. Failing fast and cheap is a valid outcome. The most expensive mistake is building the right thing for the wrong problem; the UK Blue Badge project nearly built a document-verification portal until designers found the real problem was confusing policy wording.

## Fast by default, safe by design (risk tiers)

Five yes/no questions, each with a one-sentence evidence note: personal or sensitive data (Q1), public-facing or outside the team (Q2), production or high-privilege access (Q3), financial or regulatory (Q4), decisions about people (Q5).

| Outcome | Rule | Next |
|---|---|---|
| Throwaway | The idea proved non-viable | Close; learning kept at near-zero cost |
| Tier 1 | All "no" | Deploy directly |
| Tier 2 | Q1, Q2 or Q5 "yes" (Q5 adds ethics review) | Security review and red teaming first |
| Tier 3 | Q3 or Q4 "yes", or Q1 and Q2 both "yes" | Formal engineering cycle; a risk summary is written first |

## Re-entry

When engineering finds an unknown unknown, `handing-off-to-engineering` scopes a re-entry: it quotes the ambiguity verbatim and drafts a new session brief, so the gap is resolved cheaply and engineering resumes with corrected context.

## Process diagrams

Mermaid sources live in the owning skill's `references/`:
[end-to-end](skills/running-exploration-cycle/references/process-overview.mmd) •
[one-screen view](skills/running-exploration-cycle/references/high-level-process.mmd) •
[orchestrator loop](skills/running-exploration-cycle/references/orchestrator-loop.mmd) •
[capture loop](skills/capturing-business-requirements/references/capture-loop.mmd) •
[prototyping chain](skills/building-interactive-prototypes/references/prototyping-chain.mmd) •
[handoff junction](skills/handing-off-to-engineering/references/handoff-junction.mmd) •
[rescue path](skills/reengineering-vibe-code/references/vibe-reengineering.mmd).
The process in table form: [process-definition.md](skills/running-exploration-cycle/references/process-definition.md).

## Dispatch and models

Cheap, many-pass work (capture passes, audits, synthesis) can be delegated. Which runtime and model to use, and what it costs, belongs to the `cli-agent` skill in `agent-orchestration`; this plugin never names models. State lives in a SQLite state engine; `exploration/exploration-dashboard.md` is a read-only projection of it.

## Install and use

Installed with APM, like every plugin in this repository: see [INSTALL.md](../../INSTALL.md). There are no external runtime dependencies. For a structured engineering workflow after handoff, this repository's own control plane starts at the `os-control-intake` skill; any other process can consume the framework-neutral handoff package.

**Experts:** see the [BAE Quick Start](BAE-start-guide.md). **Agents:** the entry point is the `running-exploration-cycle` skill; say "let's explore this idea". The concept in depth: [OVERVIEW.md](OVERVIEW.md).

## Layout

```
agent-exploration-cycle/
├── agents/        4 independent audit and certification agents
├── hooks/         SessionStart (injects the bootstrap) and SessionEnd (friction signal)
├── references/    plugin governance: map debt, evolution log, self-evolution profile
└── skills/<skill>/{SKILL.md, references/, assets/, scripts/, evals/}
```

Every skill is self-contained: its scripts, templates and references live inside it, and each retired skill or agent survives as a reference in the skill that absorbed it.

## Acknowledgements

The conversational dashboard pattern, blank-slate sub-agent logistics, the HARD-GATE mechanism, two-stage verification and the plain-language rule were inspired by and adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT licence), translated for non-technical experts. This plugin has no dependency on it and is independently authored.
