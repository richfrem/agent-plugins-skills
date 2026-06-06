# Acceptance Criteria: Local LLM Bridge for GitHub Copilot (Experimental)

The local LLM bridging skill for GitHub Copilot is considered functional and validated when:
- [ ] The local `llama-server` is verified running on port `8089` using the optimized Metal profile.
- [ ] The global routing proxy on port `4000` is active and routes `/v1/chat/completions` requests to the local server.
- [ ] Running the launcher in diagnostic mode `python3 run_copilot.py --diagnose` executes successfully, outputting version, help, and environment variables without errors.
- [ ] If `copilot` binary is missing from system `PATH`, the launcher cleanly exits with status code `1` and outputs a descriptive error.
- [ ] Outbox requests failover cleanly to flat plain-text 503 error payloads if the local server is offline, preventing JSON formatting parser crashes.
