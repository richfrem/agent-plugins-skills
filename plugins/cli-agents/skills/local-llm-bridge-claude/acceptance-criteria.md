# Acceptance Criteria: Local LLM Bridge

The local Gemma 4 bridging skill is considered fully functional when all the following criteria are met:

## 1. Memory and Swap Constraints
* [ ] The total memory consumption of the `llama-server` process does not exceed 10.5 GB.
* [ ] The system does not enter memory compression or SSD swap thrashing during prompt evaluations.
* [ ] The server starts up and warms up the model within 15 seconds.

## 2. Proxy Routing Accuracy
* [ ] Requests targeting `claude-*` are forwarded natively to Anthropic's Cloud API.
* [ ] Requests targeting `gemma-*` are forwarded natively to `localhost:8089/v1/messages`.
* [ ] SSE connection streaming works properly, sending chunks token-by-token.

## 3. Caching and Performance
* [ ] Second-turn queries in the same Claude Code session achieve LCP similarity score `1.000` in server logs.
* [ ] Subsequent prompts respond in under 3 seconds.
* [ ] No infinite reasoning loops occur; the model returns control to Claude Code immediately when generation completes.
