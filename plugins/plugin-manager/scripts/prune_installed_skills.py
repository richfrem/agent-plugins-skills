#!/usr/bin/env python3
"""
prune_installed_skills.py
=========================

Purpose:
    Deterministic pruning engine and dependency scanner for .agents/ components
    based on the retention manifest (plugin-retention.json). Safely identifies,
    advises on cross-component dependencies, and removes unselected skills,
    rules, and agents from the active environment.

Layer: Plugin Manager / Pruning

Interfaces:
    - scan_dependencies(skills_dir: Path, retained_skills: set[str]) -> dict[str, set[str]]
    - plan_pruning(root: Path, manifest: dict) -> dict[str, list[Path]]
    - execute_pruning(removals: dict[str, list[Path]], root: Optional[Path], dry_run: bool) -> int
    - toggle_component_state(manifest: dict, plugin_name: str, component_type: str, component_name: str) -> dict
    - CLI: python3 prune_installed_skills.py [--manifest PATH] [--execute] [--confirm-token TOKEN] [--dry-run]
"""

import os
import sys
import json
import shutil
import argparse
import re
import types
from pathlib import Path
from typing import Optional, Dict, List, Set, Any

# ---------------------------------------------------------------------------
# UTF-8 safety on Windows
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------
_ANSI = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else True

def _col(code: str, text: str) -> str:
    """Wrap text in an ANSI escape sequence if stdout is a TTY."""
    return f"\033[{code}m{text}\033[0m" if _ANSI else text

def cyan(t: str) -> str:
    return _col("96", t)

def green(t: str) -> str:
    return _col("92", t)

def yellow(t: str) -> str:
    return _col("93", t)

def dim(t: str) -> str:
    return _col("2", t)

def bold(t: str) -> str:
    return _col("1", t)

def red(t: str) -> str:
    return _col("91", t)

# ---------------------------------------------------------------------------
# Terminal raw-mode helpers
# ---------------------------------------------------------------------------
def _read_key() -> str:
    """Read one raw keypress from stdin and return a string token.

    Returns 'UP', 'DOWN', 'LEFT', 'RIGHT' for arrow keys, character for printable keys,
    or special tokens like ESC. Works on both Windows (msvcrt) and Unix (termios).
    """
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            return {"\x48": "UP", "\x50": "DOWN", "\x4b": "LEFT", "\x4d": "RIGHT"}.get(ch2, "")
        if ch == "\x1b":
            return "ESC"
        return ch
    else:
        import tty, termios, select
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                r, _, _ = select.select([sys.stdin], [], [], 0.15)
                if r:
                    c2 = sys.stdin.read(1)
                    if c2 in ("[", "O"):
                        r2, _, _ = select.select([sys.stdin], [], [], 0.1)
                        if r2:
                            c3 = sys.stdin.read(1)
                            return {
                                "[A": "UP",
                                "OA": "UP",
                                "[B": "DOWN",
                                "OB": "DOWN",
                                "[C": "RIGHT",
                                "OC": "RIGHT",
                                "[D": "LEFT",
                                "OD": "LEFT",
                            }.get(c2 + c3, "ESC")
                    return "ESC"
                return "ESC"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def _clear_lines(n: int) -> None:
    """Rewind the terminal cursor N lines up and clear to end-of-screen."""
    if _ANSI:
        sys.stdout.write(f"\033[{n}A\033[J")
        sys.stdout.flush()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CONFIRM_TOKEN = "PRUNE-INSTALLED-SKILLS"

DEFAULT_PROTECTED = [
    "plugin-installer",
    "plugin-remover",
    "plugin-syncer",
    "plugin-pruner",
    "symlink-manager",
    "worktree-manager",
]

_STOPWORDS = {
    "a", "an", "the", "and", "or", "to", "in", "for", "with", "from", "by", "on", "at",
    "python", "python3", "pip", "node", "npm", "git", "bash", "linux", "macos", "windows",
    "docker", "all", "true", "false", "none", "null", "path", "file", "dir", "test",
    "command", "agent", "agents", "skill", "skills", "rule", "rules", "workflow", "workflows",
    "as", "is", "it", "if", "not", "be", "this", "that", "see", "uses", "requires", "required"
}

# ---------------------------------------------------------------------------
# Module import resolution & compatibility aliasing
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from retention_manifest import (
        load_manifest,
        save_manifest,
        get_component_states,
        parse_artifact,
        merge_installed_components,
    )
