---
description: Run compliance and structural audits on all modified plugins and skills, and resolve errors before pushing to GitHub.
globs:
  - "plugins/**/*"
---

# Pre-Push Audit & Verification Rule

Before pushing any changes to GitHub or concluding updates to plugins or skills, you MUST run standard compliance and structural audits on all affected plugins, and resolve any flagged errors or symlink issues.

## Verification Commands

Run the following checks from the repository root:

1. **Compliance Audit**:
   ```bash
   python plugins/agent-scaffolders/scripts/audit.py --path plugins/<plugin-name>
   ```

2. **Structural Audit**:
   Verify symlink and resource compliance:
   ```bash
   python plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>
   ```

3. **Cross-Platform Symlink Check**:
   ```bash
   python .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
   ```

## Resolution Action

If any errors, missing references, or duplicate files are reported:
- Resolve them immediately before proposing a commit or push.
- Move duplicates to the plugin root `references/` folder and symlink them back to the individual skills using `symlink_manager.py`.
