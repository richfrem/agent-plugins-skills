# Repository Installation & Lifecycle — Central Authority

This document defines how to install, update, select and remove the plugins and skills in the Universal Agent Plugins & Skills repository.

Plugins are installed with [APM](https://github.com/microsoft/apm) (Agent Package Manager). APM copies each plugin's skills and agents into the agent harness folders, keeps a manifest and lockfile, and handles updates and uninstall. Background and status: [APM migration plan](docs/plans/apm_migration_plan.md).

Skills share files without symlinks: each shared file has one canonical copy, and `symlinks.json` lists the skill folders that need a copy. Those copies are not in git; a short step after cloning (`materialize_copies.py`) writes them. That is why plugins are installed **from a local clone**, not from the bare git path: the git path alone would give skills without their shared scripts. This works the same on Windows, macOS and Linux.

---

## Option 1: APM Package (Recommended)

### 1. Install APM

The repository pins the APM version it is tested with (`apm-cli==0.33.0` in `plugins/agent-scaffolders/requirements-dev.in`).

On Windows:

```powershell
irm https://aka.ms/apm-windows | iex
```

On macOS / Linux:

```bash
curl -sSL https://aka.ms/apm-unix | sh -s -- @v0.33.0
```

Verify:

```bash
apm --version
```

### 2. Get a pinned clone and materialize the shared files

Clone the repository and check out the release tag or commit you want; that commit is the pinned version of everything you install from this clone.

```bash
git clone https://github.com/richfrem/agent-plugins-skills.git
cd agent-plugins-skills
git checkout <tag-or-commit>
python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py
```

`materialize_copies.py` writes every shared copy into the skill folders and keeps them out of git (local exclude file). Run it again after every `git checkout` or `git pull`; `--check` reports missing or out-of-date copies.

### 3. Install globally (available in every project)

The consumer script checks the clone is materialized, backs up your global APM state, and installs:

```bash
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py install --plugins <plugin-name> --checkout . --global
```

For example, two plugins at once: `--plugins dev-utils,agent-memory`. Default targets are `claude,copilot,agy,codex` (`--targets` to change). The direct APM equivalent is:

```bash
apm install ./plugins/<plugin-name> --global --target claude,copilot,agy,codex
```

The global installation keeps the package cache separate from the agent folders and writes nothing into your other repositories; every repository uses the same user-level copies:

```text
APM state and cache          ~/.apm/                              (Windows: %USERPROFILE%\.apm\)
Claude Code skills           ~/.claude/skills/
Copilot and Codex skills     ~/.agents/skills/                    (shared)
Antigravity (agy) skills     ~/.gemini/antigravity-cli/skills/
```

Global (user-scope) support differs by harness (APM 0.33.0): `claude` supports every primitive; `copilot`, `codex` and `agy` support skills but only some other primitives (for `agy`, hooks and agents are not installed globally). Plugins that depend on hooks need a project install for those harnesses. Executables in a plugin's `bin/` are skipped unless you pass `--trust-bin` (or approve the package with `apm approve`).

### 4. Install only the skills you need

Keep context small by installing named skills from one plugin. `--skill` is repeatable, and the selection is saved in the manifest:

```bash
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py install --plugins dev-utils --checkout . --global --skill managing-adrs --skill bundling-context
```

A later `--skill` adds to the selection. To drop a skill, remove it from the `skills:` list in `~/.apm/apm.yml` and run `apm install --global`. To go back to all skills, use `--skill '*'`. [COMPONENT_RETENTION_GUIDE.md](COMPONENT_RETENTION_GUIDE.md) lists the recommended selection per plugin.

### 5. Install into one project instead

From the project root, point at the materialized clone:

```bash
apm install <path-to-clone>/plugins/<plugin-name> --target claude,copilot,agy,codex
```

APM records the dependency in the project's `apm.yml`, writes `apm.lock.yaml`, deploys skills into `.claude/skills/` (Claude) and the shared `.agents/skills/` (Copilot, Codex and Antigravity), and adds `apm_modules/` to `.gitignore`. Commit `apm.yml` and `apm.lock.yaml` together. In CI, reproduce the exact install with `apm install --frozen`.

### Verify

```bash
apm install ./plugins/<plugin-name> --target claude --dry-run      # preview without writing files
python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py --check
```

In Claude Code, installed skills appear in the skills list. In Copilot CLI, check with `/skills list`, or restart VS Code.

### Update

Move the clone to the new release, re-materialize, and reinstall:

```bash
git fetch --tags && git checkout <new-tag-or-commit>
python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py
apm install --global
```

`apm install --global` re-reads every installed plugin from the clone. For a project install, run `apm install` in the project and commit the updated lockfile.

### Roll back

Every `apm_consumer.py install` backs up `~/.apm/apm.yml` and `apm.lock.yaml` first. To return to the previous state (uninstalls packages added since the backup, then restores and reinstalls):

```bash
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py list-backups
python3 plugins/agent-scaffolders/skills/install-apm-package/scripts/apm_consumer.py rollback [--backup <id>]
```

### Uninstall

```bash
apm uninstall <path-to-clone>/plugins/<plugin-name> --global     # global install
apm uninstall <path-to-clone>/plugins/<plugin-name>              # project install
```

Uninstall removes only the files APM deployed; it keeps your own files, and stops (keeping its records) if you added a file inside one of the package's skill folders.

### Switching Between Local and Global Installs

To switch a project from a local install (`.agents/`, `.claude/`) to a user-level global install (`~/.agents/`, `~/.claude/`):

1. **Remove the project-level install**:
   ```bash
   apm uninstall ./plugins/<plugin-name>       # or: rm -rf .agents .claude .codex apm_modules apm.yml apm.lock.yaml
   ```
2. **Install globally from your materialized clone**:
   ```bash
   apm install ./plugins/<plugin-name> --global --target claude,copilot,agy,codex
   ```

> [!IMPORTANT]
> **Antigravity (`agy`) Hook Scope**:
> In APM 0.33.0, global installs deploy skills into `~/.gemini/antigravity-cli/skills/`, but lifecycle hooks (`SessionStart`, `PostToolUse`, `Stop`) are **only supported in project installs** (`.agents/hooks.json`). If your workflow depends on Antigravity runtime hooks, keep the project-local install (`apm install ... --target agy`).

### Where Does `materialize_copies.py` Run?

* **In Consuming Repositories (e.g., SharePoint Workbench)**:
  Consuming projects **never** need to run `materialize_copies.py`! Consuming repositories do not contain `plugins/` or `symlinks.json`. When APM installs a package (from a materialized local clone, a packed `.zip` bundle, or a GitHub release tag), APM deploys **already fully self-contained physical copies**.
* **In This Authoring Monorepo**:
  `materialize_copies.py` is an upstream monorepo maintenance tool. It ensures canonical files at `plugins/<plugin>/scripts/` are copied into local `skills/<skill>/scripts/` for tests and local execution without committing duplicates.

#### How to Invoke `materialize_copies.py` Across Different Harnesses:
If invoking the script from an installed skill (`convert-plugin-to-apm`) or across different harness environments:

| Context | Command |
| :--- | :--- |
| **Monorepo Source (Default)** | `python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py` |
| **Local Project `.agents` Harness** | `python3 .agents/skills/convert-plugin-to-apm/scripts/materialize_copies.py --path <repo-root>` |
| **Local Project `.claude` Harness** | `python3 .claude/skills/convert-plugin-to-apm/scripts/materialize_copies.py --path <repo-root>` |
| **Global Claude Harness** | `python3 ~/.claude/skills/convert-plugin-to-apm/scripts/materialize_copies.py --path <repo-root>` |
| **Global Copilot / Codex / Agy** | `python3 ~/.agents/skills/convert-plugin-to-apm/scripts/materialize_copies.py --path <repo-root>` |

### Packed bundles

`apm_build_pipeline.py --pack` (see [Local Development](#local-development-contributors--testing)) produces `build/dist/<plugin>-<version>.zip`, which installs with `apm install <bundle>.zip --global --target ...` without a clone. A bundle installs the whole plugin: `--skill` is not supported for bundles.

### Do not use multiple installations of the same plugin

APM and the older `plugin-add` installer both put skills into agent folders. Installing the same plugin both ways creates duplicate skill names, and which copy wins depends on the client.

If a project was set up with `plugin-add`, it has a `.agents/ownership/` folder and a `plugin-sources.json` file. Remove the old installation of a plugin before installing it with APM:

```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove --plugins <plugin-name>/ --yes
```

---

## Option 2: Native Marketplace (Claude Code / Copilot CLI)

If using **Claude Code** or **Copilot CLI**, you can add this repository as a native marketplace:

### Claude Code Syntax
```text
/plugin marketplace add richfrem/agent-plugins-skills
/plugin
/plugin install <plugin-name>
```

### Copilot CLI Syntax
```bash
copilot plugin marketplace add richfrem/agent-plugins-skills
copilot plugin
copilot plugin install <plugin-name>@richfrem-agent-plugins-skills
```

---

## Local Development (Contributors & Testing)

After cloning, and after editing any canonical shared file, write the copies into the skill folders:

```bash
python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/materialize_copies.py
```

Edit the canonical file (at the plugin root), never a copy; `materialize_copies.py --check` reports copies that drifted. To share a new file with a skill, add a `symlinks.json` entry with `strategy: "copy"` and re-run the script. Never create symlinks.

Install a plugin straight from the working tree to test changes before they are pushed:

```bash
apm install ./plugins/<plugin-name> --target claude,copilot,agy,codex
```

To check that a plugin packages cleanly for APM (copies created, links valid, test install and uninstall in a throwaway fixture), run the build pipeline; add `--pack` to build the bundle. It writes only to `build/` and never changes the source tree:

```bash
python3 plugins/agent-scaffolders/skills/convert-plugin-to-apm/scripts/apm_build_pipeline.py --plugin plugins/<plugin-name>
```

Each finding names its standard fix; see [APM alignment standard fixes](plugins/agent-scaffolders/skills/convert-plugin-to-apm/references/apm-alignment-fixes.md).
