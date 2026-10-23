# Plugin Acceptance Criteria — Agent Orchestration

## 1. Trigger Accuracy
- Master orchestrator (`orchestrating-agent-work`) triggers on tasks requiring structural multi-agent coordination (DAGs, supervisor/worker loops, parallel swarms).
- Multi-LLM router (`cli-agent`) triggers on bounded task delegation to CLI backends (Claude, Copilot, Gemini, Agy, Codex, local llama-server).
- Security and governance skills (`agt-security`, `maf-adapter`) trigger exclusively on their respective governance domains.

## 2. Output Quality & Verifier Sovereignty
- Output is complete, well-structured, and adheres to verifiable schemas (`graph-manifest.json`, strategy packets, job files).
- Verifier contracts cannot be bypassed or self-certified by implementation agents.
- No placeholder content or truncated payloads are returned.

## 3. Error Handling & Fallbacks
- Backend or tool failures fail closed, surface explicit error messages to callers, and record friction in `references/map-debt.md`.
- Zero silent fallback to alternative backends without explicit caller instruction.

## 4. Standards Compliance
- All execution engines and hooks are written in pure Python (.py).
- Zero external runtime package dependencies (Python standard library only).
- Installed skills must be self-contained; no symlinks.
