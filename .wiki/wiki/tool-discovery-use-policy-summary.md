---
concept: tool-discovery-use-policy-summary
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/tool-inventory/references/tool_discovery_enforcement_policy.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.265020+00:00
cluster: trigger
content_hash: 856d1d37c1244fab
---

# 🛡️ Tool Discovery & Use Policy (Summary)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
trigger: always_on
---

# 🛡️ Tool Discovery & Use Policy (Summary)

**Full workflow → `../SKILL.md`**

### Non-Negotiables
1. **No filesystem search for tools** — `grep`, `find`, `ls -R` are **forbidden** for tool discovery.
2. **Always use mapping tools** — Please trigger the `rlm-query-agent` skill with "KEYWORD".
3. **Fallback prohibited** — if no results, Please trigger the `rlm-cleanup-agent` skill and retry. Do **not** fall back to shell.
4. **Late-bind** — after finding a tool, read its header (`view_file` first 200 lines) before executing.
5. **Register new tools** — `python ./manage_tool_inventory.py add --path "plugins/..."`.
6. **Stop-and-Fix** — if a tool is imperfect, fix it. Do not bypass with raw shell commands.


## See Also

- [[analysis-rlm-tool-discovery-strategy]]
- [[analysis-rlm-tool-discovery-strategy]]
- [[agent-harness-summary]]
- [[research-summary-agent-operating-systems-agent-os]]
- [[research-summary-agent-operating-systems-aos]]
- [[category-semantic-deferred-tool-binding]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/tool-inventory/references/tool_discovery_enforcement_policy.md`
- **Indexed:** 2026-04-17T06:42:10.265020+00:00
