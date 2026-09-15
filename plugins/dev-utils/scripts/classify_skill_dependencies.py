#!/usr/bin/env python3
"""Dependency Classifier and Standardizer for Agent Skills.

Evaluates fully-resolved dependency chains across repository skills to classify them into:
- ELIGIBLE: Zero third-party packages required (standard library only) and no inter-skill capability dependencies.
- INELIGIBLE: One or more third-party packages or inter-skill capability dependencies in dependency chain.
- AMBIGUOUS: Missing requirements file, broken -r include, or unresolvable reference.

Supports genuinely read-only --check, --report, and mutating --apply.
Enforces H1 (path confinement via is_relative_to, atomic write, symlink rejection before resolve) and
H2 (hard exit sys.exit(1) outside .worktrees/ on --apply).
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

CANONICAL_ONE_LINER = "Requires Python 3.8+ (standard library only)."
DEPENDENCY_SECTION_PATTERN = re.compile(
    r"(?ms)^## Dependencies\s*\n(.*?)(?=\n(?:---+|#+ )\s|\Z)"
)


def enforce_worktree_confinement() -> None:
    """Enforce H2: Process isolation check for mutating operations."""
    cwd = Path.cwd().resolve()
    if ".worktrees" not in cwd.parts:
        print(
            "ERROR (H2): --apply must be executed inside a registered .worktrees directory. Aborting.",
            file=sys.stderr,
        )
        sys.exit(1)


def is_inter_skill_or_capability_dependency(sec_body: str) -> bool:
    """Returns True if the dependencies section specifies inter-skill or capability requirements."""
    return bool(
        re.search(r"-\s+\*\*`?[a-zA-Z0-9_-]+`?\*\*", sec_body)
        or "Evaluation gate" in sec_body
        or "Depends on:" in sec_body
    )


def resolve_req_chain(req_file: Path, visited: Set[Path] = None) -> Tuple[Set[str], List[str]]:
    """Recursively resolves requirement chains following -r includes and stand-in pointers."""
    if visited is None:
        visited = set()

    req_file = req_file.resolve()
    if req_file in visited:
        return set(), []
    visited.add(req_file)

    if not req_file.exists():
        return set(), [f"File not found: {req_file}"]

    packages: Set[str] = set()
    errors: List[str] = []

    try:
        content = req_file.read_text(encoding="utf-8").strip()
    except Exception as e:
        return set(), [f"Error reading {req_file}: {e}"]

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    # Check for single-line stand-in pointer
    if len(lines) == 1 and (lines[0].endswith(".txt") or lines[0].endswith(".in")) and not lines[0].startswith("-"):
        target_path = (req_file.parent / lines[0]).resolve()
        return resolve_req_chain(target_path, visited)

    for line in lines:
        if line.startswith("#"):
            continue
        if line.startswith("-r "):
            inc_rel = line[3:].strip()
            inc_path = (req_file.parent / inc_rel).resolve()
            inc_pkgs, inc_errs = resolve_req_chain(inc_path, visited)
            packages.update(inc_pkgs)
            errors.extend(inc_errs)
        elif line.startswith("-"):
            continue
        else:
            # Strip version specifiers and environment markers
            pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("!=")[0].split(";")[0].strip()
            if pkg:
                packages.add(pkg.lower())

    return packages, errors


def extract_dependencies_section(skill_file: Path) -> str | None:
    """Extracts the exact text of ## Dependencies section up to the next heading or divider."""
    content = skill_file.read_text(encoding="utf-8")
    match = DEPENDENCY_SECTION_PATTERN.search(content)
    if match:
        return match.group(0).strip()
    return None


