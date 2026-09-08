# Evolution Log — Agent Scaffolders

| Date | Tier | Friction / Failure | Patch | Edit Type | Outcome |
|------|------|-------------------|-------|-----------|---------|
| 2026-09-07 | Tier 2 | `references/examples/SKILL.md` was installed as a literal broken symlink target and failed frontmatter loading | Registered the canonical `create-stateful-skill/SKILL.md` source via `symlink_manager.py`, restored links, and reinstalled | Symlink repair | Resolved; source and installed example now carry valid YAML frontmatter |
