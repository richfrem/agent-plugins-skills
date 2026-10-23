# Delegation

Hand the prompt file to the backend the brief confirmed, by invoking the matching `cli-agents`
dispatcher skill by name: `cli-agent`, selecting `--cli copilot`, `agy`, `claude` or
`codex`. Do not call its scripts directly.

1. Check the skill is installed (`apm list` or checking the active client harness or global profile). If not, stop and ask.
2. Run the dispatcher's own heartbeat check first, on its cheapest tier.
3. Dispatch once with the full prompt. Pick the cheapest suitable tier from `cli-agents`
   the current models from the `cli-agent` skill's model catalogs in `cli-agents`. Batch all work in one
   request; do not iterate on premium tiers.
4. Verify the output is non-empty and every workstream's files exist before reporting done.
5. If no backend is available, return the prompt as a manual delegation prompt.

Never dispatch without user confirmation relayed by `os-lab-agent`.
