#!/usr/bin/env python3
"""Read-only structural audit for agent rule policy specifications (.md) under rules/.

Purpose:
    Enforces rule metadata, invariant structure, and sanitization standards:
    1. Frontmatter: Valid YAML, description (<= 1024 chars), globs list or trigger.
    2. Size Budget: Progressive disclosure target 30–70 lines; hard ceiling <= 80 lines.
    3. Fluff Sanitization: Zero calendar dates (202X-XX-XX), zero machine paths (/Users/, /home/).
    4. Canonical Structure: "The Iron Law", "Invariants & Forbidden Actions", "Evaluation Checklist".
    5. Passive Boundary: Enforces policy constraints rather than active execution procedures.

Usage:
    python3 scripts/audit_rule.py /path/to/rule.md [--json] [--strict]
    python3 scripts/audit_rule.py /path/to/plugin_or_repo --all [--json] [--strict]
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

RULES = {
    "input.target": {"severity": "error", "message": "Invalid rule target path"},
    "metadata.frontmatter": {"severity": "error", "message": "Missing or malformed YAML frontmatter"},
    "metadata.description": {"severity": "error", "message": "Description must be nonempty and <= 1024 characters"},
    "metadata.scope": {"severity": "warning", "message": "Rule must declare 'globs' or 'trigger' in frontmatter"},
    "size.budget": {"severity": "warning", "message": "Rule exceeds target budget of 80 lines (target 30–70 lines)"},
    "fluff.dates": {"severity": "error", "message": "Historical calendar dates found; rules must be timeless invariants"},
    "fluff.paths": {"severity": "error", "message": "Absolute machine paths (/Users/, /home/) are prohibited"},
    "structure.the-law": {"severity": "warning", "message": "Missing core 'The Law' or 'The Iron Law' invariant block early"},
    "structure.invariants": {"severity": "warning", "message": "Missing explicit 'Invariants & Forbidden Actions' section"},
    "structure.checklist": {"severity": "warning", "message": "Missing 'Evaluation Checklist' or deterministic verification criteria"},
    "boundary.procedural": {"severity": "warning", "message": "Rule contains phased procedural workflows better suited for a skill"},
    "packaging.location": {"severity": "warning", "message": "Rule should reside in a 'rules/' folder"},
}


def parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    data = {}
    i = 1
    while i < end:
        match = re.match(r"^([\w-]+):\s*(.*)$", lines[i])
        if not match:
            i += 1
            continue
        key, value = match.groups()
        clean_val = re.split(r"\s+#", value, maxsplit=1)[0].strip()
        if clean_val in (">", "|", ">-", "|-", ">+", "|+") or not clean_val:
            parts = []
            while i + 1 < end and (lines[i + 1].startswith((" ", "\t")) or not lines[i + 1].strip()):
                i += 1
                parts.append(lines[i].strip())
            data[key] = " ".join(parts).strip()
        elif clean_val.startswith("[") and clean_val.endswith("]"):
            data[key] = clean_val
        elif (clean_val.startswith('"') and clean_val.endswith('"')) or (clean_val.startswith("'") and clean_val.endswith("'")):
            data[key] = clean_val[1:-1]
        else:
            data[key] = clean_val
        i += 1
    return data


@dataclass
class RuleAuditResult:
    rule_name: str
    file_path: Path
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    findings: list = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def add(self, rule: str, message: str, line: Optional[int] = None) -> None:
        definition = RULES.get(rule, {"severity": "warning"})
        severity = definition["severity"]
        finding = {"rule_id": rule, "severity": severity, "path": str(self.file_path), "line": line, "message": message}
        self.findings.append(finding)
        if severity == "error":
            self.errors.append(message)
            self.passed = False
        else:
            self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        plugin_name = self.file_path.parent.parent.name if self.file_path.parent.name == "rules" else None
        return {
            "schema_version": 2,
            "rule_name": self.rule_name,
            "file_path": str(self.file_path),
            "plugin": plugin_name,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "findings": self.findings,
            "metrics": self.metrics,
            "content_hash": self.content_hash,
        }


def audit_rule(path: Path) -> RuleAuditResult:
    path = path.resolve()
    name = path.stem
    result = RuleAuditResult(rule_name=name, file_path=path)

    if not path.is_file():
        result.add("input.target", f"File does not exist: {path}")
        return result

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as err:
        result.add("input.target", f"Cannot read file: {err}")
        return result

    result.content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    lines = content.splitlines()
    result.metrics["line_count"] = len(lines)

    # Line budget check
    if len(lines) > 80:
        result.add("size.budget", f"Rule has {len(lines)} lines; exceeds target ceiling of <= 80 lines")

    # Frontmatter check
    fm = parse_frontmatter(content)
    if fm is None:
        result.add("metadata.frontmatter", "Missing or malformed YAML frontmatter", 1)
        return result

    end_fm_idx = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), len(lines))
    body = "\n".join(lines[end_fm_idx + 1:])
    result.metrics["frontmatter_lines"] = end_fm_idx + 1
    result.metrics["body_lines"] = len(lines) - (end_fm_idx + 1)

    desc = str(fm.get("description", "")).strip()
    result.metrics["description_len"] = len(desc)
    if not desc:
        result.add("metadata.description", "Missing required frontmatter description", 2)
    elif len(desc) > 1024:
        result.add("metadata.description", f"Description exceeds 1024 characters ({len(desc)} chars)", 2)

    has_scope = "globs" in fm or "trigger" in fm
    if not has_scope:
        result.add("metadata.scope", "Missing 'globs' or 'trigger' field defining rule application scope")

    # Fluff sanitization: Calendar dates
    date_matches = list(re.finditer(r"202[0-9]-[0-9]{2}-[0-9]{2}", content))
    result.metrics["date_count"] = len(date_matches)
    if date_matches:
        for m in date_matches:
            line_no = content[:m.start()].count("\n") + 1
            result.add("fluff.dates", f"Found calendar date '{m.group(0)}' on line {line_no}; rules must be timeless invariants", line_no)

    # Fluff sanitization: Absolute machine paths
    path_matches = list(re.finditer(r"(?:/Users/|/home/|C:\\)[^\s\"'`]+", content))
    result.metrics["path_count"] = len(path_matches)
    if path_matches:
        for m in path_matches:
            line_no = content[:m.start()].count("\n") + 1
            result.add("fluff.paths", f"Found absolute machine path '{m.group(0)}' on line {line_no}", line_no)

    # Structural checks
    first_30_body_lines = "\n".join(lines[end_fm_idx + 1:end_fm_idx + 35])
    has_the_law = bool(re.search(r"##\s+(?:(?:\d+\.\s+)?(?:The\s+Law|The\s+Iron\s+Law|Core\s+Invariant))\b", first_30_body_lines, re.I))
    if not has_the_law:
        result.add("structure.the-law", "Missing early 'The Law' or 'The Iron Law' invariant block in first 30 lines")

    has_invariants = bool(re.search(r"##\s+(?:(?:\d+\.\s+)?(?:Invariants|Forbidden\s+Actions|The\s+Rule|Core\s+(?:Anti-Sycophancy\s+)?Principles|Principles|Invariants\s+&\s+Forbidden\s+Actions))\b", body, re.I))
    if not has_invariants:
        result.add("structure.invariants", "Missing 'Invariants & Forbidden Actions' section")

    has_checklist = bool(re.search(r"##\s+(?:(?:\d+\.\s+)?(?:Evaluation\s+Checklist|Verification|Checklist|Compliance))\b", body, re.I))
    if not has_checklist:
        result.add("structure.checklist", "Missing 'Evaluation Checklist' section")

    # Check for procedural drift
    if re.search(r"##\s+(?:Phase\s+\d+|Step\s+\d+|Workflow|Execution\s+Steps)", body, re.I):
        result.add("boundary.procedural", "Contains phased procedural workflow headings; multi-step workflows belong in skills")

    # Packaging location
    if path.parent.name != "rules":
        result.add("packaging.location", f"Rule file located in '{path.parent.name}', should be in a 'rules/' folder")

    return result


def discover_rules(target: Path) -> List[Path]:
    if target.is_file() and target.suffix == ".md":
        return [target]
    rules = []
    if (target / "rules").is_dir():
        rules.extend(sorted((target / "rules").glob("*.md")))
    elif target.name == "rules":
        rules.extend(sorted(target.glob("*.md")))
    else:
        rules.extend(sorted(target.glob("*/rules/*.md")))
        rules.extend(sorted(target.glob("plugins/**/rules/*.md")))
        rules.extend(sorted(target.glob(".agent/rules/*.md")))
    return [r for r in sorted(set(rules)) if r.name.lower() != "readme.md"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Path to rule markdown file or repository root")
    parser.add_argument("--all", action="store_true", help="Discover and scan all rules in target tree")
    parser.add_argument("--json", action="store_true", help="Output results in JSON envelope")
    parser.add_argument("--strict", action="store_true", help="Fail if any warnings are detected")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if args.all or target_path.is_dir():
        rule_paths = discover_rules(target_path)
        if not rule_paths:
            parser.exit(2, f"No rule markdown files found in {target_path}\n")
    else:
        if not target_path.is_file():
            parser.exit(2, f"Target rule file not found: {target_path}\n")
        rule_paths = [target_path]

    results = []
    for p in rule_paths:
        res = audit_rule(p)
        results.append(res.to_dict())

    total = len(results)
    failed = [r for r in results if not r["passed"] or (args.strict and r["warnings"])]
    findings = [f for r in results for f in r["findings"]]

    envelope = {
        "schema_version": 2,
        "summary": {
            "total_rules": total,
            "passed_count": total - len(failed),
            "failed_count": len(failed),
            "by_rule": dict(Counter(f["rule_id"] for f in findings)),
            "by_severity": dict(Counter(f["severity"] for f in findings)),
        },
        "rules": results if len(results) > 1 else results[0]
    }

    if args.json:
        print(json.dumps(envelope if (args.all or len(results) > 1) else results[0], indent=2))
    else:
        print("=" * 70)
        print("AGENT RULE INVARIANT & POLICY AUDIT REPORT")
        print("=" * 70)
        for r in results:
            status = "PASS" if r["passed"] else "FAIL"
            print(f"{status:<5} {r['file_path']}")
            for f in r["findings"]:
                print(f"  {f['severity'].upper():<7} {f['rule_id']}: {f['message']}")
        print("=" * 70)
        print(f"Total: {total} | Passed: {total - len(failed)} | Failed: {len(failed)}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
