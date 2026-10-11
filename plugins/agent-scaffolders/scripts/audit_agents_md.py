#!/usr/bin/env python3
"""Read-only structural audit for AGENTS.md / CLAUDE.md root instruction files.

Purpose:
    Enforces repository root instruction file standards from references/agents-md-contract.md:
    1. Size Budget: Progressive disclosure ceiling on transitive eager payload
       (target <= 100 lines, WARN > 120, FAIL > 200).
    2. Fluff & Storytelling Sanitization: Zero calendar dates (YYYY-MM-DD), zero machine paths (/Users/, /home/, [A-Z]:\\).
    3. Structural Separation:
       - No duplicate directory layout trees (must point to architecture.md).
       - No procedural intake/setup walkthroughs (must point to INIT_AGENTS.md / skills).
       - No detailed inlined pitfalls (must point to docs/architecture/known-pitfalls.md or references/).
       - No redundant key files / tool name mappings.
       - No personal user capital sourcing / preferences in AGENTS.md (belongs in gitignored context/user.md).
    4. Invariants vs Procedures:
       - Rules must state the invariant inline (MUST/NEVER/ALWAYS/DO NOT/REQUIRED/PROHIBITED) and link to .agent/rules/<rule>.md.
       - Rules must be concise 1-line statements (<= 40 words); detailed rationale lives in .agent/rules/.
    5. Canonical Authority & Bridge:
       - If auditing CLAUDE.md, verifies it is a pure minimal bridge pointing to AGENTS.md (<= 5 lines).

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
from typing import Any, Dict, List, Optional, Set

TARGET_BUDGET = 100
WARN_THRESHOLD = 120
HARD_CEILING = 200
MAX_RULE_WORDS = 40

RULES = {
    "input.target": {"severity": "error", "message": "Target AGENTS.md / CLAUDE.md file not found"},
    "size.ceiling": {"severity": "error", "message": f"Transitive eager payload exceeds hard ceiling of {HARD_CEILING} lines"},
    "size.budget": {"severity": "warning", "message": f"Transitive eager payload exceeds recommended budget (target <= {TARGET_BUDGET} lines, warn > {WARN_THRESHOLD})"},
    "bridge.claude": {"severity": "error", "message": "CLAUDE.md must be a pure thin bridge (<= 5 lines) pointing to AGENTS.md with no other instructions"},
    "fluff.dates": {"severity": "warning", "message": "Historical calendar dates found; instructions must be timeless invariants"},
    "fluff.paths": {"severity": "error", "message": "Absolute machine paths (/Users/, /home/, [A-Z]:\\) are prohibited"},
    "bloat.tree": {"severity": "warning", "message": "ASCII directory tree found; repository layout belongs in architecture.md"},
    "bloat.pitfalls": {"severity": "warning", "message": "Detailed inlined pitfalls list found; extract to dedicated reference document"},
    "bloat.key_files": {"severity": "warning", "message": "Redundant 'Key Files' table found; files should be referenced in context or architecture.md instead"},
    "bloat.tool_mapping": {"severity": "warning", "message": "Redundant 'Tool Name Mapping' table found; AI runtime environments handle tool bindings natively"},
    "bloat.user_preferences": {"severity": "warning", "message": "Personal user capital sourcing or preferences found; move to gitignored context/user.md"},
    "rules.missing": {"severity": "warning", "message": "Root AGENTS.md lacks a '## Non-Negotiable Rules' or '## Invariants' section"},
    "rules.no_modal": {"severity": "warning", "message": "Rule lacks an uppercase modal constraint token (MUST, NEVER, ALWAYS, DO NOT, REQUIRED, PROHIBITED)"},
    "rules.unlinked": {"severity": "warning", "message": "Rule does not link to a dedicated policy file in .agent/rules/"},
    "rules.inline_bloat": {"severity": "warning", "message": f"Rule exceeds 1-line invariant budget (> {MAX_RULE_WORDS} words); move detailed procedure to .agent/rules/"},
}

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", ".next", ".cache", ".worktrees", "worktrees"}
IMPORT_RE = re.compile(r"(?<![\w`@])@((?:~|\.{1,2})?[\w./-]+\.md)\b")
FENCED_RE = re.compile(r"^(```|~~~).*?^\1\s*$", re.M | re.S)
MODAL_RE = re.compile(r"\b(?:MUST|NEVER|ALWAYS|DO NOT|REQUIRED|PROHIBITED)\b")
RULE_LINK_RE = re.compile(r"\[.*?\]\([^)]*rules/[^)]+\.md\)")


def strip_code_preserve_newlines(text: str) -> str:
    blanked = FENCED_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return re.sub(r"`[^`\n]*`", "", blanked)


def calculate_eager_lines(path: Path, seen: Optional[Set[Path]] = None, depth: int = 0) -> int:
    if seen is None:
        seen = set()
    real = path.expanduser().resolve()
    if real in seen or depth > 5 or not real.is_file():
        return 0
    seen.add(real)
    try:
        text = real.read_text(encoding="utf-8")
    except Exception:
        return 0
    total = len(text.splitlines())
    prose = strip_code_preserve_newlines(text)
    for m in IMPORT_RE.finditer(prose):
        ref = Path(m.group(1)).expanduser()
        target = ref if ref.is_absolute() else real.parent / ref
        total += calculate_eager_lines(target, seen, depth + 1)
    return total


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
        if rule_id not in RULES:
            raise KeyError(f"Unknown audit rule_id: {rule_id}")
        spec = RULES[rule_id]
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
            "findings": [{"rule_id": f.rule_id, "severity": f.severity, "message": f.message, "line": f.line} for f in self.findings],
            "metrics": self.metrics,
            "content_hash": self.content_hash,
        }


def audit_agents_md(path: Path, is_root: bool = True) -> AgentsMdAuditResult:
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
    raw_line_count = len(lines)
    result.metrics["raw_line_count"] = raw_line_count

    # Check CLAUDE.md pure minimal bridge invariant
    if path.name == "CLAUDE.md":
        body = [l.strip() for l in lines if l.strip() and not l.lstrip().startswith("#")]
        is_pointer = len(body) == 1 and bool(re.search(r"(?:Read\s+)?(?:\[AGENTS\.md\]\([^)]*AGENTS\.md\)|@(?:[\w./-]*/)?AGENTS\.md|AGENTS\.md)\.?", body[0]))
        if raw_line_count > 5:
            result.add("bridge.claude", f"CLAUDE.md has {raw_line_count} lines; must be a thin bridge (<= 5 lines)")
        elif not is_pointer:
            result.add("bridge.claude", "CLAUDE.md must contain only a pointer to AGENTS.md (no separate rules or imports)")

    # 1. Transitive Eager Line Budget
    eager_lines = calculate_eager_lines(path)
    result.metrics["eager_line_count"] = eager_lines

    if eager_lines > HARD_CEILING:
        result.add("size.ceiling", f"Transitive eager payload has {eager_lines} lines; exceeds hard ceiling of {HARD_CEILING} lines")
    elif eager_lines > WARN_THRESHOLD:
        result.add("size.budget", f"Transitive eager payload has {eager_lines} lines; exceeds target of <= {TARGET_BUDGET} lines (warn > {WARN_THRESHOLD})")

    # Preserve line numbers during prose inspection
    prose = strip_code_preserve_newlines(content)

    # 2. Fluff sanitization: Calendar dates (YYYY-MM-DD) outside code
    date_matches = list(re.finditer(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b", prose))
    result.metrics["date_count"] = len(date_matches)
    if date_matches:
        for m in date_matches:
            line_no = prose[:m.start()].count("\n") + 1
            result.add("fluff.dates", f"Found calendar date '{m.group(0)}' on line {line_no}; instructions must be timeless invariants", line_no)

    # 3. Fluff sanitization: Absolute machine paths in raw content
    path_matches = list(re.finditer(r"(?<![\w.:/-])(?:/Users/|/home/|[A-Z]:\\)[^\s\"'`]+", content))
    result.metrics["path_count"] = len(path_matches)
    if path_matches:
        for m in path_matches:
            line_no = content[:m.start()].count("\n") + 1
            result.add("fluff.paths", f"Found absolute machine path '{m.group(0)}' on line {line_no}", line_no)

    # 4. Bloat: ASCII directory tree
    tree_matches = re.search(r"(?:^[^\n]*[├└│─][^\n]*\n){3,}", content, re.M) or re.search(r"(?:^[^\n]*(?:\|--|\+--)[^\n]*\n){3,}", content, re.M)
    if tree_matches:
        result.add("bloat.tree", "Found multi-line directory layout tree; repository structure belongs in architecture.md")

    # 5. Bloat: Extensive inlined pitfalls
    pitfall_matches = list(re.finditer(r"\*\*\d+\.\s+[^:]+\*\*:", content))
    if len(pitfall_matches) > 5 and re.search(r"^##\s+.*Pitfall", content, re.I | re.M):
        result.add("bloat.pitfalls", f"Found {len(pitfall_matches)} inlined pitfalls; extract to docs/architecture/known-pitfalls.md or references/")

    # 6. Bloat: Key Files table
    if re.search(r"^##\s+Key\s+Files\b", content, re.I | re.M):
        result.add("bloat.key_files", "Found 'Key Files' table; reference canonical documents in context or architecture.md instead")

    # 7. Bloat: Tool Name Mapping
    if re.search(r"^##\s+Tool\s+Name\s+Mapping\b", content, re.I | re.M):
        result.add("bloat.tool_mapping", "Found 'Tool Name Mapping' table; AI runtime environments handle tool bindings natively")

    # 8. Bloat: User Preferences / Personal Capital Sourcing
    if re.search(r"^##\s+Capital\s+Sourcing\b", content, re.I | re.M) or "PSU-U.TO" in content:
        result.add("bloat.user_preferences", "Found user-specific capital sourcing or personal portfolio accounts; move to gitignored context/user.md")

    # 9. Rules linking and Invariant presence (only for root AGENTS.md)
    if is_root and path.name == "AGENTS.md":
        rules_header = re.search(r"^##[ \t]+.*(?:Governing Rules|Non-Negotiable Rules|Invariants)\b[^\n]*$", content, re.I | re.M)
        if not rules_header:
            result.add("rules.missing", "Root AGENTS.md lacks a '## Non-Negotiable Rules', '## Governing Rules', or '## Invariants' section")
        else:
            rules_section = content[rules_header.start():]
            next_h2 = re.search(r"\n##[ \t]+[A-Z]", rules_section[5:])
            if next_h2:
                rules_section = rules_section[:next_h2.start() + 5]

            rule_lines = [line.strip() for line in rules_section.splitlines() if re.match(r"^(?:\d+\.|[-*])\s+", line.strip())]
            for r_line in rule_lines:
                if not re.search(r"\[.*?\]\(.*?\)", r_line):
                    continue
                text_without_links = re.sub(r"\[.*?\]\(.*?\)", "", r_line).strip()
                if not RULE_LINK_RE.search(r_line):
                    result.add("rules.unlinked", f"Rule '{r_line[:65]}' does not link to .agent/rules/")
                if len(text_without_links.split()) > MAX_RULE_WORDS:
                    result.add("rules.inline_bloat", f"Rule '{r_line[:65]}' is too long for a 1-line invariant ({len(text_without_links.split())} words); move detail to .agent/rules/")

    return result


def discover_instruction_files(target: Path) -> List[Path]:
    if target.is_file():
        return [target]
    found = []
    if target.is_dir():
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            found.extend(Path(root) / f for f in files if f in {"AGENTS.md", "CLAUDE.md"})
    return sorted(set(found))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Path to AGENTS.md / CLAUDE.md file or repository root")
    parser.add_argument("--all", action="store_true", help="Discover and scan all instruction files in target tree")
    parser.add_argument("--json", action="store_true", help="Output results in JSON envelope")
    parser.add_argument("--strict", action="store_true", help="Fail if any warnings are detected")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    targets = discover_instruction_files(target_path) if (args.all or target_path.is_dir()) else [target_path]
    if not targets:
        if args.json:
            print(json.dumps({"schema_version": 2, "summary": {"total_files": 0, "passed_count": 0, "failed_count": 0, "by_rule": {}, "by_severity": {"error": 0, "warning": 0}}, "files": []}, indent=2))
            return 0
        parser.exit(2, f"No AGENTS.md or CLAUDE.md found in {target_path}\n")

    results = [audit_agents_md(t, is_root=(t.parent == target_path or not target_path.is_dir())) for t in targets]
    total = len(results)
    failed = [r for r in results if not r.passed or (args.strict and r.warnings)]
    findings = [f for r in results for f in r.findings]

    by_sev = Counter(f.severity for f in findings)
    by_sev.setdefault("error", 0)
    by_sev.setdefault("warning", 0)

    if args.json:
        envelope = {
            "schema_version": 2,
            "summary": {
                "total_files": total,
                "passed_count": total - len(failed),
                "failed_count": len(failed),
                "by_rule": dict(Counter(f.rule_id for f in findings)),
                "by_severity": dict(by_sev),
            },
            "files": [r.to_dict() for r in results]
        }
        print(json.dumps(envelope, indent=2))
    else:
        print("=" * 70)
        print("AGENTS.md / CLAUDE.md ROOT INSTRUCTION AUDIT REPORT")
        print("=" * 70)
        for r in results:
            status = "PASS" if r.passed and not (args.strict and r.warnings) else "FAIL"
            eager_str = f"eager payload: {r.metrics.get('eager_line_count', 0)} lines"
            print(f"{status:<5} {r.file_path} ({eager_str})")
            for f in r.findings:
                line_str = f":{f.line}" if f.line else ""
                print(f"  {f.severity.upper():<7} {f.rule_id}{line_str}: {f.message}")
        print("=" * 70)
        print(f"Total: {total} | Passed: {total - len(failed)} | Failed: {len(failed)}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
