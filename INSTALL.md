# Repository Installation — Central Authority

This document defines the single, authoritative suite of installation methods for all **120 skills** and **29 plugins** in the Universal Agent Plugins & Skills repository.

---

## Consumer Installation (Bootstrapping)

These commands are for consumers who want to add plugins seamlessly *without* cloning the repo. The single `.agents/` environment directory is **not committed** to your repo. It will be empty by default. Run one of the installers below to deploy plugins.

### Option 1: `uvx` — Modern Python Standard (Recommended)

If you have [uv](https://docs.astral.sh/uv/) installed, you get instantaneous, isolated installations natively cross-platform without Node.js.

```bash
# Interactive picker
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Install everything non-interactively (no prompts)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y

# Preview what will be installed without writing any files
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --dry-run
```

### Option 2: Fallback Bootstrap (Zero Tooling Assumptions)

If you don't use `uv`, you can install purely using standard Python tooling without cloning the repo.

**Mac / Linux:**
```bash
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python3 -
```
**Windows (PowerShell):**
```powershell
Invoke-RestMethod https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python -
```

### Subsequent Installations

Because `uvx` and `bootstrap.py` execute ephemerally, you simply repeat the same command to add new plugins later. There is no local state to manage outside of your `.agents/` folder.

---

## Alternative: Claude Code Native Marketplace

If you are using Claude Code (2.1.81+), you can add this repository as a native marketplace and install plugins without leaving the terminal:

```text
# Add this repository to your known marketplaces
/plugin marketplace add richfrem/agent-plugins-skills

# Open the interactive TUI to browse, discover, and install plugins
/plugin

# Or install a specific plugin directly
/plugin install <plugin-name>
```

---

## Alternative: npx skills CLI (Mac / Linux only)

> [!NOTE]
> **`npx skills add` installs skills only** — no commands, agents, or hooks. It also only works correctly on Mac/Linux (Git symlinks check out as plain-text files on Windows). For full plugin deployment on any platform, use `uvx` or `bootstrap.py`.

### Standard Commands
```bash
# Install a specific skill collection
npx skills add richfrem/agent-plugins-skills

# Install a specific plugin from a repository
npx skills add <user>/<repo>/plugins/<plugin-name>

# Update all installed skills across all agents
npx skills update
```

### Local Development & Reinstallation
For contributors and skill developers who need to test local sources:
```bash
# Force local reinstallation
npx skills add richfrem/agent-plugins-skills/plugins/my-plugin --force

# Reset .agents folder for clean local sync
rm -rf .agents/ && npx skills add richfrem/agent-plugins-skills/plugins/my-plugin --force
```
> [!CAUTION] 
> **Broken Symlinks on Windows:** `npx skills add` fails on Windows because it fails to dereference Git symlinks correctly. Use `uvx` or `bootstrap.py` for full platform-agnostic deployment.

---

## Installer Comparison

| Method | Platform | Full Plugin | GitHub source | Notes |
|---|---|---|---|---|
| `uvx` ★ | **All** (Win/Mac/Linux) | ✅ skills + agents + commands + hooks | ✅ `owner/repo` | Recommended default |
| `bootstrap.py` | **All** (Win/Mac/Linux) | ✅ full | ✅ `owner/repo` | Zero-dependency fallback |
| `/plugin` marketplace | Claude Code only | ✅ full | ✅ | Native Claude TUI |
| `npx skills add` | Mac/Linux only | ❌ skills only | ✅ | No Python required |

---

## Local Development (For Developers)

If you want to maintain a Git repo for debugging instead of using the remote bootstrappers:

```bash
git clone https://github.com/richfrem/agent-plugins-skills.git
cd agent-plugins-skills

# Install a specific plugin from local source
python plugins/plugin-manager/scripts/plugin_add.py --plugin <plugin-name>

# Install all plugins from local source
python plugins/plugin-manager/scripts/plugin_add.py --all
```
