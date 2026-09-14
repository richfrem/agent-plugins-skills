# Evolution Log — Agent Scaffolders

| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |
|------|------|-------------------|-------|-----------|---------|
| 2026-09-07 | Tier 2 | `references/examples/SKILL.md` was installed as a literal broken symlink target and failed frontmatter loading | Registered the canonical `create-stateful-skill/SKILL.md` source via `symlink_manager.py`, restored links, and reinstalled | Symlink repair | Resolved; source and installed example now carry valid YAML frontmatter |
| 2026-09-08 | Tier 2 | A nested `SKILL.md` symlink under `create-command/references/examples/` remained discoverable as an extra skill after the frontmatter repair | Removed both misplaced manifest links and added a structure-audit regression test rejecting nested `SKILL.md` files under skill resources | Structural guard | Resolved; skill definitions remain only at `<skill-name>/SKILL.md` |
| 2026-09-11 | Tier 1 | Progressive disclosure standard refactoring for create-skill and audit-skill | Refactored create-skill (39 lines) and audit-skill (33 lines) to lean routers, added 4-tier review rubric, discovery interview & platform references, and updated audit_skill.py with <=80 lines progressive disclosure budget check | Evolution | SUCCESS |
