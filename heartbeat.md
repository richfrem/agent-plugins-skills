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
