# Acceptance Criteria: Local LLM Bridge for Codex Clients

The local LLM bridging skill for general OpenAI/Codex compatible CLI clients is considered functional and validated when:
- [ ] The local `llama-server` is verified running on port `8089` using the optimized Metal profile.
- [ ] The global routing proxy on port `4000` is active and routes `/v1/chat/completions` requests to the local server.
- [ ] Running the launcher `python3 run_codex.py <target_command>` successfully runs the command with `OPENAI_API_BASE` and `OPENAI_BASE_URL` env overrides injected.
- [ ] If the target command is missing from PATH, the launcher exits gracefully with status code `1` and outputs a descriptive error.