except ImportError:
    from plugins.plugin_manager.scripts.retention_manifest import (
        load_manifest,
        save_manifest,
        get_component_states,
        parse_artifact,
        merge_installed_components,
    )

if "plugins.plugin_manager" not in sys.modules:
    sys.modules["plugins.plugin_manager"] = types.ModuleType("plugins.plugin_manager")
if "plugins.plugin_manager.scripts" not in sys.modules:
    sys.modules["plugins.plugin_manager.scripts"] = types.ModuleType("plugins.plugin_manager.scripts")
sys.modules["plugins.plugin_manager.scripts.prune_installed_skills"] = sys.modules[__name__]


# ---------------------------------------------------------------------------
# Dependency Scanner Engine
# ---------------------------------------------------------------------------
def scan_dependencies(skills_dir: Path, retained_skills: Set[str]) -> Dict[str, Set[str]]:
    """Scans retained skills for references to rules, companion skills, and agents.

    Args:
        skills_dir: Path to the .agents/skills directory.
        retained_skills: Set of skill directory names currently marked for retention.

    Returns:
        Dictionary with keys 'skills', 'rules', and 'agents', each containing a set
        of discovered dependency names.
    """
    deps: Dict[str, Set[str]] = {
        "skills": set(),
        "rules": set(),
        "agents": set(),
    }
    skills_dir_path = Path(skills_dir)
    if not skills_dir_path.exists():
        return deps

    # Discover known on-disk skills for cross-reference matching
    known_skills = {
        p.name for p in skills_dir_path.iterdir() if p.is_dir() and not p.name.startswith(".")
    }

    for skill_name in retained_skills:
        skill_dir = skills_dir_path / skill_name
        if not skill_dir.is_dir():
            continue

        text_corpus: List[str] = []
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            try:
                text_corpus.append(skill_md.read_text(encoding="utf-8"))
            except Exception:
                pass

        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            for ref_file in refs_dir.glob("*.md"):
                try:
                    text_corpus.append(ref_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

        combined_text = "\n".join(text_corpus)
        if not combined_text:
            continue

        # 1. Rule references
        rule_matches = set()
        # Matches paths like .agent/rules/name.md or rules/name.md
        for match in re.findall(
            r"(?:(?:\.agents?|references)?/rules/|rules/)([a-zA-Z0-9_-]+\.md)", combined_text
        ):
            rule_matches.add(match)
        # Matches rule: 'name.md' or rule 'name.md'
        for match in re.findall(
            r"\b(?:rule|policy)[:\s]+[`'\"]?([a-zA-Z0-9_-]+\.md)[`'\"]?",
            combined_text,
            re.IGNORECASE,
        ):
            rule_matches.add(match)
        # Matches inline name-rule.md or name-policy.md
        for match in re.findall(
            r"[`'\"]([a-zA-Z0-9_-]+(?:-rule|-policy)\.md)[`'\"]", combined_text
        ):
            rule_matches.add(match)

        deps["rules"].update(rule_matches)

        # 2. Skill references
        skill_matches = set()
        # Explicit triggers: requires skill-b, depends on skill-b, companion skill-b
        for match in re.findall(
            r"(?:requires?|depends?\s+on|dependency|companion)\s+(?:the\s+)?(?:skill\s+)?[`'\"]?([a-zA-Z0-9_-]+)[`'\"]?",
            combined_text,
            re.IGNORECASE,
        ):
            skill_matches.add(match)

        # Path-based skill references: .agents/skills/foo or skills/foo
        for match in re.findall(
            r"(?:\.agents?/skills/|skills/)([a-zA-Z0-9_-]+)", combined_text
        ):
            skill_matches.add(match)

        # Superpowers namespace: superpowers:foo
        for match in re.findall(r"superpowers:([a-zA-Z0-9_-]+)", combined_text):
            skill_matches.add(match)

        # Delegation statements: delegates to skill foo, calls skill foo
        for match in re.findall(
            r"\b(?:delegate[s]?\s+to|calls?)\s+(?:skill\s+)?[`'\"]?([a-zA-Z0-9_-]+)[`'\"]?",
            combined_text,
            re.IGNORECASE,
        ):
            skill_matches.add(match)

        # Explicit skill 'foo'
        for match in re.findall(
            r"\bskill\s+[`'\"]([a-zA-Z0-9_-]+)[`'\"]", combined_text, re.IGNORECASE
        ):
            skill_matches.add(match)

        # Match known on-disk skill names if mentioned as distinct words
        for known in known_skills:
            if known != skill_name and re.search(rf"\b{re.escape(known)}\b", combined_text):
                skill_matches.add(known)

        # Filter out self-reference, stopwords, and short tokens
        for s in skill_matches:
            cleaned = s.strip("._-")
            if (
                cleaned
                and cleaned != skill_name
                and cleaned.lower() not in _STOPWORDS
                and len(cleaned) > 1
            ):
                deps["skills"].add(cleaned)

        # 3. Agent references
        for match in re.findall(
            r"(?:\.agents?/agents/|agents/)([a-zA-Z0-9_-]+(?:\.md)?)", combined_text
        ):
            clean_match = match.rstrip(".")
            dest = clean_match if clean_match.endswith(".md") else f"{clean_match}.md"
            deps["agents"].add(dest)

        for match in re.findall(
            r"\bagent\s+[`'\"]?([a-zA-Z0-9_-]+(?:\.md)?)[`'\"]?",
            combined_text,
            re.IGNORECASE,
        ):
            clean_match = match.rstrip(".")
            if clean_match and clean_match.lower() not in _STOPWORDS:
                dest = clean_match if clean_match.endswith(".md") else f"{clean_match}.md"
                deps["agents"].add(dest)

    return deps


def check_dependency_advisory(
    root: Path,
    manifest: Dict[str, Any],
    plugin_name: str,
    component_type: str,
    component_name: str,
) -> Optional[str]:
    """Checks if untoggling a component triggers a dependency warning from any retained skills.

    Args:
        root: Repository root path.
        manifest: Current manifest dictionary.
        plugin_name: Plugin owning the component.
        component_type: One of 'skills', 'rules', 'agents'.
        component_name: Name of the component.

    Returns:
        Advisory warning string if referenced by another retained skill, or None.
    """
    root_path = Path(root)
    skills_dir = root_path / ".agents" / "skills"
    if not skills_dir.exists():
        return None

    ctype = component_type.lower()
    if not ctype.endswith("s"):
        ctype += "s"

    skills_state, _, _ = get_component_states(manifest)
    retained_skills = {k for k, v in skills_state.items() if v}
    # If checking a skill being untoggled, exclude it so we see if other retained skills need it
    if ctype == "skills":
        retained_skills.discard(component_name)

    deps = scan_dependencies(skills_dir, retained_skills)

    if ctype == "skills":
        if component_name in deps["skills"]:
            return (
                f"[ADVISORY] Companion skill '{component_name}' is referenced by retained skill. "
                f"Consider retaining this skill."
            )
    elif ctype == "rules":
        candidates = [component_name]
        if component_name.endswith(".md"):
            candidates.append(component_name[:-3])
        else:
            candidates.append(f"{component_name}.md")
        for c in candidates:
            if c in deps["rules"]:
                return (
                    f"[ADVISORY] Rule '{component_name}' is referenced by retained skill. "
                    f"Consider retaining this rule."
                )
    elif ctype == "agents":
        candidates = [component_name]
        if component_name.endswith(".md"):
            candidates.append(component_name[:-3])
        else:
            candidates.append(f"{component_name}.md")
        for c in candidates:
            if c in deps["agents"]:
                return (
                    f"[ADVISORY] Agent '{component_name}' is referenced by retained skill. "
                    f"Consider retaining this agent."
                )

    return None


# ---------------------------------------------------------------------------
# Pruning Planner Engine
# ---------------------------------------------------------------------------
def plan_pruning(root: Path, manifest: Dict[str, Any]) -> Dict[str, List[Path]]:
    """Computes list of removable files and directories based on the retention manifest.

    Protected defaults are preserved even if unselected in the manifest.

    Args:
        root: Path to the repository root.
        manifest: Parsed dictionary from plugin-retention.json.

    Returns:
        Dictionary mapping component category ('skills', 'rules', 'agents') to lists
        of removable Path objects.
    """
    root_path = Path(root)
    protected_raw = manifest.get("protected_defaults", DEFAULT_PROTECTED)
    protected = set(protected_raw if isinstance(protected_raw, list) else DEFAULT_PROTECTED)

    skills_state, rules_state, agents_state = get_component_states(manifest)

    plan: Dict[str, List[Path]] = {
        "skills": [],
        "rules": [],
        "agents": [],
    }
    seen_paths: Set[Path] = set()

    # 1. Skills
    for skill_name, retained in skills_state.items():
        if not retained and skill_name not in protected:
            candidate = root_path / ".agents" / "skills" / skill_name
            if candidate.exists() and candidate not in seen_paths:
                plan["skills"].append(candidate)
                seen_paths.add(candidate)

    # 2. Rules
    for rule_name, retained in rules_state.items():
        if not retained and rule_name not in protected:
            candidate_rule_names = [rule_name]
            if rule_name.endswith(".md"):
                candidate_rule_names.append(rule_name[:-3])
            else:
                candidate_rule_names.append(f"{rule_name}.md")

            for r_name in candidate_rule_names:
                for candidate in [
                    root_path / ".agent" / "rules" / r_name,
                    root_path / ".agents" / "rules" / r_name,
                    root_path / "rules" / r_name,
                ]:
                    if candidate.exists() and candidate not in seen_paths:
                        plan["rules"].append(candidate)
                        seen_paths.add(candidate)

    # 3. Agents
    for agent_name, retained in agents_state.items():
        if not retained and agent_name not in protected:
            candidates_names = [agent_name]
            if agent_name.endswith(".md"):
                candidates_names.append(agent_name[:-3])
            else:
                candidates_names.append(f"{agent_name}.md")
            for c_name in candidates_names:
                for candidate in [
                    root_path / ".agents" / "agents" / c_name,
                    root_path / "agents" / c_name,
                    root_path / ".claude" / "agents" / c_name,
                ]:
                    if candidate.exists() and candidate not in seen_paths:
                        plan["agents"].append(candidate)
                        seen_paths.add(candidate)

    # 4. Cross-check against .agents/ownership manifests if present
    ownership_dir = root_path / ".agents" / "ownership"
    if ownership_dir.is_dir():
        for own_file in ownership_dir.glob("*.json"):
            try:
                own_data = json.loads(own_file.read_text(encoding="utf-8"))
                artifacts = own_data.get("artifacts", [])
                for art in artifacts:
                    ctype, cname = parse_artifact(art)
                    if not ctype or not cname or cname in protected:
                        continue
                    is_retained = True
                    if ctype == "skills":
                        is_retained = skills_state.get(cname, True)
                    elif ctype == "rules":
                        is_retained = rules_state.get(cname, None)
                        if is_retained is None:
                            if cname.endswith(".md"):
                                is_retained = rules_state.get(cname[:-3], True)
                            else:
                                is_retained = rules_state.get(f"{cname}.md", True)
                    elif ctype == "agents":
                        is_retained = agents_state.get(cname, None)
                        if is_retained is None:
                            if cname.endswith(".md"):
                                is_retained = agents_state.get(cname[:-3], True)
                            else:
                                is_retained = agents_state.get(f"{cname}.md", True)

                    if not is_retained:
                        art_path = root_path / art
                        if art_path.exists() and art_path not in seen_paths:
                            plan[ctype].append(art_path)
                            seen_paths.add(art_path)
            except Exception:
                pass

    return plan


# ---------------------------------------------------------------------------
# Execution Engine
# ---------------------------------------------------------------------------
def execute_pruning(
    removals: Dict[str, List[Path]],
    root: Optional[Path] = None,
    dry_run: bool = False,
) -> int:
    """Executes physical deletion of planned pruning artifacts.

    Removes files/directories and synchronizes skills-lock.json and ownership records.

    Args:
        removals: Dictionary mapping component type to lists of Path objects to remove.
        root: Optional repository root Path for updating lock and ownership files.
        dry_run: If True, simulates deletion without deleting files.

    Returns:
        Total count of items deleted (or planned for deletion in dry-run).
    """
    if root is None:
        root = Path.cwd()
    root_path = Path(root)

    deleted_count = 0
    all_removed_paths: List[Path] = []

    for category, paths in removals.items():
        for p in paths:
            if not p.exists() and not p.is_symlink():
                continue
            if dry_run:
                deleted_count += 1
                all_removed_paths.append(p)
            else:
                try:
                    if p.is_dir() and not p.is_symlink():
                        shutil.rmtree(p)
                    else:
                        p.unlink()
                    deleted_count += 1
                    all_removed_paths.append(p)
                except Exception as e:
                    print(yellow(f"Warning: Failed to delete {p}: {e}"))

    if not dry_run and deleted_count > 0:
        # Update skills-lock.json if any skills were removed
        if removals.get("skills"):
            pruned_skill_names = {p.name for p in removals["skills"]}
            lock_file = root_path / "skills-lock.json"
            if lock_file.exists():
                try:
                    lock_data = json.loads(lock_file.read_text(encoding="utf-8"))
                    if "skills" in lock_data and isinstance(lock_data["skills"], dict):
                        modified = False
                        for s in pruned_skill_names:
                            if s in lock_data["skills"]:
                                del lock_data["skills"][s]
                                modified = True
                        if modified:
                            lock_file.write_text(
                                json.dumps(lock_data, indent=2) + "\n", encoding="utf-8"
                            )
                except Exception as e:
                    print(yellow(f"Warning: Failed updating skills-lock.json: {e}"))

        # Update .agents/ownership/*.json manifests
        ownership_dir = root_path / ".agents" / "ownership"
        if ownership_dir.is_dir():
            pruned_rels = set()
            for p in all_removed_paths:
                try:
                    pruned_rels.add(str(p.relative_to(root_path)).replace("\\", "/"))
                except ValueError:
                    pass
            for own_file in ownership_dir.glob("*.json"):
                try:
                    own_data = json.loads(own_file.read_text(encoding="utf-8"))
                    if "artifacts" in own_data and isinstance(own_data["artifacts"], list):
                        orig_len = len(own_data["artifacts"])
                        own_data["artifacts"] = [
                            a for a in own_data["artifacts"] if a not in pruned_rels
                        ]
                        if len(own_data["artifacts"]) != orig_len:
                            own_file.write_text(
                                json.dumps(own_data, indent=2) + "\n", encoding="utf-8"
                            )
                except Exception:
                    pass

    return deleted_count


# ---------------------------------------------------------------------------
# State Helper & Interactive Multiselect TUI
# ---------------------------------------------------------------------------
def toggle_component_state(
    manifest: Dict[str, Any], plugin_name: str, component_type: str, component_name: str
) -> Dict[str, Any]:
    """Toggles the boolean retention state of a specific component in the manifest.
    Handles rule and agent names with or without '.md' extension.

    Args:
        manifest: Parsed manifest dictionary.
        plugin_name: Name of the plugin.
        component_type: One of 'skills', 'rules', 'agents'.
        component_name: Name of the component to toggle.

    Returns:
        Updated manifest dictionary.
    """
    if "plugins" in manifest and plugin_name in manifest["plugins"]:
        plugin_entry = manifest["plugins"][plugin_name]
        ctype = component_type.lower()
        if not ctype.endswith("s"):
            ctype += "s"

        if ctype in plugin_entry and isinstance(plugin_entry[ctype], dict):
            comp_dict = plugin_entry[ctype]
            if component_name in comp_dict:
                comp_dict[component_name] = not comp_dict[component_name]
            elif ctype in ("rules", "agents"):
                if component_name.endswith(".md") and component_name[:-3] in comp_dict:
                    comp_dict[component_name[:-3]] = not comp_dict[component_name[:-3]]
                elif not component_name.endswith(".md") and f"{component_name}.md" in comp_dict:
                    comp_dict[f"{component_name}.md"] = not comp_dict[f"{component_name}.md"]
    return manifest


class TUIState:
    """Encapsulates interactive TUI navigation, selection, and advisory state."""

    def __init__(self, manifest: Dict[str, Any], root: Path):
        self.root = Path(root)
        self.manifest = manifest
        self.plugins: List[str] = sorted(manifest.get("plugins", {}).keys())
        self.plugin_idx: int = 0
        self.cursor: int = 0
        self.search: str = ""
        self.search_mode: bool = False
        self.advisory: Optional[str] = None
        self.protected: Set[str] = set(manifest.get("protected_defaults", DEFAULT_PROTECTED))

    @property
    def current_plugin_name(self) -> str:
        if not self.plugins or self.plugin_idx >= len(self.plugins):
            return ""
        return self.plugins[self.plugin_idx]

    @property
    def raw_items(self) -> List[Dict[str, Any]]:
        """Returns all components for the current plugin."""
        plugin_name = self.current_plugin_name
        if not plugin_name:
            return []
        plugin_data = self.manifest.get("plugins", {}).get(plugin_name, {})
        items = []
        for ctype in ("skills", "rules", "agents"):
            for comp_name, retained in sorted(plugin_data.get(ctype, {}).items()):
                items.append({
                    "plugin": plugin_name,
                    "type": ctype,
                    "name": comp_name,
                    "retained": bool(retained),
                    "protected": comp_name in self.protected,
                })
        return items

    @property
    def current_items(self) -> List[Dict[str, Any]]:
        """Returns filtered components based on search query."""
        items = self.raw_items
        if not self.search:
            return items
        q = self.search.lower()
        return [i for i in items if q in i["name"].lower() or q in i["type"].lower()]


def tui_process_key(key: str, state: TUIState) -> bool:
    """Handles one keypress in the multiselect TUI.

    Args:
        key: String key token (e.g. 'UP', 'DOWN', ' ', 'n', 'p', '\\r', 'q').
        state: Active TUIState object.

    Returns:
        True if the user finished or quit, False otherwise.
    """
    if state.search_mode:
        if key == "ESC":
            state.search_mode = False
            state.search = ""
            state.cursor = 0
            return False
        elif key in ("\r", "\n"):
            state.search_mode = False
            state.cursor = 0
            return False
        elif key == "\x7f":
            if state.search:
                state.search = state.search[:-1]
            else:
                state.search_mode = False
            state.cursor = 0
            return False
        elif key in ("UP", "DOWN"):
            state.search_mode = False
            # proceed to cursor move below
        elif len(key) == 1 and key.isprintable():
            state.search += key
            state.cursor = 0
            return False

    if key in ("UP", "k", "K"):
        state.cursor = max(0, state.cursor - 1)
        return False
    elif key in ("DOWN", "j", "J"):
        items = state.current_items
        if items:
            state.cursor = min(len(items) - 1, state.cursor + 1)
        return False
    elif key in ("RIGHT", "n", "N", "l", "L"):
        if state.plugin_idx < len(state.plugins) - 1:
            state.plugin_idx += 1
            state.cursor = 0
            state.search = ""
            state.search_mode = False
            state.advisory = None
        return False
    elif key in ("LEFT", "p", "P", "h", "H"):
        if state.plugin_idx > 0:
            state.plugin_idx -= 1
            state.cursor = 0
            state.search = ""
            state.search_mode = False
            state.advisory = None
        return False
    elif key == " ":
        items = state.current_items
        if items and 0 <= state.cursor < len(items):
            item = items[state.cursor]
            if item.get("protected", False):
                state.advisory = f"[PROTECTED] '{item['name']}' is a protected default and cannot be untoggled."
                return False

            was_retained = item["retained"]
            toggle_component_state(state.manifest, item["plugin"], item["type"], item["name"])
            item["retained"] = not was_retained

            if was_retained:
                adv = check_dependency_advisory(
                    state.root, state.manifest, item["plugin"], item["type"], item["name"]
                )
                state.advisory = adv
            else:
                state.advisory = None
        return False
    elif key in ("\r", "\n"):
        if state.plugin_idx < len(state.plugins) - 1:
            state.plugin_idx += 1
            state.cursor = 0
            state.search = ""
            state.search_mode = False
            state.advisory = None
            return False
        else:
            return True
    elif key in ("q", "Q", "\x03", "c", "C"):
        return True
    elif key == "a":
        items = state.current_items
        if items:
            selectable = [i for i in items if not i.get("protected", False)]
            all_retained = all(i["retained"] for i in selectable) if selectable else True
            target = not all_retained
            plugin_data = state.manifest.get("plugins", {}).get(state.current_plugin_name, {})
            for ctype in ("skills", "rules", "agents"):
                for comp_name in plugin_data.get(ctype, {}):
                    if comp_name not in state.protected:
                        plugin_data[ctype][comp_name] = target
            state.advisory = None
        return False
    elif key == "/":
        state.search = ""
        state.search_mode = True
        state.cursor = 0
        return False
    elif key == "\x7f":
        if state.search:
            state.search = state.search[:-1]
            state.cursor = 0
        return False
    elif key == "ESC":
        state.search = ""
        state.search_mode = False
        state.cursor = 0
        return False

    return False


def _render_tui_page(state: TUIState, last_line_count: int = 0) -> int:
    """Renders the current plugin review page in the terminal."""
    PAGE = 18
    lines = []

    total_plugins = len(state.plugins)
    curr_idx = state.plugin_idx + 1 if total_plugins > 0 else 0
    plugin_name = state.current_plugin_name

    lines.append(bold(f"Plugin Retention Pruner — Reviewing [{curr_idx}/{total_plugins}]: {cyan(plugin_name)}"))
    lines.append(dim("  ↑↓/jk move  |  space toggle  |  ←/p prev  |  →/n next  |  a all  |  enter next/confirm  |  q quit"))

    if state.search_mode:
        lines.append(f"  {dim('Search:')} {cyan(state.search)}_")
    elif state.search:
        lines.append(f"  {dim('Filtered:')} {cyan(state.search)} {dim('(ESC to clear)')}")
    else:
        lines.append(dim("  Type / to search"))

    items = state.current_items
    visible = items[max(0, state.cursor - PAGE // 2) : state.cursor + PAGE]
    offset = max(0, state.cursor - PAGE // 2)
    last_type = None

    for idx, item in enumerate(visible):
        abs_idx = offset + idx
        ctype = item["type"]
        if ctype != last_type:
            lines.append(f"  {dim('─── ' + ctype.capitalize() + ' ───')}")
            last_type = ctype
        is_cursor = abs_idx == state.cursor
        is_retained = item["retained"]
        is_protected = item.get("protected", False)

        if is_protected:
            check = green("[x]")
            name = dim(item["name"] + " (protected)")
        elif is_retained:
            check = green("[x]")
            name = cyan(item["name"]) if is_cursor else item["name"]
        else:
            check = red("[ ]")
            name = dim(item["name"])

        arrow = ">" if is_cursor else " "
        lines.append(f"  {arrow} {check} {name}")

    if state.advisory:
        lines.append("")
        lines.append(f"  {yellow(state.advisory)}")

    retained_count = sum(1 for i in items if i["retained"])
    lines.append("")
    lines.append(f"  {green(str(retained_count))} of {len(items)} components retained in {plugin_name}")

    if last_line_count > 0:
        _clear_lines(last_line_count)
    print("\n".join(lines), flush=True)
    return len(lines)


def interactive_prune_tui(
    root: Path,
    manifest: Dict[str, Any],
    key_provider: Optional[Any] = None,
) -> Dict[str, Any]:
    """Runs interactive arrow-key multiselect TUI for reviewing and toggling retained components.

    Args:
        root: Path to repository root.
        manifest: Loaded manifest dictionary.
        key_provider: Optional callable returning key strings (used for testing).

    Returns:
        Updated manifest dictionary.
    """
    state = TUIState(manifest=manifest, root=root)
    if not state.plugins:
        return manifest

    is_interactive = sys.stdin.isatty() and sys.stdout.isatty() if key_provider is None else True
    if not is_interactive and key_provider is None:
        print(yellow("Warning: Interactive TUI requested in non-interactive terminal; skipping."))
        return manifest

    last_line_count = 0
    if is_interactive and key_provider is None:
        last_line_count = _render_tui_page(state, last_line_count=0)

    while True:
        key = key_provider() if key_provider is not None else _read_key()
        done = tui_process_key(key, state)
        if done:
            break
        if is_interactive and key_provider is None:
            last_line_count = _render_tui_page(state, last_line_count=last_line_count)

    if is_interactive and key_provider is None:
        print()
        print(green("Interactive review complete. Updated retention manifest in memory."))

    return state.manifest


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic pruning engine for .agents/ components based on plugin-retention.json"
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="plugin-retention.json",
        help="Path to plugin-retention.json (default: plugin-retention.json)",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Repository root directory (default: parent of manifest or cwd)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute physical pruning of unselected components",
    )
    parser.add_argument(
        "--confirm-token",
        type=str,
        default="",
        help=f"Confirmation token required with --execute ({CONFIRM_TOKEN})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate pruning plan without deleting files",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch interactive multiselect TUI",
    )

    args = parser.parse_args(argv)

    # Determine root and manifest paths
    manifest_arg = Path(args.manifest)
    if args.root:
        root_path = Path(args.root).resolve()
        manifest_file = manifest_arg if manifest_arg.is_absolute() else root_path / manifest_arg
    else:
        if manifest_arg.is_absolute():
            root_path = manifest_arg.parent.resolve()
            manifest_file = manifest_arg
        else:
            root_path = Path.cwd().resolve()
            manifest_file = root_path / manifest_arg

    if not manifest_file.exists():
        if args.interactive:
            template_path = _SCRIPT_DIR.parent / "assets" / "templates" / "plugin-retention.template.json"
            if template_path.exists():
                try:
                    manifest = load_manifest(template_path)
                except Exception:
                    manifest = {"version": 1, "protected_defaults": DEFAULT_PROTECTED, "plugins": {}}
            else:
                manifest = {"version": 1, "protected_defaults": DEFAULT_PROTECTED, "plugins": {}}

            # Seed from .agents/ownership/*.json
            ownership_dir = root_path / ".agents" / "ownership"
            seeded_any = False
            if ownership_dir.is_dir():
                for own_file in sorted(ownership_dir.glob("*.json")):
                    try:
                        p_name = own_file.stem
                        data = json.loads(own_file.read_text(encoding="utf-8"))
                        artifacts = data.get("artifacts", [])
                        existing_artifacts = [
                            a for a in artifacts if (root_path / a).exists()
                        ]
                        if existing_artifacts:
                            merge_installed_components(manifest, p_name, existing_artifacts)
                            seeded_any = True
                    except Exception:
                        pass

            # Fallback: scan .agents/skills if no ownership manifests found
            if not seeded_any:
                skills_dir = root_path / ".agents" / "skills"
                if skills_dir.is_dir():
                    for s_dir in sorted(skills_dir.iterdir()):
                        if s_dir.is_dir() and not s_dir.name.startswith("."):
                            merge_installed_components(
                                manifest, "installed-skills", [f".agents/skills/{s_dir.name}"]
                            )

            print(cyan(f"Initialized retention manifest from installed components: {manifest_file.name}"))
        else:
            print(red(f"Error: Manifest not found at {manifest_file}"))
            return 1
    else:
        try:
            manifest = load_manifest(manifest_file)
        except Exception as e:
            print(red(f"Error reading manifest: {e}"))
            return 1

    if args.interactive:
        manifest = interactive_prune_tui(root_path, manifest)
        save_manifest(manifest_file, manifest)
        try:
            rel_path = manifest_file.relative_to(root_path)
        except ValueError:
            rel_path = manifest_file
        print(green(f"Saved updated retention settings to {rel_path}"))

    skills_state, rules_state, agents_state = get_component_states(manifest)
    retained_skills = {k for k, v in skills_state.items() if v}
    skills_dir = root_path / ".agents" / "skills"

    # Dependency Scan & Advisories
    deps = scan_dependencies(skills_dir, retained_skills)
    plan = plan_pruning(root_path, manifest)

    pruned_skills = {p.name for p in plan["skills"]}
    pruned_rules = {p.name for p in plan["rules"]}
    pruned_agents = {p.name for p in plan["agents"]}

    advisories = []
    for r in sorted(deps["rules"]):
        if r in pruned_rules or (r.endswith(".md") and r[:-3] in pruned_rules) or (f"{r}.md" in pruned_rules):
            advisories.append(
                f"[ADVISORY] Rule '{r}' is referenced by retained skill. Consider retaining this rule."
            )
    for s in sorted(deps["skills"]):
        if s in pruned_skills:
            advisories.append(
                f"[ADVISORY] Companion skill '{s}' is referenced by retained skill. Consider retaining this skill."
            )
    for a in sorted(deps["agents"]):
        if a in pruned_agents or (a.endswith(".md") and a[:-3] in pruned_agents) or (f"{a}.md" in pruned_agents):
            advisories.append(
                f"[ADVISORY] Agent '{a}' is referenced by retained skill. Consider retaining this agent."
            )

    for adv in advisories:
        print(yellow(adv))

    total_items = sum(len(paths) for paths in plan.values())

    print()
    print(bold("Component Pruning Plan Summary:"))
    print(f"  Skills to remove:  {len(plan['skills'])}")
    print(f"  Rules to remove:   {len(plan['rules'])}")
    print(f"  Agents to remove:  {len(plan['agents'])}")
    print(f"  Total items:       {total_items}")
    print()

    if total_items == 0:
        print(green("Environment is in sync with retention manifest. Nothing to prune."))
        return 0

    for cat in ("skills", "rules", "agents"):
        paths = plan[cat]
        if paths:
            print(bold(f"  Removable {cat.capitalize()}:"))
            for p in sorted(paths, key=lambda x: str(x)):
                try:
                    rel = p.relative_to(root_path)
                except ValueError:
                    rel = p
                print(f"    - {rel}")
    print()

    # Dry-run check
    if not args.execute or args.dry_run:
        print(
            cyan(
                f"[DRY RUN] No files deleted. Use --execute --confirm-token {CONFIRM_TOKEN} to apply changes."
            )
        )
        return 0

    # Execute confirmation
    if args.confirm_token != CONFIRM_TOKEN:
        is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
        if is_interactive:
            try:
                entered = input(
                    f"Are you sure you want to prune {total_items} items? Type '{CONFIRM_TOKEN}' to confirm: "
                )
                if entered.strip() != CONFIRM_TOKEN:
                    print(red("Pruning aborted: token mismatch."))
                    return 1
            except (KeyboardInterrupt, EOFError):
                print(red("\nPruning aborted."))
                return 1
        else:
            print(red(f"Error: --execute requires --confirm-token {CONFIRM_TOKEN}"))
            return 1

    # Execute physical deletion
    deleted = execute_pruning(plan, root=root_path, dry_run=False)
    print(green(f"Successfully pruned {deleted} items from .agents/ environment."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
