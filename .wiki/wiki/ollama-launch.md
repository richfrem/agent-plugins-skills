---
concept: ollama-launch
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ollama-launch/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.132627+00:00
cluster: distillation
content_hash: fbf12019f78ac924
---

# Ollama Launch

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: ollama-launch
description: Start and verify the local Ollama LLM server. Use when Ollama is needed for RLM distillation, seal snapshots, embeddings, or any local LLM inference — and it's not already running. Checks if Ollama is running, starts it if not, and verifies the health endpoint.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Ollama Launch

Ollama provides local LLM inference for RLM distillation (seal phase summarization) and embeddings.

## When You Need This

- **Seal fails** with `Connection refused` to `127.0.0.1:11434`
- **RLM distillation** shows `[DISTILLATION FAILED]` for new files
- Any tool that calls the Ollama API locally

## Pre-Flight Check

```bash
# Check if Ollama is already running
curl -sf http://127.0.0.1:11434/api/tags > /dev/null && echo "✅ Ollama running" || echo "❌ Ollama not running"
```

If running, you're done. If not, proceed.

## Start Ollama

```bash
# Start Ollama in the background
ollama serve &>/dev/null &

# Wait and verify (2-3 seconds)
sleep 3
curl -sf http://127.0.0.1:11434/api/tags > /dev/null && echo "✅ Ollama ready" || echo "❌ Ollama failed to start"
```

## Verify Model Available

For RLM distillation, the project uses model you define in .env

```bash
# List available models
ollama list

# If the model is missing, pull it
ollama pull qwen2:7b
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Connection refused` after start | Wait longer (`sleep 5`), model may be loading |
| `ollama: command not found` | Ollama not installed — ask user to install from https://ollama.com |
| Port 11434 already in use | Another process on that port — `lsof -i :11434` to identify |

## Integration Points

- **Learning Loop Seal Phase**: RLM synthesis calls Ollama for distillation
- **RLM Factory**: `/rlm-factory:distill` requires Ollama for batch summarization
- **Embeddings**: Any tool that needs local vector embeddings


## See Also

- [[acceptance-criteria-ollama-launch]]
- [[acceptance-criteria-ollama-launch]]
- [[vector-db-launch-python-native-server]]
- [[acceptance-criteria-vector-db-launch]]
- [[vector-db-launch-python-native-server]]
- [[vector-db-launch-python-native-server]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ollama-launch/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.132627+00:00
