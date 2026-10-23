# Audit lenses

Read the source files in `plugins/`, not the installed client copies, which can be stale.

## Prior art
- the plugin map-debt file: entries marked `Repeat: YES` for the target. If one matches, stop
  and escalate to `os-lab-agent`; do not plan over a hypothesis that already failed.
- `wiki/decisions/` and `wiki/playbook-*.md` for rejected approaches.

## Gap lenses
- Description: says what AND when; trigger phrases; DO NOT USE lines for siblings.
- Length: SKILL.md concise; detail moved to `references/`.
- Paths: relative to the skill root; no repo-root `plugins/...` paths.
- Evals: at least 10 real cases in `should_trigger` form, including sibling negatives.
- Gotchas section, handoff block, smoke test present.
- Hard-coded model IDs that should come from the `update-cli-models` skill in `cli-agents`.
- Overlap with another skill that could be extended instead.

## Match quality
Full: exists, current, no gaps. Partial: exists with gaps. None: nothing close.
