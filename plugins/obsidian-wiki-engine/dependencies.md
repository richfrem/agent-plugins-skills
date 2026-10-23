# Plugin Dependencies: obsidian-wiki-engine

## Companion Package: agent-memory (`rlm-init`)

The `obsidian-wiki-engine` plugin coordinates with distillation capabilities in `agent-memory`.
Install packages via APM in your active project or globally:

```bash
apm install @richfrem/obsidian-wiki-engine @richfrem/agent-memory
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
