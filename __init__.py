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
    ("adr-manager",              "adr-management"),
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
    ("coding-conventions",       "coding-conventions-agent"),
    ("context-bundler",          "context-bundler"),
    ("context-bundler",          "red-team-bundler"),
    ("copilot-cli",              "copilot-cli-agent"),
    ("dependency-management",    "dependency-management"),
    ("exploration-cycle-plugin", "business-requirements-capture"),
    ("exploration-cycle-plugin", "exploration-workflow"),
    ("exploration-cycle-plugin", "prototype-builder"),
    ("gemini-cli",               "gemini-cli-agent"),
    ("huggingface-utils",        "hf-init"),
    ("huggingface-utils",        "hf-upload"),
    ("link-checker",             "link-checker-agent"),
    ("memory-management",        "memory-management"),
    ("mermaid-to-png",           "convert-mermaid"),
    ("obsidian-wiki-engine",     "obsidian-wiki-builder"),
    ("obsidian-wiki-engine",     "obsidian-query-agent"),
    ("obsidian-wiki-engine",     "obsidian-init"),
    ("plugin-manager",           "plugin-installer"),
    ("plugin-manager",           "plugin-remover"),
    ("plugin-manager",           "plugin-syncer"),
    ("rlm-factory",              "rlm-distill-agent"),
    ("rlm-factory",              "rlm-search"),
    ("rlm-factory",              "rlm-init"),
    ("rsvp-speed-reader",        "rsvp-reading"),
    ("spec-kitty-plugin",        "spec-kitty-specify"),
    ("spec-kitty-plugin",        "spec-kitty-implement"),
    ("spec-kitty-plugin",        "spec-kitty-plan"),
    ("spec-kitty-plugin",        "spec-kitty-review"),
    ("task-manager",             "task-agent"),
    ("vector-db",                "vector-db-ingest"),
    ("vector-db",                "vector-db-search"),
    ("vector-db",                "vector-db-init"),
    ("voice-writer",             "humanize"),
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
