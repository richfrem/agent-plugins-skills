# Session Memory Manager - Connectors
**Mapping Skill Dependencies to LLM Tools**

| Dependency | Standard LLM Tool | Purpose Context |
| :--- | :--- | :--- |
| `~~filesystem` | `Read` | Parsing the dated `context/memory/YYYY-MM-DD.md` logs, and scanning `context/memory.md` for conflict detection (Dementia Defense). |
| `~~filesystem` | `Write` | Appending curated facts to `context/memory.md` and modifying timestamp headers in `context/status.md`. |
| `~~filesystem` | `Bash` | Using `rm` or `mv` to archive daily logs to `context/memory/archive/` post-promotion. |