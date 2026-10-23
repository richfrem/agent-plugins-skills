# dev-utils

Developer utilities as 8 self-contained skills. Each skill carries its own scripts, references, assets and tests; there are no plugin-root scripts, no symlinks and no copy-manifest entries.

## Skills

| Skill | Purpose |
|---|---|
| `managing-github-issues` | Log friction and bugs as deduplicated, redacted, taxonomy-validated issues; promote `tasks/*.md` notes; rank P0-P3; draft refactoring proposals; audit closed issues |
| `resolving-github-issues` | Isolated issue worktrees (`.worktrees/issue-NNN`) and the issue to PR to closure flow |
| `bundling-context` | Bundle code and docs (Markdown or ZIP) for review and sub-agent delegation |
| `checking-links` | Audit and repair markdown link integrity |
| `enforcing-coding-conventions` | File headers, type hints, docstrings and naming standards; workspace conventions audit |
| `managing-adrs` | Scaffold, number, list and search Architecture Decision Records |
| `managing-symlinks` | Create, audit and repair cross-platform symlinks |
| `managing-huggingface-assets` | Validate HuggingFace credentials; download and upload datasets, models and snapshots |

## Plugin Structure

```
dev-utils/
├── .claude-plugin/plugin.json    # Claude Code plugin manifest
├── plugin.yaml                   # Plugin manifest (skills list, platforms)
├── README.md                     # This file
├── requirements.in / .txt        # Python dependencies (standard library only)
├── agents/                       # Host sub-agents: coding-conventions-agent, link-checker-agent
├── rules/                        # Installed rules: coding-conventions, dependency-management,
│                                 #   git-operations
├── references/                   # Plugin governance: evolution-log, map-debt, self-evolution-profile
└── skills/<skill>/               # SKILL.md, scripts/, references/, assets/, tests/, evals/
```

## Testing

```bash
python3 -m pytest plugins/dev-utils
```
