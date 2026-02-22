---
trigger: always_on
---

# 🛡️ Tool Discovery & Use Policy (Summary)

**Full workflow → `plugins/tool-inventory/skills/tool_discovery/SKILL.md`**

### Non-Negotiables
1. **No filesystem search for tools** — `grep`, `find`, `ls -R` are **forbidden** for tool discovery.
2. **Always use `query_cache.py`** — `python plugins/rlm-factory/scripts/query_cache.py --type tool "KEYWORD"`.
3. **Fallback prohibited** — if no results, run `python plugins/codify/rlm/refresh_cache.py` and retry. Do **not** fall back to shell.
4. **Late-bind** — after finding a tool, read its header (`view_file` first 200 lines) before executing.
5. **Register new tools** — `python plugins/tool-inventory/scripts/manage_tool_inventory.py add --path "plugins/..."`.
6. **Stop-and-Fix** — if a tool is imperfect, fix it. Do not bypass with raw shell commands.