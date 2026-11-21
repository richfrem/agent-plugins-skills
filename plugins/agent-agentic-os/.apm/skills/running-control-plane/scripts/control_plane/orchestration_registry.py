#!/usr/bin/env python3
"""
control_plane/orchestration_registry.py - execution strategies and sibling skills from the APM dependency.

Purpose:
    `agent-agentic-os` declares `agent-orchestration` as an APM dependency (apm.yml). APM installs every skill
    side by side in one skills folder, so the orchestration skills are always found as siblings of this one:
    `<skills root>/orchestrating-agent-work` and `<skills root>/cli-agent`. That is the only place looked at:
    no repository paths, no home-folder search, no retired skill names (B8, B9). A missing sibling fails
    closed with the `apm install` instruction.

    The execution strategies come from one registry, `orchestrating-agent-work/references/patterns.json`
    (B11, B12). The control plane's own YAML `strategy_artifacts` keeps only strategies the orchestration skill
    does not own (`triple-loop-learning`).

    Tests pass the skills root as a parameter; the source tree is not a runtime location.

Key Functions:
    - skills_root(override)          -- the installed skills folder (this skill's parent), or the override
    - sibling_skill(name, root)      -- a sibling skill folder that has a SKILL.md, or OrchestrationDependencyMissing
    - load_patterns(root)            -- patterns.json from the sibling orchestrating-agent-work
    - strategy_config(pattern, ...)  -- a patterns.json entry, else the YAML strategy_artifacts entry, else None
    - resolve_validator(cfg, root)   -- absolute validator script for a strategy, or None when it has none
    - cli_agent_references(root)     -- the sibling cli-agent skill's references folder (model catalogs)

Key Classes:
    - OrchestrationDependencyMissing
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

ORCHESTRATION_SKILL = "orchestrating-agent-work"
CLI_AGENT_SKILL = "cli-agent"
PATTERNS_RELATIVE_PATH = ("references", "patterns.json")
INSTALL_COMMAND = (
    "apm install richfrem/agent-plugins-skills/plugins/agent-orchestration "
    "--global --target claude,copilot,codex,agy"
)

# control_plane -> scripts -> running-control-plane -> <skills root>
_THIS_SKILLS_ROOT = Path(__file__).resolve().parents[3]


class OrchestrationDependencyMissing(Exception):
    """A sibling skill from the agent-orchestration APM package is not installed beside this skill."""

    def __init__(self, name: str, root: Path):
        self.name = name
        self.root = Path(root)
        super().__init__(
            f"{name} is not installed beside running-control-plane ({self.root}). "
            f"It ships in the agent-orchestration APM package: {INSTALL_COMMAND}"
        )


def _default_skills_root() -> Path:
    """The skills folder this skill is installed in."""
    return _THIS_SKILLS_ROOT


def skills_root(override: Optional[Path] = None) -> Path:
    """The skills folder that holds this skill and its siblings, or `override` when one is given."""
    return Path(override) if override is not None else _default_skills_root()


def sibling_skill(name: str, root: Optional[Path] = None) -> Path:
    """The folder of sibling skill `name`; raises OrchestrationDependencyMissing when it has no SKILL.md."""
    base = skills_root(root)
    folder = base / name
    if not (folder / "SKILL.md").is_file():
        raise OrchestrationDependencyMissing(name, base)
    return folder


def load_patterns(root: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """The strategy registry, read from the sibling orchestrating-agent-work skill's patterns.json."""
    path = sibling_skill(ORCHESTRATION_SKILL, root).joinpath(*PATTERNS_RELATIVE_PATH)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise OrchestrationDependencyMissing(ORCHESTRATION_SKILL, skills_root(root)) from None
    except ValueError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict) or not all(isinstance(v, dict) for v in data.values()):
        raise ValueError(f"{path} must map each pattern name to an object")
    return data


def _yaml_strategy_artifacts(registry: Any = None) -> Dict[str, Dict[str, Any]]:
    """The control plane's own strategy_artifacts (only strategies the orchestration skill does not own)."""
    if registry is None:
        from control_plane.registry import TransitionRegistry

        registry = TransitionRegistry.load_default()
    return registry.strategy_artifacts


def strategy_config(pattern: str, root: Optional[Path] = None, registry: Any = None) -> Optional[Dict[str, Any]]:
    """The configuration of one execution strategy: the patterns.json entry; otherwise the YAML
    `strategy_artifacts` entry (whose `artifact` key is returned as `plan_artifact`, the patterns.json name);
    otherwise None. A missing orchestrating-agent-work sibling raises OrchestrationDependencyMissing."""
    patterns = load_patterns(root)
    if pattern in patterns:
        return dict(patterns[pattern])
    yaml_cfg = _yaml_strategy_artifacts(registry).get(pattern)
    if yaml_cfg is None:
        return None
    cfg = dict(yaml_cfg)
    if "plan_artifact" not in cfg and "artifact" in cfg:
        cfg["plan_artifact"] = cfg.pop("artifact")
    cfg.setdefault("pattern", pattern)
    return cfg


def known_strategies(root: Optional[Path] = None, registry: Any = None) -> list:
    """Every strategy name the control plane accepts (patterns.json plus the YAML-owned ones), sorted."""
    return sorted(set(load_patterns(root)) | set(_yaml_strategy_artifacts(registry)))


def resolve_validator(cfg: Dict[str, Any], root: Optional[Path] = None) -> Optional[Path]:
    """The validator script of a strategy, resolved inside its owning sibling skill; None when the strategy
    has no `validator_script`. A missing skill or script raises OrchestrationDependencyMissing."""
    rel = cfg.get("validator_script")
    if not rel:
        return None
    owner = cfg.get("next_skill") or ORCHESTRATION_SKILL
    folder = sibling_skill(owner, root)
    script = (folder / rel).resolve()
    try:
        script.relative_to(folder.resolve())
    except ValueError:
        raise ValueError(f"validator_script '{rel}' must stay inside the {owner} skill") from None
    if not script.is_file():
        raise OrchestrationDependencyMissing(f"{owner}/{rel}", skills_root(root))
    return script


def cli_agent_references(root: Optional[Path] = None) -> Path:
    """The sibling cli-agent skill's references folder, which holds the model catalogs."""
    return sibling_skill(CLI_AGENT_SKILL, root) / "references"
