---
concept: plugin-manager
source: plugin-code
source_file: plugin-manager/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.659317+00:00
cluster: plugins
content_hash: 11d23ac72c4443b1
---

# Plugin Manager

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Plugin Manager

**Universal Cross-Platform Plugin Installer — Works where other managers cannot**

The **Plugin Manager** is the cross-agent, cross-platform orchestration hub for your plugin ecosystem. Where other managers install individual skills only and the Claude `/plugin` marketplace is Claude-specific, `plugin_add.py` installs **full plugins** (skills + agents + commands + hooks) directly from GitHub — on any OS, for any agent.

---

## Why This Exists: The Three-Tool Landscape

| Tool | Platform | Installs | GitHub source |
|---|---|---|---|
| Legacy skills managers | Mac/Linux only (symlink issues) | Skills only | ✓ `owner/repo` |
| `/plugin marketplace add` | Claude Code only | Full plugins | ✓ `owner/repo` |
| **`plugin_add.py`** ★ | **All platforms** (Windows, Mac, Linux) | **Full plugins** (skills + agents + commands + hooks) | ✓ `owner/repo` |

> `plugin_add.py` is the cross-platform, cross-agent equivalent of other skills managers — but for full plugins, not just individual skills.

---

## Initial Installation (Bootstrapping)

These commands are for consumers who want to add plugins seamlessly *without* cloning the repo.

### Option 1: `uvx` — Modern Python Standard (Recommended)

If you have [uv](https://docs.astral.sh/uv/) installed (the modern Python package manager), you get instantaneous, isolated installations exactly like `npx`, but natively cross-platform without Node.js.

```bash
# Interactive picker
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Install everything non-interactively
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y

# Preview without writing any files
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --dry-run
```

### Option 2: Fallback Bootstrap (Zero Tooling Assumptions)

If you don't use `uv`, you can install purely using standard Python tooling without cloning the repo.

**Mac / Linux:**
```bash
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python -
```
**Windows (PowerShell):**
```powershell
Invoke-RestMethod https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python -
```

### Option 3: Claude Code Marketplace (Claude Code only)

```bash
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install plugin-manager
```

## Subsequent Installations

Because `uvx` and `bootstrap.py` execute ephemerally, you simply repeat the same command to add new plugins later. There is no local state to manage outside of your `.agents/` folder.

If you chose to **clone the repo locally** instead of using the remote bootstrappers, run:
```bash
python ./scripts/plugin_add.py
```

---

## Why `plugin_add.py` Works on Windows

Legacy installers often fail on Windows because Git checks out symlinks as plain text files (e.g. `scripts/install_all_plugins.py`). Node.js `cp({ dereference: true })` detects real symlinks and copies the target on Mac/Linux — but on Windows it sees a text file and copies the literal path string, leaving broken installs.

`plugin_add.py` solves this by reading those pointer files at install time, following the relative path back to the real Python source, and writing a proper hard copy into `.agents/`. **No symlinks. No npm. No Node.js dependency.** Works identically on all platforms.

---

## 🌐 Supported Targets

The Plugin Manager deploys to `.agents/` as the universal canonical store, then symlinks to:

| Agent Environment | Directory |
|---|---|
| **Universal / All agents** | `.agents/` |
| **Claude Code** | `.claude/` |
| **Azure AI** | `.azure/` |

> Antigravity, GitHub Copilot, and Gemini CLI all read directly from `.agents/` — no per-agent symlinks needed.

---

## Skills

| Skill | Purpose | Key Scripts |
| :--- | :--- | :--- |
| **[plugin-installer](skills/plugin-installer/SKILL.md)** | Default: `plugi

*(content truncated)*

## See Also

- [[adr-manager-plugin]]
- [[task-manager-plugin]]
- [[acceptance-criteria-adr-manager]]
- [[identity-the-adr-manager]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[session-memory-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `plugin-manager/README.md`
- **Indexed:** 2026-04-17T06:42:09.659317+00:00
