# os-environment-probe — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Output Format

Write `context/memory/environment.md`:

```markdown
# AI Environment Profile
_Last updated: YYYY-MM-DD_

## Available Environments

| Environment | Status | Cheapest model | Premium model |
|-------------|--------|----------------|---------------|
| Claude Code | active | claude-haiku-4-5 | claude-sonnet-4-6 |
| Copilot CLI | active | gpt-5-mini | claude-sonnet-4.6 (via --model) |
| Agy CLI     | active | gemini-3.5-flash | — |

> Consult `references/cheapest_models.md` for current model names and costs — do not hardcode here.

## Delegation Strategy

**Cheapest brainstorm model**: <first available in priority order below>
1. Copilot CLI — gpt-5-mini (per-token, low cost)
2. Agy CLI — gemini-3.5-flash (per-token, low cost)
3. Claude Haiku subagent — low cost, in-session

**Primary dispatch model**: claude-sonnet-4-6 (via Copilot CLI if available, else Claude subagent)

## Capability Matrix

| Task | Best tool | Fallback |
|------|-----------|---------|
| Brainstorm options (cheap) | <cheapest model> | claude-haiku-4-5-20251001 |
| Single-file delegation | Copilot CLI | Claude subagent |
| Multi-workstream delegation | Copilot CLI claude-sonnet-4-6 | Claude subagent (sonnet) |
| Overnight unattended loop | os-improvement-loop | — |
```

## Smoke Test

1. After interview + probes, `context/memory/environment.md` exists and contains a
   populated `## Delegation Strategy` section with at least one "Cheapest brainstorm model" line.
2. Running the skill a second time overwrites the file (no duplicate rows).
3. If only Claude Code is confirmed, the file lists only Claude Code as active and sets
   "Cheapest brainstorm model: claude-haiku-4-5 (see references/cheapest_models.md)".

## Gotchas

- **Probe commands must be non-interactive**: use `--version`, `explain "test"`, or
  similar read-only flags — never trigger billing or start sessions.
- **User may not know model names**: ask about products (GitHub Copilot, Gemini), not
  model IDs. Map to model IDs internally.
- **Copilot CLI vs GitHub Copilot in IDE**: these are separate. Copilot CLI requires
  `gh extension install github/gh-copilot`. Confirm CLI specifically, not just Copilot.
- **No free tier**: Copilot and Agy bill per token as of June 2026. Only self-hosted `llama` (Gemma 4) is free. See `references/cheapest_models.md` for current costs.

## Support files

This skill includes two convenience support files to make repro and re-probing easier:

- `scripts/probe_environments.sh` — a small, non-interactive shell probe that runs the same
  read-only commands listed above (`agy --version`, `cursor --version`,
  `gh copilot explain "test"`) and prints a short summary. Safe (non-billing) and tolerant of
  missing commands.
- `references/gemini-detection-example.md` — a short session-specific note showing an observed
  gemini probe result (example output captured during an interactive session). Use as an example
  snippet when building or testing environment.md content.

Write any additional probe outputs to the `references/` directory so downstream skills
(os-architect, os-evolution-planner) can read concrete examples when deciding delegation.
