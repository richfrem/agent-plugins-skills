# Repository Installation & Lifecycle — Central Authority

This document defines how to install, update, select and remove the plugins and skills in the Universal Agent Plugins & Skills repository.

Plugins are installed with [APM](https://github.com/microsoft/apm) (Agent Package Manager). APM copies each plugin's skills and agents into the agent harness folders, keeps a manifest and lockfile, and handles updates and uninstall. Background and status: [APM migration plan](docs/plans/apm_migration_plan.md).

Each plugin keeps its skills and agents in `plugins/<plugin>/.apm/`, with a `plugins/<plugin>/apm.yml`. Everything APM installs is committed to git, so there is no build or copy step: clone the repository and run `apm install`. This works the same on Windows, macOS and Linux.

---

## Option 1: APM Package (Recommended)

### 1. Install APM

Use APM 0.35.0 or newer; the `agy` (Antigravity) target needs it.

On Windows:

```powershell
irm https://aka.ms/apm-windows | iex
```

On macOS / Linux:

```bash
curl -sSL https://aka.ms/apm-unix | sh -s -- @v0.35.0
```

Verify:

```bash
apm --version
```

### 2. Get a pinned clone

Clone the repository and check out the release tag or commit you want; that commit is the pinned version of everything you install from this clone.

```bash
git clone https://github.com/richfrem/agent-plugins-skills.git
cd agent-plugins-skills
git checkout <tag-or-commit>
```

### 3. Install globally (available in every project)

Global installs need the **absolute path** to each plugin folder; a relative path such as `./plugins/<plugin-name>` is rejected. Plugins are the folders under `plugins/` (for example `agent-agentic-os`, `agent-memory`, `dev-utils`).

Windows (PowerShell), one plugin:

```powershell
apm install "$PWD\plugins\<plugin-name>" --global --target claude,copilot,agy,codex --parallel-downloads 0
```

macOS / Linux:

```bash
apm install "$PWD/plugins/<plugin-name>" --global --target claude,copilot,agy,codex
```

Pass several absolute paths in one command to install several plugins at once. `--parallel-downloads 0` avoids an "Access denied" error on Windows when APM renames its staging folder.

The global installation keeps the package cache separate from the agent folders and writes nothing into your other repositories; every repository uses the same user-level copies:

```text
APM state and cache          ~/.apm/                              (Windows: %USERPROFILE%\.apm\)
Claude Code skills           ~/.claude/skills/
Copilot and Codex skills     ~/.agents/skills/                    (shared)
Antigravity (agy) skills     ~/.gemini/antigravity-cli/skills/
```

Global (user-scope) support differs by harness (APM 0.35.0): `claude` supports every primitive; `copilot`, `codex` and `agy` support skills but only some other primitives (for `agy`, hooks and agents are not installed globally). Plugins that depend on hooks need a project install for those harnesses. Executables in a plugin's `bin/` are skipped unless you pass `--trust-bin` (or approve the package with `apm approve`). If a skill folder already exists that APM did not create, APM skips it; add `--force` to overwrite.

#### Windows and macOS / Linux

| | Windows | macOS / Linux |
| :--- | :--- | :--- |
| Install APM | `irm https://aka.ms/apm-windows \| iex` | `curl -sSL https://aka.ms/apm-unix \| sh -s -- @v0.35.0` |
| Plugin path | Absolute, `"$PWD\plugins\<plugin-name>"` | Absolute, `"$PWD/plugins/<plugin-name>"` |
| Extra flag | `--parallel-downloads 0` (avoids "Access denied" on the staging rename) | not needed |
| State folder | `%USERPROFILE%\.apm\` | `~/.apm/` |
| Python in examples | `python` | `python3` |

### 4. Install only the skills you need

Keep context small by installing named skills from one plugin. `--skill` is repeatable, and the selection is saved in the manifest. This uses the consumer script, which also backs up your global APM state first:

```bash
python3 plugins/agent-extension-authoring/.apm/skills/packaging-with-apm/scripts/apm_consumer.py install --plugins dev-utils --checkout . --global --skill managing-adrs --skill bundling-context
```

A later `--skill` adds to the selection. To drop a skill, remove it from the `skills:` list in `~/.apm/apm.yml` and run `apm install --global`. To go back to all skills, use `--skill '*'`. [COMPONENT_RETENTION_GUIDE.md](COMPONENT_RETENTION_GUIDE.md) lists the recommended selection per plugin.

### 5. Install into one project instead

From the project root, point at the clone:

```bash
apm install <path-to-clone>/plugins/<plugin-name> --target claude,copilot,agy,codex
```

APM records the dependency in the project's `apm.yml`, writes `apm.lock.yaml`, deploys skills into `.claude/skills/` (Claude) and the shared `.agents/skills/` (Copilot, Codex and Antigravity), and adds `apm_modules/` to `.gitignore`. Commit `apm.yml` and `apm.lock.yaml` together. In CI, reproduce the exact install with `apm install --frozen`.

### Verify

```bash
apm install <path-to-clone>/plugins/<plugin-name> --target claude --dry-run      # preview without writing files
```

In Claude Code, installed skills appear in the skills list. In Copilot CLI, check with `/skills list`, or restart VS Code.

### Update

Move the clone to the new release and reinstall:

```bash
git fetch --tags && git checkout <new-tag-or-commit>
apm install --global
```

`apm install --global` re-reads every installed plugin from the clone. For a project install, run `apm install` in the project and commit the updated lockfile.

### Roll back

Every `apm_consumer.py install` backs up `~/.apm/apm.yml` and `apm.lock.yaml` first. To return to the previous state (uninstalls packages added since the backup, then restores and reinstalls):

```bash
python3 plugins/agent-extension-authoring/.apm/skills/packaging-with-apm/scripts/apm_consumer.py list-backups
python3 plugins/agent-extension-authoring/.apm/skills/packaging-with-apm/scripts/apm_consumer.py rollback [--backup <id>]
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
   apm uninstall <path-to-clone>/plugins/<plugin-name>       # or: rm -rf .agents .claude .codex apm_modules apm.yml apm.lock.yaml
   ```
2. **Install globally from your clone** (absolute path, see section 3):
   ```bash
   apm install <path-to-clone>/plugins/<plugin-name> --global --target claude,copilot,agy,codex
   ```

> [!IMPORTANT]
> **Antigravity (`agy`) Hook Scope**:
> Global installs deploy skills into `~/.gemini/antigravity-cli/skills/`, but lifecycle hooks (`SessionStart`, `PostToolUse`, `Stop`) are **only supported in project installs** (`.agents/hooks.json`). If your workflow depends on Antigravity runtime hooks, keep the project-local install (`apm install ... --target agy`).

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

Install a plugin straight from the working tree to test changes before they are pushed:

```bash
apm install <path-to-clone>/plugins/<plugin-name> --target claude,copilot,agy,codex
```

To check that a plugin packages cleanly for APM (links valid, test install and uninstall in a throwaway fixture), run the build pipeline; add `--pack` to build the bundle. It writes only to `build/` and never changes the source tree:

```bash
python3 plugins/agent-extension-authoring/.apm/skills/packaging-with-apm/scripts/apm_build_pipeline.py --plugin plugins/<plugin-name>
```

Each finding names its standard fix; see [APM alignment standard fixes](plugins/agent-extension-authoring/.apm/skills/packaging-with-apm/references/apm-alignment-fixes.md).
