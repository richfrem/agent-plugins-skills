# Acceptance Criteria: Local LLM Bridge for Antigravity (Agy) (Experimental)

The local LLM bridging skill for Antigravity is considered functional and validated when:
- [ ] The local `llama-server` is verified running on port `8089` using the optimized Metal profile.
- [ ] The global routing proxy on port `4000` is active and routes `/v1/chat/completions` requests to the local server.
- [ ] Patching of `config.toml` in `run_agy.py` is fully idempotent (no duplicates or false-positives for existing `gemma-4-12b` models with different endpoints).
- [ ] The `LOCAL_PASSTHROUGH` environment variable is successfully set/propagated when executing `agy`.
- [ ] Agy execution exits gracefully with status code `1` and prints a clear error if the `agy` binary is missing from PATH.
