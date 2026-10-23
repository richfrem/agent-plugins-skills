---
trigger: always_on
description: Superseded. No new symlinks; share files between skills through the copy manifest (plugin-architecture-policy Section 5).
globs: ["**/*"]
---

# Rule: No New Symlinks (supersedes the symlink_manager.py workflow)

Plugins no longer use symlinks to share files between skills (APM migration, `docs/plans/apm_migration_plan.md` Section 10.3). Symlinks broke on Windows checkouts, where each one becomes a short text stub that APM installs as the file.

1. **NEVER create symlinks** (`ln -s`, `symlink_manager.py create`, junctions or hardlinks).
2. **Share a file between skills** by keeping one canonical copy at the plugin root and listing each skill path in `symlinks.json` with `strategy: "copy"`.
3. **After cloning or changing a canonical file**, write the copies:
   ```bash
   python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py
   ```
   The copies are listed in the local git exclude file and are never committed.
4. **Before committing**, check for drift and edit the canonical file, never a copy:
   ```bash
   python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py --check
   ```
5. **The one remaining symlink** (`plugins/agent-agentic-os/tests/transition_simulation_cases.py`) is test-only and is not packaged.

Full policy: [plugin-architecture-policy.md](plugin-architecture-policy.md) Section 5.
