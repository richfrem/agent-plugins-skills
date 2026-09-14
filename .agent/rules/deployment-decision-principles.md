---
description: >
  Three decision principles for choosing whether a migration stage needs
  full automation, a generated wave script, or manual/simpler handling --
  found during the Phase 9 exhaustive source audit as already-generic
  guidance with no project-specific content.
globs:
  - "plugins/sharepoint-migration-planning/**/*"
---

# Rule: Deployment Decision Principles

Apply these three principles when deciding whether a dependency-graph
finding warrants a generated wave script, or a simpler/manual response.

## "Like for like" is a principle, not a hard rule

The goal is to preserve *what the source object does*, not *how it was
originally built*. Before generating a wave script to recreate a legacy
construct exactly, ask: does a modern SharePoint Online capability already
make the original construct unnecessary? Migrate the data; don't rebuild
the mechanism if the platform already covers the outcome natively.

## "Quantity ≠ effort"

A dependency graph with many nodes of the same object type does not
automatically mean many nodes of work. Several similarly-shaped objects can
often collapse into one generated wave script with a parameter, or one
platform capability with a filtered view, rather than one script per
object. Assess the actual distinct implementation work, not the object
count.

## "Manual recreation beats complex automation" for one-off, low-complexity cases

If an object's entire migration logic is simple and low-volume, a person
configuring it directly in SharePoint Online may take less time and carry
less risk than a developer building and testing a generated script for it.
`generate-sharepoint-wave-scripts` should recommend manual handling for
these cases rather than generating a script anyway "for completeness."

## Applying these principles to stage sequencing

- If a completeness check (`completeness_checks.py`) reports a source
  object as `NEEDS_ONBOARDING`-equivalent (present at the source, no
  generic capability covers it, and it is low-complexity), recommend
  manual handling and say so explicitly — never generate an in-flight
  script for a capability that has not actually been designed or tested.
- If a source object maps 1:1 to an existing `sharepoint-provisioning`
  capability (a list, a field, a content type, a calendar), the generated
  wave script should call that capability directly — never reimplement
  provisioning logic that already exists.
- If a source object has no 1:1 equivalent (arbitrary custom code, complex
  branching logic), the generated wave guide must say so and describe the
  requirement, not attempt a mechanical translation of the original
  artifact's implementation.
