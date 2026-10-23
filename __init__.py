"""
Purpose:
    Hermes plugin registration for agent-plugins-skills ecosystem.
    Registers all plugin skill directories so they are discoverable
    via 'agent-plugins-skills:<skill>' inside hermes sessions.
    Hermes auto-prefixes the plugin name as the namespace.

Key Input Dependencies:
    - plugins/ directory with all 10 plugin subdirectories
    - Each plugin with skills/ subdirectory structure
    - Hermes plugin loader context (ctx) at registration time

Key Functions:
    - register(): Register all skills with hermes plugin loader
"""

from __future__ import annotations

from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PLUGINS_DIR = _HERE / "plugins"

_SKILL_DIRS = [
    # agent-agentic-os (15 skills on disk; the subset registered here)
    ("agent-agentic-os",         "os-control-intake"),
    ("agent-agentic-os",         "os-lab-planner"),
    ("agent-agentic-os",         "os-lab-backport"),
    ("agent-agentic-os",         "os-lab-setup"),
    ("agent-agentic-os",         "os-lab-scorer"),
    ("agent-agentic-os",         "os-lab-log"),
    ("agent-agentic-os",         "os-lab-loop"),
    ("agent-agentic-os",         "os-control-init"),
    ("agent-agentic-os",         "os-lab-memory"),

    # agent-orchestration/ (6 skills)
    ("agent-orchestration/",              "agent-swarm"),
    ("agent-orchestration/",              "dual-loop"),
    ("agent-orchestration/",              "learning-loop"),
    ("agent-orchestration/",              "orchestrator"),
    ("agent-orchestration/",              "red-team-review"),
    ("agent-orchestration/",              "triple-loop-learning"),

    # agent-memory (4 skills)
    ("agent-memory",             "managing-rlm-cache"),
    ("agent-memory",             "managing-vector-db"),
    ("agent-memory",             "managing-obsidian-vaults"),
    ("agent-memory",             "memory-management"),

    # agent-scaffolders (30 skills)
    ("agent-scaffolders",        "audit-plugin"),
    ("agent-scaffolders",        "compile-apm-package"),
    ("agent-scaffolders",        "convert-plugin-to-apm"),
    ("agent-scaffolders",        "create-agentic-workflow"),
    ("agent-scaffolders",        "create-apm-package"),
    ("agent-scaffolders",        "create-azure-agent"),
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
    ("agent-scaffolders",        "install-apm-package"),
    ("agent-scaffolders",        "manage-marketplace"),

    # cli-agents — backend dispatch, local LLM, model catalogs and project setup live in cli-agent
    ("cli-agents",               "agt-security"),
    ("cli-agents",               "cli-agent"),
    ("cli-agents",               "maf-adapter"),

    # dev-utils (8 skills)
    ("dev-utils",                "bundling-context"),
    ("dev-utils",                "checking-links"),
    ("dev-utils",                "enforcing-coding-conventions"),
    ("dev-utils",                "managing-adrs"),
    ("dev-utils",                "managing-github-issues"),
    ("dev-utils",                "managing-huggingface-assets"),
    ("dev-utils",                "managing-symlinks"),
    ("dev-utils",                "resolving-github-issues"),

    # agent-exploration-cycle (5 skills)
    ("agent-exploration-cycle", "running-exploration-cycle"),
    ("agent-exploration-cycle", "capturing-business-requirements"),
    ("agent-exploration-cycle", "building-interactive-prototypes"),
    ("agent-exploration-cycle", "handing-off-to-engineering"),
    ("agent-exploration-cycle", "reengineering-vibe-code"),

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
