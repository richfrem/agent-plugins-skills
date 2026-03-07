# Env Helper Plugin (V2)

Minimal environment variable utility for resolving shared ecosystem constants (HuggingFace credentials, dataset repo IDs, project root) without circular dependencies.

## Features
- **Zero Dependency Resolution**: Safely locate and load `.env` files across deep folder hierarchies without relying on heavy internal ecosystem meta-plugins or `python-dotenv`.
- **Token Leakage Constraints (V2)**: Strict L5 verification rules forbidding LLM agents from reading raw API strings out loud into the chat context. 

## Installation

### Local Development
```bash
claude --plugin-dir ./plugins/env-helper
```

## Usage

### CLI
```bash
# Resolve a single key
python3 plugins/env-helper/skills/*/scripts/env_helper.py --key HF_TOKEN

# Dump the HuggingFace dataset configuration block
python3 plugins/env-helper/skills/*/scripts/env_helper.py --hf-config
```

### Agent Integration
Agents should execute the script silently through inline subshells or standard CLI execution to capture the standard out, and NEVER print the results back to the user.

## Directory Structure
```
env-helper/
├── scripts/
│   └── env_helper.py            # The zero-dependency resolver script
├── skills/
│   └── env-helper/
│       └── SKILL.md             # Agent persona and Negative Constraints
└── README.md
```

## License
MIT
