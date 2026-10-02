# Acceptance Criteria: prototype-builder

## Correct Behaviors

- **Correct:** When a Discovery Plan exists at `exploration/discovery-plans/` and a layout direction file exists at `exploration/captures/layout-direction.md`, prototype-builder begins component decomposition immediately without re-presenting either artifact for re-approval or re-confirmation.

- **Correct:** When no Discovery Plan exists in `exploration/discovery-plans/`, prototype-builder uses the canonical HARD-GATE redirect text from `references/hard-gate-enforcement.md` and stops — it does not attempt to infer a plan from conversation or proceed without one.

- **Correct:** When invoked from within an active Exploration Session (dashboard exists and Status is not Complete), prototype-builder checks the `## Session Context` block for session type and dispatch strategy before building anything.

- **Correct:** For brownfield sessions, prototype-builder builds into the existing codebase directory rather than creating a standalone prototype directory.

## Incorrect Behaviors

- **Incorrect:** Prototype-builder re-asks the SME to confirm the Discovery Plan or layout direction that was already approved — this is redundant and breaks the HARD-GATE approval that already happened.

- **Incorrect:** Prototype-builder proceeds without a Discovery Plan by inferring requirements from the conversation — all build work must be grounded in an approved written plan.

- **Incorrect:** Prototype-builder builds all components in one pass without the two-stage review (plan alignment check + quality check) per component.
