# The GenAI Double Diamond: Vision-to-Execution Framework

The **GenAI Double Diamond** bridges the maturity gap between a raw idea (the *vibe*) and a hardened engineering contract (the *spec*). This plugin is the first diamond. The one-screen picture is [high-level-process.mmd](skills/running-exploration-cycle/references/high-level-process.mmd); the full process is [process-overview.mmd](skills/running-exploration-cycle/references/process-overview.mmd).

## Three entry points inside Diamond 1

1. **Path 1, pre-build discovery** (no code yet): guides the expert from intent through framing, layout and prototype to a risk-tiered handoff. Skills: `running-exploration-cycle`, `capturing-business-requirements`, `building-interactive-prototypes`.
2. **Path 2, vibe-to-enterprise rescue** (a working prototype exists): `reengineering-vibe-code` audits the running app, salvages the business logic worth keeping ("preservation gems"), quarantines technical debt, and migrates slice by slice behind a characterization-test safety net. Diagram: [vibe-reengineering.mmd](skills/reengineering-vibe-code/references/vibe-reengineering.mmd).
3. **Path 3, technical discovery** (refactor, bug, subsystem): read-only diagnosis in `handing-off-to-engineering` that produces a diagnostic brief.

## Diamond 1: exploration (discovery)

**Goal:** translate vision into validated intent. **Role:** the scouting party.

- **Cheap exploration.** Focused low-cost workers (through the `cli-agent` skill) do framing and story passes; the conductor keeps judgment.
- **Prototype-led discovery.** Working prototypes in minutes surface requirements that meetings take weeks to find.
- **No bottleneck.** The analyst, designer and developer queue is replaced by a guided conversation, with the expert making every decision.
- **Empathetic salvage (rescue).** A vibe-coded prototype proves the concept works. The rescue keeps what is valuable and isolates what is brittle or insecure.

## The transition: handoff and risk analysis

A mandatory filter before any rigorous engineering. Rigor tiers follow five questions (personal data, public exposure, privileged access, financial or regulatory, decisions about people):

- **Tier 1 (low):** internal, no sensitive data. Lightweight deployment.
- **Tier 2 (moderate):** internal data or broader exposure, or decisions about people. Security review and red teaming first.
- **Tier 3 (high):** privileged access or financial/regulatory, or sensitive data together with public exposure. Formal engineering with architectural hardening.

The rescue path ends at the same handoff junction: its output is a framework-neutral specification package plus a certification manifest, not a tool-specific format.

## Diamond 2: the engineering cycle (outside this plugin)

Runs on whatever process the receiving team uses. For this repository's own structured workflow, start at the `os-control-intake` skill. Third-party spec and execution frameworks are surveyed as optional design constraints in [external-spec-frameworks.md](skills/handing-off-to-engineering/references/external-spec-frameworks.md), and what engineering can rely on is in [engineering-cycle-contract.md](skills/handing-off-to-engineering/references/engineering-cycle-contract.md).

## Re-entry

Unknown unknowns found during engineering loop back to a new, focused exploration session. Re-entry is the pipeline working as designed; there is no limit on cycles per engineering run.

## Where to read next

[Design rationale](skills/running-exploration-cycle/references/design-rationale.md) (why the loop halts where it does) • [Process definition](skills/running-exploration-cycle/references/process-definition.md) • [BAE Quick Start](BAE-start-guide.md).
