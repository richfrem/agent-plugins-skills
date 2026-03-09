---
trigger: always_on
---

# 🛡️ Tool Discovery & Use Policy (Summary)

**Full workflow → `../../SKILL.md`**

### Non-Negotiables
1. **No filesystem search for tools** — `grep`, `find`, `ls -R` are **forbidden** for tool discovery.
2. **Always use mapping tools** — Please trigger the `rlm-query-agent` skill with "KEYWORD".
3. **Fallback prohibited** — if no results, Please trigger the `rlm-cleanup-agent` skill and retry. Do **not** fall back to shell.
4. **Late-bind** — after finding a tool, read its header (`view_file` first 200 lines) before executing.
5. **Register new tools** — `python ../../scripts/manage_tool_inventory.py add --path "plugins/..."`.
6. **Stop-and-Fix** — if a tool is imperfect, fix it. Do not bypass with raw shell commands.