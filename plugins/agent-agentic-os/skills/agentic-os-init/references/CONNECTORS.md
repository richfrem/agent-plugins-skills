# Agentic OS Init - Connectors
**Mapping Skill Dependencies to LLM Tools**

| Dependency | Standard LLM Tool | Purpose Context |
| :--- | :--- | :--- |
| `~~python` | `Bash` | Executing `./init_agentic_os.py` wrapper to scaffold the environment. |
| `~~filesystem` | `Read`, `Write` | Overriding manual scaffolding fallbacks if Python isn't available, wiring `hooks.json`. |
| `~~scheduler` | `Bash` | (Optional Phase) Wiring the heartbeat / loop commands to the host environment. |