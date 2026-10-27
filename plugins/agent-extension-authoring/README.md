# Agent Extension Authoring (`agent-extension-authoring`)

The interactive creation, auditing, and packaging suite for the agent ecosystem.
Consolidates 24 legacy scaffolding skills into 6 cohesive authoring assets.

Every skill in this plugin is completely self-contained inside `.apm/skills/` with its own scripts, references, assets, tests, and evals.

---

## What's in the Box

| Skill | Purpose | Key capabilities |
|---|---|---|
| `authoring-skills` | Scaffolds, evaluates, and audits agent skills | Instructional & executable skills, stateful skills, benchmark loop, 64-pattern catalog |
| `authoring-plugins` | Scaffolds and audits whole plugins | Plugin skeleton, manifest compliance, structure verification, ecosystem indexing |
| `authoring-subagents` | Scaffolds and audits sub-agents | Sub-agent markdown specs, sandboxing, permission gates, adversarial personas |
| `authoring-instructions` | Scaffolds and audits governance instructions | AGENTS.md, CLAUDE.md, rules, lifecycle hooks (PreToolUse, PostToolUse) |
| `authoring-github-workflows` | Scaffolds GitHub workflows and Copilot agents | GitHub Agentic Workflows (gh-aw), CI/CD actions, Copilot custom agents |
| `packaging-with-apm` | Packages, builds, and distributes via APM | APM manifest compilation, package distribution, migration, rollback |

---

## Directory Structure

```
agent-extension-authoring/
├── .apm/
│   └── skills/
│       ├── authoring-github-workflows/
│       ├── authoring-instructions/
│       ├── authoring-plugins/
│       ├── authoring-skills/
│       ├── authoring-subagents/
│       └── packaging-with-apm/
├── .claude-plugin/
│   └── plugin.json
├── apm.yml
├── README.md
└── rules/
    └── plugin-architecture-policy.md
```

---

## Architecture & Constraints

- **Self-Contained Skills**: Each skill owns its dependencies, tests, references, and scripts directly inside `.apm/skills/<skill>/`. No shared plugin-root scripts or symlinks.
- **Portability**: No machine-specific paths; scripts run in source and installed APM layouts.
- **Verification**: Run deterministic audits (`audit_skill.py`, `audit_plugin_structure.py`, `audit.py`) before pushing changes.