def classify_all_skills(plugins_dir: Path) -> Dict[str, Any]:
    """Scans all skills in plugins_dir and classifies dependency eligibility."""
    eligible: List[str] = []
    ineligible: List[Dict[str, Any]] = []
    ambiguous: List[Dict[str, str]] = []

    for skill_file in sorted(plugins_dir.glob("*/skills/*/SKILL.md")):
        content = skill_file.read_text(encoding="utf-8")
        if "## Dependencies" not in content:
            continue

        match = DEPENDENCY_SECTION_PATTERN.search(content)
        sec_body = match.group(1).strip() if match else ""
        rel_path = str(skill_file.relative_to(plugins_dir.parent))

        # Check for inter-skill or capability dependencies
        if is_inter_skill_or_capability_dependency(sec_body):
            ineligible.append({
                "skill": rel_path,
                "reason": "Capability / inter-skill dependency (not python package requirements)",
            })
            continue

        skill_dir = skill_file.resolve().parent
        s_in = skill_dir / "requirements.in"
        s_req = skill_dir / "requirements.txt"
        p_in = skill_dir.parent.parent / "requirements.in"
        p_req = skill_dir.parent.parent / "requirements.txt"

        target_req: Path | None = None
        if s_in.exists():
            target_req = s_in
        elif s_req.exists():
            target_req = s_req
        elif p_in.exists():
            target_req = p_in
        elif p_req.exists():
            target_req = p_req

        if not target_req:
            ambiguous.append({
                "skill": rel_path,
                "reason": "No requirements.txt or requirements.in found in skill or plugin root",
            })
            continue

        packages, errors = resolve_req_chain(target_req)
        if errors:
            ambiguous.append({
                "skill": rel_path,
                "reason": "; ".join(errors),
            })
        elif len(packages) == 0:
            eligible.append(rel_path)
        else:
            ineligible.append({
                "skill": rel_path,
                "packages": sorted(list(packages)),
            })

    return {
        "eligible": eligible,
        "ineligible": [item["skill"] for item in ineligible],
        "ineligible_details": ineligible,
        "ambiguous": ambiguous,
    }


def apply_standardized_dependencies(
    eligible_skills: List[str], repo_root: Path
) -> List[str]:
    """Applies standardized one-liner to eligible skills using atomic writes and H1 constraints."""
    updated: List[str] = []
    plugins_resolved = (repo_root / "plugins").resolve()

    for rel_path in eligible_skills:
        candidate_file = repo_root / rel_path

        # H1 Target Confinement
        if candidate_file.name != "SKILL.md":
            print(f"Skipping {rel_path}: Not SKILL.md", file=sys.stderr)
            continue
        if candidate_file.is_symlink():
            print(f"Skipping {rel_path}: Symlink write rejected", file=sys.stderr)
            continue
        if not candidate_file.resolve().is_relative_to(plugins_resolved):
            print(f"Skipping {rel_path}: Outside plugins/", file=sys.stderr)
            continue

        content = candidate_file.read_text(encoding="utf-8")
        match = DEPENDENCY_SECTION_PATTERN.search(content)
        if not match:
            continue

        replacement = f"## Dependencies\n\n{CANONICAL_ONE_LINER}\n"
        new_content = content[:match.start()] + replacement + content[match.end():]

        if new_content != content:
            # Atomic write
            tmp_path = candidate_file.with_suffix(".tmp")
            original_mode = candidate_file.stat().st_mode
            tmp_path.write_text(new_content, encoding="utf-8")
            os.chmod(tmp_path, original_mode)
            os.replace(tmp_path, candidate_file)
            updated.append(rel_path)

    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and standardize skill dependencies.")
    parser.add_argument("--check", action="store_true", help="Read-only check for drift or unstandardized eligible skills.")
    parser.add_argument("--report", action="store_true", help="Emit JSON classification report to context/dependency-classification-report.json.")
    parser.add_argument("--apply", action="store_true", help="Apply standardized one-liner to confirmed ELIGIBLE skills.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root path.")

    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    plugins_dir = repo_root / "plugins"

    if args.apply:
        enforce_worktree_confinement()

    report = classify_all_skills(plugins_dir)

    # Save report to context ONLY on --report or --apply, never on --check (genuinely read-only)
    report_file = repo_root / "context" / "dependency-classification-report.json"
    if args.report or args.apply:
        if report_file.is_symlink():
            print(f"Error: Report target {report_file} is a symlink. Aborting write.", file=sys.stderr)
            return 1
        report_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_report = report_file.with_suffix(".tmp")
        tmp_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        os.replace(tmp_report, report_file)

    if args.check:
        unstandardized = []
        for rel_path in report["eligible"]:
            skill_file = repo_root / rel_path
            sec = extract_dependencies_section(skill_file)
            if not sec or CANONICAL_ONE_LINER not in sec or "pip-compile" in sec:
                unstandardized.append(rel_path)
        if unstandardized:
            print(f"Check failed: {len(unstandardized)} eligible skills need standardization:")
            for p in unstandardized:
                print(f"  - {p}")
            return 1
        print("Check passed: All eligible skills are standardized.")
        return 0

    if args.apply:
        updated = apply_standardized_dependencies(report["eligible"], repo_root)
        print(f"Applied standardized dependencies to {len(updated)} eligible skills.")
        return 0

    # Default report output
    print("Dependency Classification Summary:")
    print(f"  ELIGIBLE:   {len(report['eligible'])} skills")
    print(f"  INELIGIBLE: {len(report['ineligible'])} skills")
    print(f"  AMBIGUOUS:  {len(report['ambiguous'])} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
