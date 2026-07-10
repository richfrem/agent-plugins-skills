<!-- spec-kitty:orientation -->
**Spec Kitty v3.2.2** — project: unknown (healthy)

Two usage patterns:
- **Full mission** (spec → plan → tasks → implement → review → merge):
  trigger: "spec out", "create a mission", "write a spec", "plan this"
  → run `/spec-kitty.specify`
- **Lightweight dispatch** (ad-hoc fix, question, or advice — no mission created):
  trigger: "hey spec kitty", "use spec kitty to", "spec kitty <anything>"
  → **ALWAYS run `spec-kitty dispatch "<request verbatim>"` — do NOT answer directly.**
  If you know the right profile, pass it to skip routing:
  `spec-kitty dispatch "<request verbatim>" --profile <profile-id>`
  Reason: `spec-kitty dispatch` loads governance context, routes the request,
  and opens the Op. Skipping it produces ungoverned, untracked responses.
  After finishing the work, close the Op with the command printed in the capsule
  (`spec-kitty profile-invocation complete --invocation-id <id> --outcome <done|failed|abandoned>`).
<!-- /spec-kitty:orientation -->

---

## Plugin Reinstall Rule (always active)

> **After modifying any skill, script, reference, or plugin source file in `plugins/`**, you MUST reinstall the affected plugin(s) into `.agents/` so the live runtime reflects the changes.
> The skills in `.agents/skills/` are what agents actually run — edits to `plugins/` are inactive until synced.

```bash
# Reinstall all plugins (recommended after multi-plugin edits)
python3 plugins/plugin-manager/scripts/sync_with_inventory.py

# Reinstall a single plugin only
python3 plugins/plugin-manager/scripts/plugin_add.py plugins/<plugin-name> -y
```

Skip reinstall only for: documentation-only edits to `references/`, `ADRs/`, or `docs/` that contain no agent-executable content.

---

## Architecture Reference

See [`architecture.md`](./architecture.md) for the full repo architecture overview — project structure, plugin-by-plugin breakdown, ADR summary, symlink system, and runtime state layout.

`plugins/` is the **source of truth**. `.agents/` contains installed copies only — never derive counts, versions, or skill lists from installed artifacts.

---

## Pre-Push Audit & Verification Rule (always active)

> **Before pushing any changes to GitHub or concluding updates to plugins or skills**, you MUST run standard compliance and structural audits on all affected plugins, and resolve any flagged errors or symlink issues.

```bash
# 1. Run compliance audit on your modified plugin:
python plugins/agent-scaffolders/scripts/audit.py --path plugins/<plugin-name>

# 2. Run structural audit to verify symlink and resource compliance:
python plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>

# 3. Run cross-platform symlink check:
python .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
```

Fix any reported errors, missing references, or duplicate files (moving duplicates to the plugin root `references/` folder and symlinking them via the symlink manager) before proposing or pushing the code.

