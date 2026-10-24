"""
scaffold.py (CLI)
=====================================

Purpose:
    Deterministically generates compliant directory architectures and boilerplate logic for Agent Skills, Plugins, Hooks, Commands, and Sub-Agents.

Key Input Dependencies:
    - Format templates located in ../assets/templates/ (README.md.jinja, SKILL.md.jinja, execute.py.jinja, agent.md.jinja, command.md.jinja)
    - argparse for CLI argument parsing
    - pathlib for path resolution

Layer: Meta-Execution

Usage Examples:
    pythonfold.py --type skill --name <skill-name> --path <output-dir> --desc "<description>"

Supported Object Types:
    - Plugins
    - Skills
    - Hooks
    - Sub-Agents
    - Commands

CLI Arguments:
    --type: The resource type to scaffold (plugin, skill, hook, etc).
    --name: The unique slug identifier for the resource.
    --path: Destination deployment directory.
    --desc: Short contextual description.
    --event: Lifecycle hook event (e.g. PreToolUse).
    --action: Hook action type.

Output:
    - Generated directory tree and markdown/json files at the requested --path.

Key Functions:
    - create_plugin()
    - create_skill()
    - create_hook()
    - create_sub_agent()
    - create_command()

Consumed by:
    - Agent Scaffolders logic (create-plugin, create-skill, etc.)
"""

import argparse
import os
import json
import re
from pathlib import Path


def get_template(filename: str) -> str | None:
    """Load a format template relative to the invoked source or installed script."""
    template_path = Path(__file__).absolute().parent.parent / "assets/templates" / filename
    return template_path.read_text(encoding="utf-8") if template_path.is_file() else None


def _create_skill_directories(skill_dir: str) -> None:
    """Create standard skill directory structure."""
    scripts_dir = os.path.join(skill_dir, "scripts")
    references_dir = os.path.join(skill_dir, "references")
    examples_dir = os.path.join(skill_dir, "examples")
    templates_dir = os.path.join(skill_dir, "templates")
    evals_dir = os.path.join(skill_dir, "evals")
    test_dir = os.path.join(skill_dir, "test")

    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(references_dir, exist_ok=True)
    os.makedirs(examples_dir, exist_ok=True)
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(evals_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)


def _create_skill_documentation(skill_dir: str, name: str, description: str) -> None:
    """Create SKILL.md, CONNECTORS.md, and reference files."""
    skill_template = get_template("SKILL.md.jinja")
    if skill_template:
        template_safe = skill_template.replace("${{", "{").replace("}}", "}")
        skill_content = template_safe.format(
            name=name,
            description=description,
            title_name=name.replace("-", " ").title(),
            plugins="${plugins}"
        )
    else:
        skill_content = "---snip---"

    with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)

    with open(os.path.join(skill_dir, "CONNECTORS.md"), "w") as f:
        f.write(f"# {name} Connectors Map\n\nMap abstract `~~category` tool requirements to exact system dependencies here to keep the plugin portable.")

    references_dir = os.path.join(skill_dir, "references")
    with open(os.path.join(references_dir, "architecture.md"), "w") as f:
        f.write(f"# {name} Protocol Reference\n\nPut deep context here so it is not loaded into context implicitly.")

    with open(os.path.join(references_dir, "acceptance-criteria.md"), "w") as f:
        f.write(f"# Acceptance Criteria: {name}\n\nDefine at least two testable criteria or correct/incorrect operational patterns here to ensure the skill functions correctly.")


def _create_skill_evals_and_diagram(skill_dir: str, name: str) -> None:
    """Create evals.json, results.tsv, and workflow diagram."""
    evals_dir = os.path.join(skill_dir, "evals")
    eval_set = [
        {"query": f"I need help using the {name} skill", "should_trigger": True},
        {"query": f"Can you use the {name} skill for me?", "should_trigger": True},
        {"query": "What time is it in New York?", "should_trigger": False},
        {"query": "How do I boil an egg?", "should_trigger": False}
    ]
    with open(os.path.join(evals_dir, "evals.json"), "w") as f:
        json.dump(eval_set, f, indent=2)

    with open(os.path.join(evals_dir, "results.tsv"), "w") as f:
        f.write("iteration\ttrain_score\ttest_score\tdecision\tnotes\tdescription\n")

    mmd_content = f"""stateDiagram-v2
    [*] --> Init
    Init --> Process : Execute {name}
    Process --> [*]
    """
    with open(os.path.join(skill_dir, f"{name}-flow.mmd"), "w") as f:
        f.write(mmd_content)


