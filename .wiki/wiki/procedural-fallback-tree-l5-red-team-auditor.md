---
concept: procedural-fallback-tree-l5-red-team-auditor
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/audit-plugin-l5/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.739586+00:00
cluster: agent
content_hash: 50a8148dcadaca90
---

# Procedural Fallback Tree: L5 Red Team Auditor

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: L5 Red Team Auditor

## 1. Sub-Agent Dispatch Fails (Auth/Permissions)
If the environment (like Claude Code) blocks the execution of `claude -p l5-red-team-auditor` or the subagent errors out on boot:
- **Action**: Do not attempt to simulate the 39-point matrix yourself within the current context. Provide the user with the exact CLI command and instruct them to run it manually in a separate terminal.

## 2. Target Directory Does Not Exist
If the user requests an audit on a plugin name that cannot be found locally:
- **Action**: Terminate the dispatch sequence. Run a local directory search to find similar names. Offer the corrected paths to the user before proceeding.

## 3. Sub-Agent Output is Garbled/Truncated
If the `l5-red-team-auditor` returns a malformed report that misses the required checklists or transparency declarations:
- **Action**: Treat the audit as INCOMPLETE. Warn the user that the sub-agent context likely blew out. Recommend running the analysis on individual sub-components (e.g., just the `scripts/` folder) instead of the whole plugin.

## 4. Red Team Finds Zero Flaws
If the sub-agent returns a perfect L5 score on a complex plugin:
- **Action**: Flag the review as suspiciously shallow. Verify that the sub-agent actually read the `scripts/` directory and didn't just parse the `./SKILL.md` frontmatter. Prompt the user to double-check the `Sources Checked` transparency list.


## See Also

- [[procedural-fallback-tree-red-team-review]]
- [[procedural-fallback-tree-red-team-bundler]]
- [[procedural-fallback-tree-red-team-bundler]]
- [[procedural-fallback-tree-red-team-review]]
- [[procedural-fallback-tree-red-team-review]]
- [[l5-red-team-auditor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/audit-plugin-l5/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:09.739586+00:00
