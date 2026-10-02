#!/usr/bin/env python3
"""Audit agent skills for complete compliance with the canonical template:
Pillar A: SKILL.md format and template alignment
Pillar B: Skill folder structure template

Purpose:
    Enforce canonical skill format and folder structure quality invariants:
    1. Frontmatter: Valid YAML, slug matching directory name, 3rd-person description.
    2. H1 Title: # <Title> or # <Title> (<skill-name>).
    3. ## Contents: Table of contents with valid markdown anchor links.
    4. ## Constraints / ## Critical Constraints: Core behavioral constraints.
    5. ## Quick start: Initial minimal execution command or starting step.
    6. ## Workflow: Phased or procedural execution steps.
    7. ## Verification: Observable verification steps and audit command.
    8. ## References: Required if references/ directory has markdown files.
    9. ## Dependencies: If present, must be listed in ## Contents.
    10. Banned legacy sections: No Available Commands, Safety Gates, Self-Evolution boilerplate.
    11. Size budget: <= 80 lines (preview limit <= 100 lines).
    12. Folder structure: Only SKILL.md in root; evals/evals.json required; no loose files; allowed dirs only.

Usage:
    python3 plugins/agent-scaffolders/scripts/audit_template_compliance.py [path] [--json] [--verbose]
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]

sys.path.insert(0, str(SCRIPT_DIR))
try:
    from audit_skill import audit_skill, discover, parse_frontmatter, prose_lines
except ImportError:
    raise ImportError("Could not import audit_skill from agent-scaffolders/scripts")

ALLOWED_SKILL_SUBDIRS = {"evals", "scripts", "references", "assets", "examples", "templates", "tests", "agents", ".history"}


@dataclass
class SkillComplianceResult:
    skill_name: str
    plugin: str
    skill_dir: str
    line_count: int
    is_compliant: bool = True
    is_content_compliant: bool = True
    is_folder_compliant: bool = True
    missing_sections: List[str] = field(default_factory=list)
    legacy_sections: List[str] = field(default_factory=list)
    content_issues: List[str] = field(default_factory=list)
    folder_issues: List[str] = field(default_factory=list)
    auditor_findings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def audit_template_compliance(skill_dir: Path) -> SkillComplianceResult:
    skill_dir = skill_dir.resolve()
    skill_name = skill_dir.name
    plugin_name = skill_dir.parent.parent.name if skill_dir.parent.name == "skills" else "standalone"
    skill_md = skill_dir / "SKILL.md"

    result = SkillComplianceResult(
        skill_name=skill_name,
        plugin=plugin_name,
        skill_dir=str(skill_dir),
        line_count=0
    )

    # =========================================================================
    # PILLAR B: FOLDER STRUCTURE TEMPLATE AUDIT
    # =========================================================================
    if not skill_md.is_file():
        result.folder_issues.append("Missing SKILL.md in skill root")
        result.is_folder_compliant = False
        result.is_content_compliant = False
        result.is_compliant = False
        return result

    # Check 1: No loose files in skill root (only SKILL.md allowed)
    loose_files = [
        item.name for item in skill_dir.iterdir()
        if item.is_file() and item.name != "SKILL.md" and not item.name.startswith(".")
    ]
    if loose_files:
        result.folder_issues.append(
            f"Loose files in skill root: {', '.join(sorted(loose_files))} (organize into references/, scripts/, or plugin root)"
        )

    # Check 2: evals/ directory and evals/evals.json
    evals_dir = skill_dir / "evals"
    evals_json = evals_dir / "evals.json"
    if not evals_dir.is_dir():
        result.folder_issues.append("Missing required evals/ directory in skill structure")
    elif not evals_json.is_file():
        result.folder_issues.append("Missing required evals/evals.json routing evaluations file")

    # Check 3: Allowed subdirectories whitelist
    disallowed_dirs = [
        item.name for item in skill_dir.iterdir()
        if item.is_dir() and item.name not in ALLOWED_SKILL_SUBDIRS and not item.name.startswith(".")
    ]
    if disallowed_dirs:
        result.folder_issues.append(
            f"Disallowed subdirectories: {', '.join(sorted(disallowed_dirs))} (only {sorted(ALLOWED_SKILL_SUBDIRS)} permitted)"
        )

    # Check 4: Empty resource directories
    for res_name in ("scripts", "references", "assets"):
        res_dir = skill_dir / res_name
        if res_dir.is_dir():
            entries = [f for f in res_dir.iterdir() if not f.name.startswith(".")]
            if not entries:
                result.folder_issues.append(f"Empty resource directory '{res_name}/' (remove if unused)")

    # =========================================================================
    # PILLAR A: SKILL.md FORMAT & CANONICAL TEMPLATE AUDIT
    # =========================================================================
    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        result.content_issues.append(f"Cannot read SKILL.md: {e}")
        result.is_content_compliant = False
        result.is_compliant = False
        return result

    lines = content.splitlines()
    line_count = len(lines)
    result.line_count = line_count

    # Line budget check
    if line_count > 80:
        result.content_issues.append(f"Line count ({line_count}) exceeds progressive disclosure target (<= 80 lines)")
    if line_count > 100:
        result.content_issues.append(f"Line count ({line_count}) exceeds preview hard limit (100 lines)")

    # Frontmatter check
    fm = parse_frontmatter(content)
    if fm is None:
        result.content_issues.append("Missing valid YAML frontmatter")
    else:
        name = fm.get("name", "")
        if name != skill_name:
            result.content_issues.append(f"Frontmatter name '{name}' does not match directory '{skill_name}'")
        desc = fm.get("description", "")
        if not desc or not isinstance(desc, str):
            result.content_issues.append("Frontmatter description is missing or empty")
        elif len(desc) > 1024:
            result.content_issues.append(f"Frontmatter description exceeds 1024 characters ({len(desc)} chars)")
        elif re.search(r"<[^>]+>", desc):
            result.content_issues.append("Frontmatter description contains prohibited XML tags")

    # Prose lines and Headings
    prose = prose_lines(content)
    h1_headings = []
    h2_headings = []
    for line_no, line in prose:
        m1 = re.match(r"^\s{0,3}#\s+(.+?)(?:\s+#+)?$", line)
        if m1:
            h1_headings.append((line_no, m1.group(1).strip()))
        m2 = re.match(r"^\s{0,3}##\s+(.+?)(?:\s+#+)?$", line)
        if m2:
            h2_headings.append((line_no, m2.group(1).strip()))

    h2_lower = [h[1].lower() for h in h2_headings]

    # H1 title check
    if not h1_headings:
        result.content_issues.append("Missing top-level H1 title heading (# <Title>)")

    # Section 1: ## Contents with local anchor links
    has_contents = any(re.match(r"^(?:table of )?(?:contents|navigation)\b", t) for t in h2_lower)
    has_anchor_links = any(re.search(r"\[[^\]]+\]\((#[^)]+)\)", line) for _, line in prose)
    if not has_contents:
        result.missing_sections.append("## Contents")
    elif not has_anchor_links:
        result.content_issues.append("## Contents section does not contain local markdown anchor links")

    # Section 2: ## Constraints or ## Critical Constraints
    has_constraints = any(re.match(r"^(?:critical\s+)?constraints\b", t) for t in h2_lower)
    if not has_constraints:
        result.missing_sections.append("## Constraints (or ## Critical Constraints)")

    # Section 3: ## Quick start
    has_quick_start = any(re.match(r"^quick\s*start\b", t) for t in h2_lower)
    if not has_quick_start:
        result.missing_sections.append("## Quick start")

    # Section 4: ## Workflow
    has_workflow = any(re.match(r"^workflow\b", t) for t in h2_lower)
    if not has_workflow:
        result.missing_sections.append("## Workflow")

    # Section 5: ## Verification
    has_verification = any(re.match(r"^verification\b", t) for t in h2_lower)
    if not has_verification:
        result.missing_sections.append("## Verification")

    # Section 6: References if skill directory has references/ with .md files
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir() and any(f.suffix == ".md" for f in refs_dir.iterdir()):
        has_references = any(re.match(r"^references\b", t) for t in h2_lower)
        has_ref_links = any(re.search(r"references/[^\s)]+", line) for _, line in prose)
        if not (has_references or has_ref_links):
            result.missing_sections.append("## References (or direct links to references/)")

    # Section 7: Dependencies listed in TOC if ## Dependencies exists
    has_dependencies = any(re.match(r"^dependencies\b", t) for t in h2_lower)
    if has_dependencies:
        has_dep_toc = any(re.search(r"\[[^\]]*dependencies[^\]]*\]\(#dependencies\)", line, re.I) for _, line in prose)
        if not has_dep_toc:
            result.content_issues.append("## Dependencies section is present but not listed in ## Contents")

    # Check for legacy forbidden sections
    legacy_patterns = [
        (r"available\s+commands", "## Available Commands"),
        (r"safety\s+&\s+validation\s+gates", "## Safety & Validation Gates"),
        (r"self-evolution\s+&\s+quality\s+loop", "## Self-Evolution & Quality Loop"),
        (r"architecture\s+&\s+principles", "## Architecture & Principles"),
        (r"execution\s+steps", "## Execution Steps"),
        (r"operational\s+invariants", "## Operational Invariants"),
        (r"execution\s+guardrails", "## Execution Guardrails"),
        (r"prerequisites", "## Prerequisites"),
    ]
    for line_no, title in h2_headings:
        for pat, legacy_name in legacy_patterns:
            if re.search(pat, title, re.I):
                result.legacy_sections.append(f"{legacy_name} (line {line_no})")

    # Run audit_skill for links and packaging symlink verification
    audit_res = audit_skill(skill_dir)
    result.auditor_findings = audit_res.findings
    if audit_res.errors:
        for err in audit_res.errors:
            if "missing required SKILL.md" not in err.lower():
                result.folder_issues.append(f"Symlink/evals error: {err}")

    # Determine compliance
    if result.missing_sections or result.legacy_sections or result.content_issues:
        result.is_content_compliant = False
    if result.folder_issues:
        result.is_folder_compliant = False

    result.is_compliant = result.is_content_compliant and result.is_folder_compliant
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Root repository directory, plugins directory, or specific skill path")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details for all skills including compliant ones")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()

    if (target_path / "SKILL.md").is_file():
        skills = [target_path]
    elif (target_path / "skills").is_dir():
        skills = sorted(p.parent for p in target_path.glob("skills/*/SKILL.md"))
    elif target_path.name == "plugins":
        skills = sorted(p.parent for p in target_path.glob("*/skills/*/SKILL.md"))
    else:
        canonical_skills, _, _ = discover(target_path)
        if not canonical_skills:
            canonical_skills = [p.parent for p in target_path.glob("plugins/*/skills/*/SKILL.md")]
        skills = sorted(canonical_skills)

    if not skills:
        print(f"Error: No canonical skills found in {target_path}", file=sys.stderr)
        return 2

    results: List[SkillComplianceResult] = []
    for skill_path in skills:
        res = audit_template_compliance(skill_path)
        results.append(res)

    total = len(results)
    compliant = [r for r in results if r.is_compliant]
    non_compliant = [r for r in results if not r.is_compliant]
    compliant_count = len(compliant)
    non_compliant_count = len(non_compliant)
    rate = (compliant_count / total * 100) if total else 0.0

    content_compliant = sum(1 for r in results if r.is_content_compliant)
    folder_compliant = sum(1 for r in results if r.is_folder_compliant)

    by_plugin = Counter(r.plugin for r in results)
    compliant_by_plugin = Counter(r.plugin for r in compliant)

    if args.json:
        payload = {
            "summary": {
                "total_skills": total,
                "fully_compliant_count": compliant_count,
                "non_compliant_count": non_compliant_count,
                "compliance_rate_percent": round(rate, 1),
                "pillar_a_content_compliant": content_compliant,
                "pillar_b_folder_compliant": folder_compliant,
                "by_plugin": {
                    plugin: {
                        "total": count,
                        "compliant": compliant_by_plugin.get(plugin, 0),
                        "non_compliant": count - compliant_by_plugin.get(plugin, 0)
                    }
                    for plugin, count in sorted(by_plugin.items())
                }
            },
            "skills": [r.to_dict() for r in results]
        }
        print(json.dumps(payload, indent=2))
        return 0 if non_compliant_count == 0 else 1

    # Human-readable Report
    print("=" * 80)
    print("CANONICAL SKILL TEMPLATE & FOLDER STRUCTURE AUDIT REPORT")
    print("=" * 80)
    print(f"Target:                           {target_path}")
    print(f"Total Skills Audited:             {total}")
    print(f"Fully Compliant (Both Pillars):   {compliant_count} ({rate:.1f}%)")
    print(f"Pillar A (SKILL.md Template):     {content_compliant}/{total} compliant")
    print(f"Pillar B (Folder Structure):      {folder_compliant}/{total} compliant")
    print(f"Non-Compliant Requiring Action:   {non_compliant_count}")
    print("-" * 80)
    print("COMPLIANCE BY PLUGIN:")
    print(f"{'Plugin':<30} | {'Total':<6} | {'Compliant':<10} | {'Non-Compliant':<14} | {'Rate':<6}")
    print("-" * 80)
    for plugin, count in sorted(by_plugin.items()):
        c = compliant_by_plugin.get(plugin, 0)
        nc = count - c
        p_rate = (c / count * 100) if count else 0.0
        print(f"{plugin:<30} | {count:<6} | {c:<10} | {nc:<14} | {p_rate:.1f}%")
    print("=" * 80)

    if non_compliant:
        print("\nNON-COMPLIANT SKILLS REQUIRING RETROFIT / CLEANUP:")
        print("-" * 80)
        for r in non_compliant:
            status = []
            if not r.is_content_compliant:
                status.append("CONTENT_FAIL")
            if not r.is_folder_compliant:
                status.append("FOLDER_FAIL")
            print(f"FAIL [{' + '.join(status)}]: [{r.plugin}] {r.skill_name} ({r.line_count} lines)")
            if r.missing_sections:
                print(f"  [Pillar A] Missing Sections:  {', '.join(r.missing_sections)}")
            if r.legacy_sections:
                print(f"  [Pillar A] Legacy Sections:   {', '.join(r.legacy_sections)}")
            if r.content_issues:
                for issue in r.content_issues:
                    print(f"  [Pillar A] Content Issue:     {issue}")
            if r.folder_issues:
                for issue in r.folder_issues:
                    print(f"  [Pillar B] Folder Issue:      {issue}")
            print()
    else:
        print("\nALL SKILLS ARE 100% COMPLIANT ACROSS BOTH PILLARS!")

    if args.verbose and compliant:
        print("\nCOMPLIANT SKILLS:")
        print("-" * 80)
        for r in compliant:
            print(f"PASS: [{r.plugin}] {r.skill_name} ({r.line_count} lines)")

    return 0 if non_compliant_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
