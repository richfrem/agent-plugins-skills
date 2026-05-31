# cli-agents

Unified CLI Conductor Suite. Orchestrates task delegation to Claude, Copilot, and Gemini CLI engines with integrated AGF/AGT security controls, path boundary assertions, and default-isolated execution modes.

## Plugin Structure

```
cli-agents/
├── .claude-plugin/
│   └── plugin.json           # Unified manifest
├── README.md                 # This file
├── agents/                   # Consolidated agent personas
│   ├── refactor-expert.md
│   ├── security-auditor.md
│   └── architect-review.md
├── scripts/
│   ├── conductor.py          # Unified execution conductor
│   ├── path_security.py      # Assertions for allowed path boundaries
│   ├── test_harness.py       # Local MAF adapter test simulator
│   ├── agt_ops.py            # Local AGT sandbox & key validator
│   └── adapters/             # Lightweight provider CLI adapters
│       ├── claude_adapter.py
│       ├── copilot_adapter.py
│       └── gemini_adapter.py
└── skills/
    ├── claude-cli-agent/     # Claude CLI execution wrapper
    ├── copilot-cli-agent/    # Copilot CLI execution wrapper
    ├── gemini-cli-agent/     # Gemini CLI execution wrapper
    ├── project-setup/        # Unifies project setups
    ├── maf-adapter/          # MAF adapter specifications & simulation
    └── agt-security/         # AGT sandboxing, HMAC controls
```

## Features

1. **Secure by Default**: Sub-agents default to `isolated=True` (no tool access). Tool execution requires explicit `--allow-tools` parameter validation.
2. **Path Traversal Protection**: Unified `path_security.py` checks target paths before passing to CLIs.
3. **Pre-flight Heartbeats**: Adapters perform model and authentication status health checks.