def _create_skill_execute_script(skill_dir: str, name: str, description: str) -> None:
    """Create execute.py script from template."""
    execute_template = get_template("execute.py.jinja")
    script_content = ""
    if execute_template:
        script_content = execute_template.format(
            description=description,
            name=name
        )
    else:
        script_content = "# Template failed to load"

    scripts_dir = os.path.join(skill_dir, "scripts")
    script_path = os.path.join(scripts_dir, "execute.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)


def create_skill(name: str, path: str, description: str, iteration: int | None = None,
                 variant: str = "instructional", plugin_root: str | None = None,
                 json_output: bool = False) -> dict:
    """Preflight a variant and generate a self-contained skill (the executable variant writes its script inside the skill)."""
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        raise ValueError("Skill name must be 1–64 lowercase letters, numbers or hyphens")
    if not description.strip() or len(description) > 1024 or re.search(r"<[^>]+>", description):
        raise ValueError("Description must be nonempty, <=1024 characters and contain no XML tags")
    filename = "SKILL.md.jinja" if variant == "instructional" else "SKILL-executable.md.jinja"
    template = get_template(filename)
    if template is None:
        raise ValueError(f"Missing required template: {filename}")
    contract_path = Path(__file__).absolute().parent.parent / "references/skill-authoring-contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    layout = contract["variants"][variant]
    if layout["template"] != filename:
        raise ValueError("Template and authoring contract disagree")
    base = Path(path).absolute()
    skill = base / ".history" / f"iteration-{iteration}" / name if iteration else base / name
    if skill.exists():
        raise ValueError(f"Output already exists: {skill}")
    script_name = name.replace("-", "_") + ".py"
    links = []
    script_content = None
    script_path = None
    if variant == "executable":
        script_template = get_template(layout["script_template"])
        if script_template is None:
            raise ValueError("Missing required template: execute.py.jinja")
        script_path = skill / "scripts" / script_name
        script_content = script_template.format(name=name, description=json.dumps(description))
        compile(script_content, str(script_path), "exec")
    content = template.format(name=name, description=json.dumps(description, ensure_ascii=False),
                              title_name=name.replace("-", " ").title(), purpose=description,
                              script_name=script_name)
    skill.mkdir(parents=True)
    for directory in layout["directories"]:
        (skill / directory).mkdir(exist_ok=True)
    (skill / "SKILL.md").write_text(content, encoding="utf-8")
    _create_skill_evals_and_diagram(str(skill), name)
    if script_path is not None:
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(script_content, encoding="utf-8")
    report = {"status": "generated", "skill_path": str(skill),
              "contract_version": contract["version"], "variant": variant, "links": links}
    print(json.dumps(report, indent=2) if json_output else
          f"Generated {variant} skill at {skill}; status: {report['status']}. Customize and evaluate before publishing.")
    return report


def main() -> None:
    """Parse CLI arguments and scaffold a skill."""
    parser = argparse.ArgumentParser(description="Skill scaffolder")
    parser.add_argument("--type", choices=["skill"], default="skill", help="Resource type (skills only; plugins, hooks and sub-agents have their own scaffolders)")
    parser.add_argument("--name", required=True, help="Skill name (1-64 lowercase letters, digits, hyphens)")
    parser.add_argument("--path", required=True, help="Destination skills directory")
    parser.add_argument("--desc", default="A generated resource.", help="Skill description")
    parser.add_argument("--iteration", type=int, help="Iteration number for safe rollback isolation (e.g., 1, 2)")
    parser.add_argument("--variant", choices=("instructional", "executable"), default="instructional")
    parser.add_argument("--plugin-root", default=None, help="Deprecated, ignored (skills are self-contained)")
    parser.add_argument("--json", action="store_true", help="JSON skill generation receipt")
    args = parser.parse_args()
    try:
        create_skill(args.name, args.path, args.desc, args.iteration, args.variant, args.plugin_root, args.json)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
