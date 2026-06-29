"""agent-plugins-skills — hermes plugin registration.

Registers all 11 plugin skill directories so they are discoverable
via 'agent-plugins-skills:<skill>' inside hermes sessions.
Hermes auto-prefixes the plugin name as the namespace.
"""

from __future__ import annotations

from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PLUGINS_DIR = _HERE / "plugins"

_SKILL_DIRS = [
    # agent-agentic-os (19 skills)
    ("agent-agentic-os",         "gpt55-critical-auditor"),
    ("agent-agentic-os",         "optimize-agent-instructions"),
    ("agent-agentic-os",         "os-architect"),
    ("agent-agentic-os",         "os-clean-locks"),
    ("agent-agentic-os",         "os-environment-probe"),
    ("agent-agentic-os",         "os-eval-backport"),
    ("agent-agentic-os",         "os-eval-lab-setup"),
    ("agent-agentic-os",         "os-eval-runner"),
    ("agent-agentic-os",         "os-evolution-planner"),
    ("agent-agentic-os",         "os-evolution-verifier"),
    ("agent-agentic-os",         "os-experiment-log"),
    ("agent-agentic-os",         "os-guide"),
    ("agent-agentic-os",         "os-improvement-loop"),
    ("agent-agentic-os",         "os-improvement-report"),
    ("agent-agentic-os",         "os-init"),
    ("agent-agentic-os",         "os-memory-manager"),
    ("agent-agentic-os",         "os-skill-improvement"),
    ("agent-agentic-os",         "self-evolution"),
    ("agent-agentic-os",         "todo-check"),

    # agent-loops (6 skills)
    ("agent-loops",              "agent-swarm"),
    ("agent-loops",              "dual-loop"),
    ("agent-loops",              "learning-loop"),
    ("agent-loops",              "orchestrator"),
    ("agent-loops",              "red-team-review"),
    ("agent-loops",              "triple-loop-learning"),

    # agent-memory (13 skills)
    ("agent-memory",             "memory-management"),
    ("agent-memory",             "rlm-audit"),
    ("agent-memory",             "rlm-cleanup-agent"),
    ("agent-memory",             "rlm-curator"),
    ("agent-memory",             "rlm-distill-agent"),
    ("agent-memory",             "rlm-init"),
    ("agent-memory",             "rlm-search"),
    ("agent-memory",             "vector-db-audit"),
    ("agent-memory",             "vector-db-cleanup"),
    ("agent-memory",             "vector-db-ingest"),
    ("agent-memory",             "vector-db-init"),
    ("agent-memory",             "vector-db-launch"),
    ("agent-memory",             "vector-db-search"),

    # agent-scaffolders (30 skills)
    ("agent-scaffolders",        "analyze-plugin"),
    ("agent-scaffolders",        "audit-plugin"),
    ("agent-scaffolders",        "audit-plugin-l5"),
    ("agent-scaffolders",        "compile-apm-package"),
    ("agent-scaffolders",        "convert-plugin-to-apm"),
    ("agent-scaffolders",        "create-agentic-workflow"),
    ("agent-scaffolders",        "create-apm-package"),
    ("agent-scaffolders",        "create-azure-agent"),
    ("agent-scaffolders",        "create-command"),
    ("agent-scaffolders",        "create-docker-skill"),
    ("agent-scaffolders",        "create-github-action"),
    ("agent-scaffolders",        "create-hook"),
    ("agent-scaffolders",        "create-mcp-integration"),
    ("agent-scaffolders",        "create-plugin"),
    ("agent-scaffolders",        "create-skill"),
    ("agent-scaffolders",        "create-stateful-skill"),
    ("agent-scaffolders",        "create-sub-agent"),
    ("agent-scaffolders",        "ecosystem-authoritative-sources"),
    ("agent-scaffolders",        "ecosystem-standards"),
    ("agent-scaffolders",        "eval-autoresearch-fit"),
    ("agent-scaffolders",        "fix-plugin-paths"),
    ("agent-scaffolders",        "install-apm-package"),
    ("agent-scaffolders",        "l5-red-team-auditor"),
    ("agent-scaffolders",        "manage-marketplace"),
    ("agent-scaffolders",        "mine-plugins"),
    ("agent-scaffolders",        "mine-skill"),
    ("agent-scaffolders",        "path-reference-auditor"),
    ("agent-scaffolders",        "self-audit"),
    ("agent-scaffolders",        "synthesize-learnings"),
    ("agent-scaffolders",        "update-ecosystem-index"),

    # cli-agents (12 skills) — consolidated from deleted claude-cli + copilot-cli + gemini-cli
    ("cli-agents",               "agt-security"),
    ("cli-agents",               "agy-cli-agent"),
    ("cli-agents",               "antigravity-project-setup"),
    ("cli-agents",               "claude-cli-agent"),
    ("cli-agents",               "claude-project-setup"),
    ("cli-agents",               "codex-cli-agent"),
    ("cli-agents",               "copilot-cli-agent"),
    ("cli-agents",               "gemini-cli-agent"),
    ("cli-agents",               "local-llm-bridge"),
    ("cli-agents",               "local-llm-setup"),
    ("cli-agents",               "maf-adapter"),
    ("cli-agents",               "project-setup"),

    # dependency-management (1 skill)
    ("dependency-management",    "dependency-management"),

    # dev-utils (14 skills)
    ("dev-utils",                "adr-management"),
    ("dev-utils",                "bundle-context-full"),
    ("dev-utils",                "coding-conventions-agent"),
    ("dev-utils",                "context-bundler"),
    ("dev-utils",                "convert-mermaid"),
    ("dev-utils",                "hf-download"),
    ("dev-utils",                "hf-init"),
    ("dev-utils",                "hf-upload"),
    ("dev-utils",                "humanize"),
    ("dev-utils",                "link-checker-agent"),
    ("dev-utils",                "optimize-context"),
    ("dev-utils",                "red-team-bundler"),
    ("dev-utils",                "symlink-manager"),
    ("dev-utils",                "task-agent"),

    # exploration-cycle-plugin (20 skills)
    ("exploration-cycle-plugin", "business-requirements-capture"),
    ("exploration-cycle-plugin", "business-workflow-doc"),
    ("exploration-cycle-plugin", "discovery-planning"),
    ("exploration-cycle-plugin", "exploration-handoff"),
    ("exploration-cycle-plugin", "exploration-optimizer"),
    ("exploration-cycle-plugin", "exploration-session-brief"),
    ("exploration-cycle-plugin", "exploration-workflow"),
    ("exploration-cycle-plugin", "prototype-builder"),
    ("exploration-cycle-plugin", "subagent-driven-prototyping"),
    ("exploration-cycle-plugin", "user-story-capture"),
    ("exploration-cycle-plugin", "using-exploration-cycle"),
    ("exploration-cycle-plugin", "vibe-behavioral-test-capture"),
    ("exploration-cycle-plugin", "vibe-browser-audit"),
    ("exploration-cycle-plugin", "vibe-domain-extractor"),
    ("exploration-cycle-plugin", "vibe-reengineer"),
    ("exploration-cycle-plugin", "vibe-slice-migrator"),
    ("exploration-cycle-plugin", "vibe-spec-packager"),
    ("exploration-cycle-plugin", "vibe-to-speckit-superpowers"),
    ("exploration-cycle-plugin", "vibe-togaf-architect"),
    ("exploration-cycle-plugin", "visual-companion"),

    # obsidian-wiki-engine (10 skills)
    ("obsidian-wiki-engine",     "obsidian-bases-manager"),
    ("obsidian-wiki-engine",     "obsidian-canvas-architect"),
    ("obsidian-wiki-engine",     "obsidian-graph-traversal"),
    ("obsidian-wiki-engine",     "obsidian-init"),
    ("obsidian-wiki-engine",     "obsidian-markdown-mastery"),
    ("obsidian-wiki-engine",     "obsidian-query-agent"),
    ("obsidian-wiki-engine",     "obsidian-rlm-distiller"),
    ("obsidian-wiki-engine",     "obsidian-vault-crud"),
    ("obsidian-wiki-engine",     "obsidian-wiki-builder"),
    ("obsidian-wiki-engine",     "obsidian-wiki-linter"),

    # plugin-manager (3 skills)
    ("plugin-manager",           "plugin-installer"),
    ("plugin-manager",           "plugin-remover"),
    ("plugin-manager",           "plugin-syncer"),

    # spec-kitty-plugin (19 skills)
    ("spec-kitty-plugin",        "spec-kitty-accept"),
    ("spec-kitty-plugin",        "spec-kitty-analyze"),
    ("spec-kitty-plugin",        "spec-kitty-checklist"),
    ("spec-kitty-plugin",        "spec-kitty-clarify"),
    ("spec-kitty-plugin",        "spec-kitty-constitution"),
    ("spec-kitty-plugin",        "spec-kitty-dashboard"),
    ("spec-kitty-plugin",        "spec-kitty-implement"),
    ("spec-kitty-plugin",        "spec-kitty-merge"),
    ("spec-kitty-plugin",        "spec-kitty-plan"),
    ("spec-kitty-plugin",        "spec-kitty-research"),
    ("spec-kitty-plugin",        "spec-kitty-review"),
    ("spec-kitty-plugin",        "spec-kitty-specify"),
    ("spec-kitty-plugin",        "spec-kitty-status"),
    ("spec-kitty-plugin",        "spec-kitty-sync-plugin"),
    ("spec-kitty-plugin",        "spec-kitty-tasks"),
    ("spec-kitty-plugin",        "spec-kitty-tasks-finalize"),
    ("spec-kitty-plugin",        "spec-kitty-tasks-outline"),
    ("spec-kitty-plugin",        "spec-kitty-tasks-packages"),
    ("spec-kitty-plugin",        "spec-kitty-workflow"),
]


def register(ctx) -> None:
    """Register all skills. Called once by the hermes plugin loader."""
    for plugin_name, skill_name in _SKILL_DIRS:
        skill_path = _PLUGINS_DIR / plugin_name / "skills" / skill_name
        if skill_path.exists():
            ctx.register_skill(
                name=skill_name,
                path=skill_path,
            )
