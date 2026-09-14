---
description: >
  Schema/dependency definitions for a SharePoint migration must live in JSON,
  never hardcoded inside generated or hand-written deployment scripts.
globs:
  - "plugins/sharepoint-migration-planning/**/*.py"
  - "plugins/sharepoint-migration-planning/assets/*.json"
---

## Core principle

Every schema/deployment-object definition (site columns, content types,
lists, or any other deployable object type) lives in a caller-supplied JSON
structure -- never hardcoded inline in a deployment script or an
orchestrator. Deploy logic and validation logic both read the SAME
structure, so they cannot drift from each other: if a field, content type,
or list is renamed, added, or removed in the schema, both the code that
deploys it and the code that verifies it see the change on the very next
run, not on a separately-maintained copy someone forgot to update.

## The dependency-annotation standard

Any object that needs ordered deployment relative to other objects
declares its dependencies **by name**, in the same shared schema structure
used for planning and validation (this plugin's generalized
`DeploymentObject.depends_on`, see `scripts/wave_planning.py`) -- never by
having its position hand-encoded into a separate, fixed-order orchestrator
step list. A dependency is "this object depends on that named object," not
"this object belongs in stage N" -- the latter requires a human to keep the
stage number in sync with reality every time the object set changes, which
is exactly the kind of coupling this rule exists to eliminate.

## Why this rule exists

A hand-maintained deployment step list is a duplicate source of truth: it
encodes, by hand, an ordering that a dependency graph could instead compute.
The moment the underlying set of deployable objects changes -- one is
renamed, several are consolidated into a single script, or a new one is
introduced -- the hand-maintained list can silently fall out of sync with
that reality. Nothing catches the drift until the orchestrator is actually
run: it may reference an object or script that no longer exists, or it may
run everything in an order that no longer reflects real dependencies. A
schema-driven, dependency-annotated approach -- where deployment order is
computed via topological sort over declared dependencies, not typed out by
a human -- turns that class of bug into a planning-time failure (an
unresolved dependency or a cycle, reported honestly) rather than a
run-time surprise against a live tenant.

## Deliberately out of scope for this rule

1. **No hardcoded object definitions inside a generated wave script.** Every list/field/
   content-type name a generated script touches must come from `dependency-matrix.json`, never be
   typed into the script by the generation step as a literal.
2. **The deploy script and its validation/test companion must read the same JSON.** If a script
   and its test derive their expectations from different sources, they can drift from each other
   silently — this was the specific failure mode `dependency-matrix.json`'s design is meant to
   prevent.
3. **Wave order is computed, never hand-assigned.** `analyze-sharepoint-dependency-graph` derives
   order via topological sort (`sharepoint-migration-planning`'s own `wave_planning.py`) from
   declared dependencies — it is never a human-maintained sequence of stage numbers.
4. **A dependency is declared by name, not by wave number.** Referring to "whatever ran in an
   earlier stage" instead of a specific named object is exactly the kind of coupling that goes
   stale when stages are renumbered, split, or reordered.
