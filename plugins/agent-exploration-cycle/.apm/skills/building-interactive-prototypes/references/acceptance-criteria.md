# Acceptance Criteria: building-interactive-prototypes

The original prototype-builder criteria are kept in [prototype-builder-acceptance-criteria.md](prototype-builder-acceptance-criteria.md); the consolidated criteria are below.

## 1. Routing
- [ ] Triggers on "build the prototype", "show me a working version", "what should it look like", "layout options", "walk me through it", once a plan exists.
- [ ] Does not trigger for production code, or for rescuing an existing app (`reengineering-vibe-code`).

## 2. Gate
- [ ] With no approved plan in `exploration/discovery-plans/` the skill stops and sends the expert back to discovery; a file marked DRAFT does not count.
- [ ] Nothing is written under `exploration/prototype/` before the layout direction is confirmed (brownfield sessions with established patterns may skip, marked `[~]`).

## 3. Layout
- [ ] Three distinct plain-language options are presented before any code; the confirmed choice is saved to `exploration/captures/layout-direction.md` (or `document-structure.md` for documents and flows).
- [ ] `python3 ../running-exploration-cycle/scripts/validate_phase_gate.py 2` passes after confirmation.

## 4. Build
- [ ] The build is split into 3 to 6 components; each is reviewed for plan alignment, then quality, and advances only when `COMPLETE` (otherwise `BLOCKED` or `NEEDS_CONTEXT`).
- [ ] Work happens in an isolated workspace via the `os-control-worktree` skill; with no such skill, greenfield warns once and builds in `exploration/prototype/`, and brownfield halts.
- [ ] The prototype is runnable and clickable, not a wireframe: `index.html` and a `README.md` exist for greenfield sessions.

## 5. Walkthrough
- [ ] The expert walks each main flow; the raw record goes to `exploration/captures/walkthrough-notes.md` only. Structured notes come from `capturing-business-requirements`.
- [ ] `python3 ../running-exploration-cycle/scripts/validate_phase_gate.py 3` passes after the notes exist; the skill ends with `PHASE 3 COMPLETE`.

## 6. Language
- [ ] Messages say "isolated workspace" and "validation check", never git, worktree or TDD terms, and no model IDs are named.
