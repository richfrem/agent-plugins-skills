# Procedural Fallback Tree: RLM Factory

If the primary curation or distillation scripts fail, execute the following triage steps exactly in order:

## 1. Connection Refused (Ollama Down)
If `distiller.py` exits with an HTTP `Connection refused` referencing port `11434`:
- **Action**: Do not attempt to debug the python script. It means the background AI server is not running on the operating system. You must either start the server manually (`ollama serve &`) or instruct the user they must boot it up. 

## 2. JSON Cache Corruption
If `inventory.py`, `query_cache.py`, or `distiller.py` crashes with a `json.decoder.JSONDecodeError` while trying to read the cache files inside `.agent/learning/`:
- **Action**: This means a rogue agent bypassed the concurrency constraints and corrupted the file. You must cleanly delete the corrupted `rlm_summary_cache.json` or `rlm_tool_cache.json` files and re-run distillation completely. Do not try to manually repair millions of lines of malformed JSON strings.

## 3. Sub-Agent Write Failures
If you are running `inject_summary.py` manually and the terminal throws an error about `lock acquisition failed` or times out:
- **Action**: This means another active swarm process is currently writing to the exact same file. Pause operations for 10 seconds, then retry using the python tool. Do NOT attempt to fallback to writing the file natively.
