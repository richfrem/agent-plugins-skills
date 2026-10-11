#!/usr/bin/env python3
"""Read-only structural audit for AGENTS.md / CLAUDE.md root instruction files.

Purpose:
    Enforces repository root instruction file standards:
    1. Size Budget: Progressive disclosure ceiling (target <= 150 lines, max 200).
    2. Fluff & Storytelling Sanitization: Zero calendar dates (202X-XX-XX), zero machine paths (/Users/, /home/).
    3. Structural Separation:
       - No duplicate directory layout trees (must point to architecture.md).
       - No procedural intake/setup walkthroughs (must point to INIT_AGENTS.md / work-intake).
       - No detailed inlined pitfalls (must point to docs/architecture/known-pitfalls.md).
       - No redundant key files / tool name mappings (context window bloat).
    4. Non-Negotiable Rules: Rules must be concise invariants with markdown links to .agent/rules/<rule>.md.

Usage:
    python3 scripts/audit_agents_md.py /path/to/AGENTS.md [--json] [--strict]
    python3 scripts/audit_agents_md.py /path/to/repo [--all] [--json] [--strict]
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
    "input.target": {"severity": "error", "message": "Target AGENTS.md / CLAUDE.md file not found"},
    "size.budget": {"severity": "warning", "message": "Root instruction file exceeds progressive disclosure budget (target <= 150 lines)"},
    "fluff.dates": {"severity": "error", "message": "Historical calendar dates found; instructions must be timeless invariants"},
    "fluff.paths": {"severity": "error", "message": "Absolute machine paths (/Users/, /home/, C:\\) are prohibited"},
    "bloat.tree": {"severity": "warning", "message": "ASCII directory tree found; repository layout must link to architecture.md"},
    "bloat.pitfalls": {"severity": "warning", "message": "Detailed inlined pitfalls list found; extract to dedicated reference document"},
    "bloat.key_files": {"severity": "warning", "message": "Redundant 'Key Files' table found; files should be referenced in context or architecture.md"},
    "bloat.tool_mapping": {"severity": "warning", "message": "Redundant 'Tool Name Mapping' table found; runtimes handle native tool mappings"},
    "rules.links": {"severity": "warning", "message": "Non-negotiable rules section lacks links to dedicated policy rules in .agent/rules/"},
}


@dataclass
class AuditFinding:
    rule_id: str
    severity: str
    message: str
    line: Optional[int] = None


@dataclass
class AgentsMdAuditResult:
    file_path: Path
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    findings: List[AuditFinding] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""

    def add(self, rule_id: str, message: str, line: Optional[int] = None) -> None:
        spec = RULES.get(rule_id, {"severity": "warning"})
        severity = spec["severity"]
        finding = AuditFinding(rule_id, severity, message, line)
        self.findings.append(finding)
        if severity == "error":
            self.errors.append(message)
            self.passed = False
        else:
            self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": str(self.file_path),
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "message": f.message,
                    "line": f.line,
                }
                for f in self.findings
            ],
            "metrics": self.metrics,
            "content_hash": self.content_hash,
        }


def audit_agents_md(path: Path) -> AgentsMdAuditResult:
    result = AgentsMdAuditResult(file_path=path)
    if not path.is_file():
        result.add("input.target", f"File does not exist: {path}")
        return result

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        result.add("input.target", f"Failed to read file: {e}")
        return result

    result.content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    lines = content.splitlines()
    line_count = len(lines)
    result.metrics["line_count"] = line_count

    # 1. Size budget
    if line_count > 150:
        result.add("size.budget", f"File has {line_count} lines; exceeds progressive disclosure target of <= 150 lines")

    # 2. Fluff sanitization: Calendar dates (202X-XX-XX)
    date_matches = list(re.finditer(r"202[0-9]-[0-9]{2}-[0-9]{2}", content))
    result.metrics["date_count"] = len(date_matches)
    if date_matches:
        for m in date_matches:
            line_no = content[:m.start()].count("\n") + 1
            result.add("fluff.dates", f"Found calendar date '{m.group(0)}' on line {line_no}; instructions must be timeless invariants", line_no)

    # 3. Fluff sanitization: Absolute machine paths
    path_matches = list(re.finditer(r"(?:/Users/|/home/|C:\\)[^\s\"'`]+", content))
    result.metrics["path_count"] = len(path_matches)
    if path_matches:
        for m in path_matches:
            line_no = content[:m.start()].count("\n") + 1
            result.add("fluff.paths", f"Found absolute machine path '{m.group(0)}' on line {line_no}", line_no)

    # 4. Bloat: ASCII directory tree
    if re.search(r"```(?:\w+)?\n(?:[^\n]*[├└│─][^\n]*\n){3,}", content):
        result.add("bloat.tree", "Found multi-line ASCII directory tree; repository structure belongs in architecture.md")

    # 5. Bloat: Extensive inlined pitfalls
    pitfall_matches = list(re.finditer(r"\*\*\d+\.\s+[^:]+\*\*:", content))
    if len(pitfall_matches) > 5 and re.search(r"##\s+.*Pitfall", content, re.I):
        result.add("bloat.pitfalls", f"Found {len(pitfall_matches)} inlined pitfalls; extract to docs/architecture/known-pitfalls.md")

    # 6. Bloat: Key Files table
    if re.search(r"##\s+Key\s+Files\b", content, re.I):
        result.add("bloat.key_files", "Found 'Key Files' table; reference canonical documents in context or architecture.md instead")

    # 7. Bloat: Tool Name Mapping
    if re.search(r"##\s+Tool\s+Name\s+Mapping\b", content, re.I):
        result.add("bloat.tool_mapping", "Found 'Tool Name Mapping' table; AI runtime environments handle tool bindings natively")

    # 8. Rules linking
    rules_header = re.search(r"##\s+(?:Non-Negotiable\s+)?Rules\b", content, re.I)
    if rules_header:
        rules_section = content[rules_header.start():]
        # Next H2 boundary
        next_h2 = re.search(r"\n##\s+", rules_section[5:])
        if next_h2:
            rules_section = rules_section[:next_h2.start() + 5]
        if not re.search(r"\[.*?\]\([^)]*rules/[^)]+\.md\)", rules_section):
            result.add("rules.links", "Rules section lacks links to modular policy files in .agent/rules/")

    return result


def discover_instruction_files(target: Path) -> List[Path]:
    if target.is_file() and target.name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md"):
        return [target]
    found = []
    candidates = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]
    if target.is_dir():
        for name in candidates:
            p = target / name
            if p.is_file():
                found.append(p)
        for sub in sorted(target.glob("*/AGENTS.md")):
            found.append(sub)
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Path to AGENTS.md / CLAUDE.md file or repository root")
    parser.add_argument("--all", action="store_true", help="Discover and scan all instruction files in target tree")
    parser.add_argument("--json", action="store_true", help="Output results in JSON envelope")
    parser.add_argument("--strict", action="store_true", help="Fail if any warnings are detected")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if args.all or target_path.is_dir():
        files = discover_instruction_files(target_path)
        if not files:
            parser.exit(2, f"No AGENTS.md or CLAUDE.md files found in {target_path}\n")
    else:
        if not target_path.is_file():
            parser.exit(2, f"Target instruction file not found: {target_path}\n")
        files = [target_path]

    results = []
    for f in files:
        res = audit_agents_md(f)
        results.append(res.to_dict())

    total = len(results)
    failed = [r for r in results if not r["passed"] or (args.strict and r["warnings"])]
    findings = [finding for r in results for finding in r["findings"]]

    envelope = {
        "schema_version": 2,
        "summary": {
            "total_files": total,
            "passed_count": total - len(failed),
            "failed_count": len(failed),
            "by_rule": dict(Counter(f["rule_id"] for f in findings)),
            "by_severity": dict(Counter(f["severity"] for f in findings)),
        },
        "files": results if len(results) > 1 else results[0]
    }

    if args.json:
        print(json.dumps(envelope if (args.all or len(results) > 1) else results[0], indent=2))
    else:
        print("=" * 70)
        print("AGENTS.md / CLAUDE.md ROOT INSTRUCTION AUDIT REPORT")
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
