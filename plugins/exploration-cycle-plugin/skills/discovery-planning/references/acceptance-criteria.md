# Acceptance Criteria

## Trigger Accuracy
- Skill triggers on relevant requests and does not trigger on unrelated requests.

## Output Quality
- Output is complete, well-structured, and matches the skill's stated purpose.
- No placeholder content is left in outputs.

## Error Handling
- Skill surfaces clear errors when inputs are missing or malformed.
- Skill does not silently fail or produce empty output.

## Standards Compliance
- All scripts are Python (.py) only — no shell scripts.
- No cross-plugin runtime dependencies.
- Symlinks follow the hub-and-spoke pattern via symlinks.json.
