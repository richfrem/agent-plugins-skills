# Agentic OS - Global Connectors
**Mapping Plugin Dependencies to LLM Tools**

| Dependency | Standard LLM Tool | Purpose Context |
| :--- | :--- | :--- |
| `~~filesystem` | `Read`, `Write`, `List` | Reading and scaffolding `CLAUDE.md`, `context/status.md`, `context/memory/`, and `skills/`. |
| `~~scheduler` | `Bash` | Creating cron jobs, background processes, or platform-specific scheduling loops (e.g. Claude Code `/loop`). |
| `~~python` | `Bash` | Native hook script execution (`hooks/update_memory.py` and `init_agentic_os.py`). |
