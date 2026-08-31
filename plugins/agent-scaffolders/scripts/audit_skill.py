#!/usr/bin/env python3
"""
audit_skill.py
==============
Audits and aligns an individual agent skill against ecosystem evolution standards:
1. Lean Layer 1 procedural core (line budget <= 100 lines target)
2. Boolean evals schema (JSON array with 'should_trigger: bool')
3. Hub-and-spoke script architecture (ADR-002/ADR-003 - scripts must be symlinks)
4. Frontmatter standards (name matches directory, 3rd-person description <= 1024 chars)
5. Contract references (acceptance-criteria.md, fallback-tree.md)
6. Spoke hygiene (no raw logs, wiki notes, or session state in skills)

Usage:
  python3 audit_skill.py <path/to/skill> [--fix] [--json]
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SkillAuditResult:
    skill_name: str
    skill_dir: Path
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "skill_dir": str(self.skill_dir),
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied,
            "metrics": self.metrics,
        }


def parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Simple robust parser for YAML frontmatter between --- markers without third-party deps."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)
    else:
        return None

    # Parse simple key-values
    data: Dict[str, Any] = {}
    current_key = None
    desc_lines = []
    in_desc = False

    for line in fm_lines:
        if line.startswith("description:"):
            in_desc = True
            current_key = "description"
            val = line.split(":", 1)[1].strip()
            if val and val not in (">", "|", ">-", "|-"):
                desc_lines.append(val)
            continue
        elif in_desc:
            if re.match(r"^[a-zA-Z0-9_-]+:", line):
                in_desc = False
                data["description"] = " ".join(desc_lines).strip()
            else:
                desc_lines.append(line.strip())
                continue

        if ":" in line and not in_desc:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip().strip("\"'")
            data[k] = v

    if in_desc and desc_lines:
        data["description"] = " ".join(desc_lines).strip()

    return data


def audit_skill(
    skill_path: Path | str,
    plugin_root: Optional[Path | str] = None,
    fix: bool = False
) -> SkillAuditResult:
    skill_dir = Path(skill_path).resolve()
    skill_name = skill_dir.name
    res = SkillAuditResult(skill_name=skill_name, skill_dir=skill_dir)

    if not skill_dir.exists() or not skill_dir.is_dir():
        res.passed = False
        res.errors.append(f"Skill directory does not exist: {skill_dir}")
        return res

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        res.passed = False
        res.errors.append(f"Missing required SKILL.md in {skill_dir}")
        return res

    # 1. Check Line Budget
    try:
        content = skill_md.read_text(encoding="utf-8")
    except Exception as e:
        res.passed = False
        res.errors.append(f"Cannot read SKILL.md: {e}")
        return res

    lines = content.splitlines()
    line_count = len(lines)
    res.metrics["line_count"] = line_count

    if line_count > 100:
        res.warnings.append(
            f"SKILL.md exceeds 100 lines ({line_count} lines). "
            "Layer 1 procedural core standard recommends <= 100 lines; "
            "propose Progressive Disclosure offloading to references/."
        )

    # 2. Frontmatter Standards
    fm = parse_frontmatter(content)
    if not fm:
        res.passed = False
        res.errors.append("SKILL.md is missing valid YAML frontmatter between --- markers")
    else:
        name_val = fm.get("name")
        if not name_val:
            res.passed = False
            res.errors.append("Frontmatter missing required 'name' field")
        elif name_val != skill_name:
            if fix:
                content = re.sub(r"^name:\s*.*", f"name: {skill_name}", content, count=1, flags=re.MULTILINE)
                skill_md.write_text(content, encoding="utf-8")
                res.fixes_applied.append(f"Auto-aligned frontmatter name from '{name_val}' to '{skill_name}'")
            else:
                res.passed = False
                res.errors.append(f"Frontmatter name '{name_val}' does not match directory name '{skill_name}'")

        desc_val = fm.get("description", "")
        res.metrics["description_len"] = len(desc_val)
        if not desc_val:
            res.passed = False
            res.errors.append("Frontmatter missing required 'description' field")
        else:
            if len(desc_val) > 1024:
                res.passed = False
                res.errors.append(f"Description exceeds 1024 characters ({len(desc_val)} chars)")
            elif len(desc_val) > 800:
                res.warnings.append(f"Description length ({len(desc_val)} chars) exceeds 800 chars warning threshold")

            # Check 3rd person phrasing
            first_person = re.match(r"^(I\b|I will|This skill will|My\b)", desc_val.strip(), re.IGNORECASE)
            if first_person:
                res.warnings.append(
                    f"Description appears to use first-person '{first_person.group(0)}'. "
                    "Standards require third-person active verb (e.g. 'Extracts...', 'Orchestrates...')."
                )

    # 3. Evals Schema Compliance
    evals_file = skill_dir / "evals" / "evals.json"
    if not evals_file.exists():
        res.warnings.append("Missing evals/evals.json - routing verification evals are recommended")
    else:
        try:
            eval_raw = evals_file.read_text(encoding="utf-8")
            eval_data = json.loads(eval_raw)
            entries = None

            if isinstance(eval_data, dict):
                list_key = None
                for candidate in ("evals", "entries", "tests", "test_cases", "items"):
                    if candidate in eval_data and isinstance(eval_data[candidate], list):
                        list_key = candidate
                        break
                if not list_key and len(eval_data) == 1:
                    sole_val = next(iter(eval_data.values()))
                    if isinstance(sole_val, list):
                        list_key = next(iter(eval_data.keys()))

                if list_key:
                    if fix:
                        entries = eval_data[list_key]
                        eval_data = entries
                        evals_file.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
                        res.fixes_applied.append(f"Migrated evals.json from dict wrapper ('{list_key}') to root JSON array")
                    else:
                        res.passed = False
                        res.errors.append(f"evals.json must be a root JSON array, not wrapped in {{'{list_key}': [...]}}")
                        entries = eval_data[list_key]
                else:
                    res.passed = False
                    res.errors.append("evals.json must contain a JSON array of test cases")
            elif isinstance(eval_data, list):
                entries = eval_data
            else:
                res.passed = False
                res.errors.append("evals.json must contain a JSON array of test cases")

            if entries is not None and isinstance(entries, list):
                res.metrics["eval_count"] = len(entries)
                for idx, entry in enumerate(entries):
                    if not isinstance(entry, dict):
                        res.passed = False
                        res.errors.append(f"evals.json entry #{idx} is not an object")
                        continue
                    if "should_trigger" not in entry:
                        if fix:
                            entry["should_trigger"] = (entry.get("type") != "negative")
                            res.fixes_applied.append(f"Auto-inferred 'should_trigger: {entry['should_trigger']}' for eval #{idx}")
                        else:
                            res.passed = False
                            res.errors.append(
                                f"evals.json entry #{idx} (id: {entry.get('id', 'unknown')}) missing required 'should_trigger' boolean. "
                                "Legacy 'expected_behavior' schema is deprecated."
                            )
                if fix and res.fixes_applied and entries is not None:
                    evals_file.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")

        except Exception as e:
            res.passed = False
            res.errors.append(f"evals/evals.json is malformed JSON: {e}")

    # 4. Hub-and-Spoke Script Architecture (ADR-002 / ADR-003)
    skill_scripts = skill_dir / "scripts"
    if skill_scripts.exists() and skill_scripts.is_dir():
        for script_file in skill_scripts.iterdir():
            if script_file.is_file() and not script_file.name.startswith("."):
                # Must be a symlink!
                if not script_file.is_symlink():
                    res.passed = False
                    res.errors.append(
                        f"Violates ADR-002/ADR-003 hub-and-spoke: '{script_file.name}' is a real file, not a symlink. "
                        "Shared scripts must reside in plugin root scripts/ and be symlinked via symlink_manager.py."
                    )

    # 5. Contract References (acceptance-criteria.md, fallback-tree.md)
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        res.warnings.append("Skill missing references/ directory. Progressive Disclosure is recommended.")
    else:
        ac_file = refs_dir / "acceptance-criteria.md"
        if not ac_file.exists():
            res.warnings.append("Missing references/acceptance-criteria.md contract link.")
        fb_file = refs_dir / "fallback-tree.md"
        if not fb_file.exists():
            res.warnings.append("Missing references/fallback-tree.md fallback protocol link.")

    # 6. Spoke Hygiene (zero raw telemetry or wiki notes in spoke)
    for bad_name in ("wiki", "traces", ".agent", "raw"):
        if (skill_dir / bad_name).exists():
            res.passed = False
            res.errors.append(f"Spoke hygiene violation: '{bad_name}' directory found in skill. Spoke must remain clean.")

    return res


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit and align an agent skill against evolution standards.")
    parser.add_argument("skill_path", nargs="?", default=None, help="Path to skill directory to audit")
    parser.add_argument("--all", action="store_true", help="Audit all skills in the repository or target path")
    parser.add_argument("--plugin-root", default=None, help="Optional plugin root directory")
    parser.add_argument("--fix", action="store_true", help="Auto-repair fixable schema issues")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if args.all or (args.skill_path and Path(args.skill_path).is_dir() and not (Path(args.skill_path) / "SKILL.md").exists()):
        base_dir = Path(args.skill_path) if args.skill_path else Path.cwd()
        skill_mds = sorted(list(base_dir.glob("plugins/**/skills/*/SKILL.md")) + list(base_dir.glob("skills/*/SKILL.md")) + list(base_dir.glob(".agents/skills/*/SKILL.md")))
        seen = set()
        skills = []
        for smd in skill_mds:
            s_dir = smd.parent.resolve()
            if s_dir not in seen:
                seen.add(s_dir)
                skills.append(smd.parent)

        if not skills:
            print("No skills found to audit.")
            return 0

        total_errors = 0
        results = []
        for s in skills:
            r = audit_skill(s, plugin_root=args.plugin_root, fix=args.fix)
            results.append(r.to_dict())
            if not r.passed:
                total_errors += 1
            if not args.json:
                status_symbol = "✅ PASS" if r.passed else "❌ FAIL"
                print(f"[{status_symbol}] {r.skill_name} ({s})")
                if r.fixes_applied:
                    for f in r.fixes_applied:
                        print(f"  ✓ {f}")
                if r.errors:
                    for e in r.errors:
                        print(f"  ✖ {e}")

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\nAudited {len(skills)} skills. {total_errors} failed.")

        return 0 if total_errors == 0 else 1

    if not args.skill_path:
        parser.error("skill_path or --all is required")

    result = audit_skill(args.skill_path, plugin_root=args.plugin_root, fix=args.fix)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        status_symbol = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"\n--- Skill Audit: {result.skill_name} [{status_symbol}] ---")
        print(f"Directory: {result.skill_dir}")
        print(f"Metrics:   Lines: {result.metrics.get('line_count', 'N/A')} | "
              f"Desc: {result.metrics.get('description_len', 'N/A')} chars | "
              f"Evals: {result.metrics.get('eval_count', 0)}")

        if result.fixes_applied:
            print("\n🔧 Fixes Applied:")
            for fix_item in result.fixes_applied:
                print(f"  ✓ {fix_item}")

        if result.errors:
            print("\n🚨 Errors:")
            for err in result.errors:
                print(f"  ✖ {err}")

        if result.warnings:
            print("\n⚠️ Warnings:")
            for warn in result.warnings:
                print(f"  ! {warn}")

        print("")

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
