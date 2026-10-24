> Retired skill `audit-plugin`, kept as the **audit-plugin** mode of `authoring-plugins`. Body unchanged apart from link targets and the parts rewritten for the self-contained end state (no copy manifest, optional `apm.yml`, delegation to sibling skills by name). Frontmatter removed.
>
> Original description: Use when the user asks to audit or validate a plugin, check its structure or .claude-plugin/plugin.json, review components, or confirm compliance. Also trigger after plugin components change. Audit the whole plugin here; use authoring-skills for one skill.

# Audit Plugin (`audit-plugin`)

Performs comprehensive validation of a plugin against structure standards, naming conventions, and component requirements.

## Contents

- [Dependencies](#dependencies)
- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Dependencies

Requires Python 3.8+ and standard library modules.

## Constraints

- **APM Native & Unified Structure**: In APM-native packages, primitives live exclusively in `.apm/`. `audit_plugin_structure.py` flags duplicate primitive directories outside `.apm/` as errors.
- **No raw filesystem symlinks**: Under APM, skills must be self-contained packages. Raw symlinks are prohibited.
- **Self-contained skills**: shared files are not kept at the plugin root; a plugin that still has a `symlinks.json` copy manifest is mid-migration and its drift is checked with the `packaging-with-apm` skill.
- **Portability**: No hardcoded paths (`/Users/`, `/home/`); use relative paths or `${CLAUDE_PLUGIN_ROOT}`.
- **Manifest schemas**: `apm.yml` defines APM package metadata; `.claude-plugin/plugin.json` author field must be an object `{"name": "...", "email": "..."}`.

## Quick start

Run structural and component audits for target plugin:

```bash
# 1. Structure and manifest audit
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
# 2. Plugin compliance gate (also runs every skill audit when authoring-skills is installed)
python3 scripts/audit.py --path plugins/<plugin-name>
```

Then delegate by skill name: `authoring-skills` (audit all skills), `authoring-subagents` (audit the agents), `authoring-instructions` (audit rules and hooks) and, while a copy manifest exists, `packaging-with-apm` (`materialize_copies.py --check`).

## Workflow

1. **Structure & Manifest**: Run `audit_plugin_structure.py` for `.claude-plugin/plugin.json` conformance (author object, no auto-discovered arrays) and the absence of raw symlinks.
2. **Compliance gate**: Run `audit.py --path` for the plugin-level checks and the per-skill audits.
3. **Components**: Delegate skills, sub-agents, rules and hooks to the skills named above.
4. **Portability**: Verify zero hardcoded tokens or machine-specific paths.

## Verification

```bash
# Full verification pipeline for a plugin
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>
python3 scripts/audit.py --path plugins/<plugin-name>
```

## References

- [audit-plugin-guide.md](../audit-plugin-guide.md) — Comprehensive audit rules and error codes.
- [acceptance-criteria.md](../acceptance-criteria.md) — Plugin validation acceptance criteria.
- [fallback-tree.md](../fallback-tree.md) — Escalation protocol for structural audit failures.
