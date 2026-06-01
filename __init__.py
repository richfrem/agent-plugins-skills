"""agent-plugins-skills — hermes plugin registration.

Registers all 23 plugin skill directories so they are discoverable
via 'agent-plugins-skills:<skill>' inside hermes sessions.
Hermes auto-prefixes the plugin name as the namespace.
"""

from __future__ import annotations

from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PLUGINS_DIR = _HERE / "plugins"

_SKILL_DIRS = [
    ("agent-agentic-os",         "optimize-agent-instructions"),
    ("agent-agentic-os",         "os-clean-locks"),
    ("agent-agentic-os",         "os-eval-runner"),
    ("agent-agentic-os",         "os-guide"),
    ("agent-agentic-os",         "os-improvement-loop"),
    ("agent-agentic-os",         "os-improvement-report"),
    ("agent-agentic-os",         "os-init"),
    ("agent-agentic-os",         "os-memory-manager"),
    ("agent-agentic-os",         "todo-check"),
    ("agent-loops",              "agent-swarm"),
    ("agent-loops",              "dual-loop"),
    ("agent-loops",              "learning-loop"),
    ("agent-loops",              "orchestrator"),
    ("agent-loops",              "red-team-review"),
    ("agent-loops",              "triple-loop-learning"),
    ("agent-scaffolders",        "create-plugin"),
    ("agent-scaffolders",        "create-skill"),
    ("agent-scaffolders",        "create-sub-agent"),
    ("agent-scaffolders",        "audit-plugin"),
    ("agent-scaffolders",        "create-github-action"),
    ("agent-scaffolders",        "create-mcp-integration"),
    ("claude-cli",               "claude-cli-agent"),
    ("copilot-cli",              "copilot-cli-agent"),
    ("dependency-management",    "dependency-management"),
    ("dev-utils",                "adr-management"),
    ("dev-utils",                "coding-conventions-agent"),
    ("dev-utils",                "context-bundler"),
    ("dev-utils",                "convert-mermaid"),
    ("dev-utils",                "hf-init"),
    ("dev-utils",                "hf-upload"),
    ("dev-utils",                "humanize"),
    ("dev-utils",                "link-checker-agent"),
    ("dev-utils",                "red-team-bundler"),
    ("dev-utils",                "rsvp-comprehension-agent"),
    ("dev-utils",                "rsvp-reading"),
    ("dev-utils",                "symlink-manager"),
    ("dev-utils",                "task-agent"),
    ("exploration-cycle-plugin", "business-requirements-capture"),
    ("exploration-cycle-plugin", "exploration-workflow"),
    ("exploration-cycle-plugin", "prototype-builder"),
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
    ("obsidian-wiki-engine",     "obsidian-wiki-builder"),
    ("obsidian-wiki-engine",     "obsidian-query-agent"),
    ("obsidian-wiki-engine",     "obsidian-init"),
    ("plugin-manager",           "plugin-installer"),
    ("plugin-manager",           "plugin-remover"),
    ("plugin-manager",           "plugin-syncer"),
    ("spec-kitty-plugin",        "spec-kitty-specify"),
    ("spec-kitty-plugin",        "spec-kitty-implement"),
    ("spec-kitty-plugin",        "spec-kitty-plan"),
    ("spec-kitty-plugin",        "spec-kitty-review"),
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
