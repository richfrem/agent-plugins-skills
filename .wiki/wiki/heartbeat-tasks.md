---
concept: heartbeat-tasks
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-init/assets/templates/HEARTBEAT_MD.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.176932+00:00
cluster: every
content_hash: 2dbc79a6957e1525
---

# Heartbeat Tasks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Heartbeat Tasks

<!-- Scheduled tasks for /loop. Start with: /loop "Read heartbeat.md and execute the items listed under Every Hour" --interval 1h -->

## Every Hour
- Run the `os-health-check` agent to verify event bus and lock integrity
<!-- e.g. Scan open PRs, check build status, write status.md -->

## Every 24 Hours
<!-- e.g. Promote facts from today's session log to context/memory.md -->
<!-- e.g. Write a day summary to context/memory/YYYY-MM-DD.md -->

## On Session Start
- Load START_HERE.md
- Report open items from context/status.md if it exists


## See Also

- [[loop-scheduler-and-heartbeat-pattern]]
- [[dual-loop-meta-tasks]]
- [[learning-loop-meta-tasks]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[spec-kitty-workflow-meta-tasks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-init/assets/templates/HEARTBEAT_MD.md`
- **Indexed:** 2026-04-17T06:42:10.176932+00:00
