> Retired skill `install-apm-package`, kept as the **install-apm-package** mode of `packaging-with-apm`. Body unchanged apart from link targets, moved script/test paths and the compile verification command (`apm compile --validate`). Frontmatter removed.
>
> Original description: Activate when the user wants to install, deploy, update, roll back, test, or materialize an APM package into runtime directories (.agents/, .claude/, .github/, .codex/ and others), globally or into one project, or do a dry run of an APM install. Use after creating or converting an APM package.

# Install APM Package (`install-apm-package`)

Installs APM packages, including this repository's plugins, globally or into a project, pinned to a ref, with backup and rollback of the global state. Behaviour below was verified with APM `0.33.0`.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Where Files Land](#where-files-land)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Pin every install** to `#<tag>` or `#<commit-sha>`. `scripts/apm_consumer.py` refuses unpinned installs.
2. **Never edit deployed files** in harness folders; change the source package and reinstall.
3. **Commit `apm.yml` and `apm.lock.yaml` together** for project installs; use `apm install --frozen` in CI.
4. **One installer per plugin**: do not install the same plugin with APM and the legacy `plugin-add` installer (duplicate skill names).

## Quick start

```bash
python3 scripts/apm_consumer.py install --plugins dev-utils --ref <tag-or-sha> --global
```

Default targets are `claude,copilot,agy,codex`. Add `--skill <name>` (repeatable, one plugin) to install only some skills.

## Workflow

1. **Preview**: `apm install <package>#<ref> --target claude --dry-run`.
2. **Install**: `scripts/apm_consumer.py install ...` (global installs back up `~/.apm/apm.yml` and `apm.lock.yaml` first), or `apm install <package>#<ref> --target <targets>` in a project.
3. **Move to a new release**: `scripts/apm_consumer.py set-ref --ref <new-ref>` rewrites every global install from this repository and reinstalls (after a backup).
4. **Roll back**: `scripts/apm_consumer.py rollback [--backup <id>]` uninstalls packages added since the backup, restores both files, and reinstalls. Restoring the files alone would leave orphaned skills.
5. **Remove**: `apm uninstall <package> [--global]`. It keeps untracked files and stops (keeping its records) if a user file sits inside a package's skill folder.

## Where Files Land

| | Project install | Global install |
|---|---|---|
| Skills | `.claude/skills/`; `.agents/skills/` (copilot, codex, agy) | `~/.claude/skills/`; `~/.agents/skills/`; `~/.gemini/antigravity-cli/skills/` |
| Agents | `.claude/agents/`, `.github/agents/`, `.codex/agents/` | `~/.claude/agents/`, `~/.copilot/agents/`, `~/.codex/agents/` |
| Manifest, lockfile, cache | `apm.yml`, `apm.lock.yaml`, `apm_modules/` | `~/.apm/` (Windows: `%USERPROFILE%\.apm\`) |

A global install writes nothing into any repository; every repository uses the same user-level copies. Global installs give agy no hooks or agents. Plugins whose shared files come from a copy manifest are installed from their packed bundle (`apm install <bundle>.zip`), not the raw git path.

## Verification

```bash
apm install --frozen          # project: reproduce exactly from the lockfile
python3 scripts/apm_consumer.py list-backups
```

In Claude Code the installed skills appear in the skills list; in Copilot CLI use `/skills list`. Tests: `tests/test_apm_consumer.py` in this skill.

## References

- [acceptance-criteria.md](../acceptance-criteria.md) — Acceptance gates and target verification criteria.
- [fallback-tree.md](../fallback-tree.md) — Fallback resolution for installation failures and target collisions.
