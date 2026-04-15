# Plugin Dependencies: obsidian-wiki-engine

## Required: rlm-factory

The `obsidian-wiki-engine` plugin delegates all distillation tasks to scripts
in `rlm-factory`. Both plugins must be installed in the same `.agents/` folder.

### Install both plugins at once

```bash
# Recommended — uvx (cross-platform, zero-setup):
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y

# Or install individually:
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
# Then select: obsidian-wiki-engine, rlm-factory
```

### Zero-dep fallback (macOS/Linux)

```bash
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python3 -
```

### Local clone (interactive TUI)

```bash
python plugins/plugin-manager/scripts/plugin_add.py
```

---

## Required: Obsidian Desktop App

The Obsidian desktop application must be installed to browse and visualize
the generated wiki nodes and canvas files.

- **macOS:** `brew install --cask obsidian`
- **Manual download:** https://obsidian.md/download

---

## Required: Python 3.8+

All scripts in this plugin use Python 3.8+ standard library plus `pyyaml`.

```bash
pip install pyyaml
# Or via the locked requirements:
pip install -r requirements.txt
```

---

## Optional: Cheap LLM CLIs (for distillation)

The `obsidian-rlm-distiller` skill uses the cheapest available CLI automatically:

| Priority | CLI | Model Used |
|:---------|:----|:-----------|
| 1st | `copilot` (GitHub Copilot Pro) | `gpt-5-mini` |
| 2nd | `claude` (Claude Code) | `claude-haiku-4-5` |
| 3rd | `gemini` (Gemini CLI) | `gemini-3-flash-preview` |

> **Note:** `rlm-distill-ollama` is deprecated. Only `rlm-distill-agent` with
> cheap cloud models is used. No local GPU required.
