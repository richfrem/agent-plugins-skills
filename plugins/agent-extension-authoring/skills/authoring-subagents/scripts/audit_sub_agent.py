#!/usr/bin/env python3
"""Read-only structural audit for agent specifications (.md) under agents/.

Purpose:
    Enforces sub-agent metadata, persona design, and packaging invariants:
    1. Frontmatter: Valid YAML, slug matching filename, model, color, tools.
    2. Description: 3rd-person scope statement, 2-4 <example> trigger blocks.
    3. System Prompt: 2nd-person address (You are...), clear responsibilities, output expectations.
    4. Packaging: Flat file in agents/, no pointer-wrappers delegating to skills.

Usage:
    python3 scripts/audit_sub_agent.py /path/to/agent.md [--json] [--strict]
    python3 scripts/audit_sub_agent.py /path/to/plugin_or_repo --all [--json] [--strict]
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

VALID_MODELS = frozenset({"inherit", "sonnet", "opus", "haiku", "cheap"})
VALID_COLORS = frozenset({"blue", "cyan", "green", "yellow", "magenta", "red", "purple", "orange"})
GENERIC_NAMES = frozenset({"helper", "assistant", "agent", "tool"})

RULES = {
    "input.target": {"severity": "error", "message": "Invalid agent target path"},
    "metadata.frontmatter": {"severity": "error", "message": "Missing or malformed YAML frontmatter"},
    "metadata.name": {"severity": "error", "message": "Agent name must be 3–50 chars matching filename slug"},
    "metadata.model": {"severity": "error", "message": "Missing or invalid model parameter"},
    "metadata.color": {"severity": "error", "message": "Missing or invalid UI color badge"},
    "metadata.description": {"severity": "error", "message": "Description missing or invalid"},
    "metadata.examples": {"severity": "warning", "message": "Description should contain 2–4 <example> trigger blocks"},
    "prompt.address": {"severity": "warning", "message": "System prompt should use second person (You are...)"},
    "prompt.structure": {"severity": "warning", "message": "System prompt should define clear responsibilities or process steps"},
    "packaging.wrapper": {"severity": "error", "message": "Pointer-wrapper stub merely delegating to a skill is forbidden"},
    "packaging.location": {"severity": "warning", "message": "Sub-agent should be a flat markdown file under an agents/ directory"},
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
class AgentAuditResult:
    agent_name: str
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
        plugin_name = self.file_path.parent.parent.name if self.file_path.parent.name == "agents" else None
        return {
            "schema_version": 2,
            "agent_name": self.agent_name,
            "file_path": str(self.file_path),
            "plugin": plugin_name,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "findings": self.findings,
            "metrics": self.metrics,
            "content_hash": self.content_hash,
        }


def audit_agent(path: Path) -> AgentAuditResult:
    # Check if the file is a symlink pointing to a skill (SKILL_ALIAS)
    is_symlink = path.is_symlink()
    symlink_target = None
    if is_symlink:
        try:
            symlink_target = os.readlink(path)
        except OSError:
            pass

    resolved_path = path.resolve()
    name = path.stem
    result = AgentAuditResult(agent_name=name, file_path=resolved_path)

    if is_symlink and (symlink_target and "skills/" in symlink_target and symlink_target.endswith(".md")):
        # Recognized SKILL_ALIAS per destructive-action-guard Part 2 Step 4
        result.metrics["is_alias"] = True
        result.metrics["alias_target"] = symlink_target
        if not resolved_path.is_file():
            result.add("packaging.alias", f"Broken SKILL_ALIAS symlink pointing to non-existent target: {symlink_target}", 1)
        return result

    if not resolved_path.is_file():
        result.add("input.target", f"File does not exist: {resolved_path}")
        return result

    if path.name.lower() == "readme.md":
        result.add("packaging.location", "README.md found inside agents/ folder; agents/ must contain only agent specifications", 1)
        return result

    try:
        content = resolved_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as err:
        result.add("input.target", f"Cannot read file: {err}")
        return result

    result.content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    lines = content.splitlines()
    result.metrics["line_count"] = len(lines)

    # Check for text stand-in
    if len(lines) == 1 and ("../skills/" in content or content.strip().endswith(".md")):
        result.add("packaging.wrapper", "Raw text stand-in pointer found; must be a full agent specification", 1)
        return result

    # Check for wrapper stubs
    if re.search(r"please run the `?[a-z0-9-]+`? skill immediately", content, re.I):
        result.add("packaging.wrapper", "Pointer-wrapper stub merely delegating to a skill is forbidden", 1)

    fm = parse_frontmatter(content)
    if fm is None:
        result.add("metadata.frontmatter", "Missing or malformed YAML frontmatter", 1)
        return result

    end_fm_idx = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), len(lines))
    body = "\n".join(lines[end_fm_idx + 1:])
    result.metrics["frontmatter_lines"] = end_fm_idx + 1
    result.metrics["body_lines"] = len(lines) - (end_fm_idx + 1)

    # Check name
    fm_name = str(fm.get("name", "")).strip()
    valid_name_stems = {name, name.replace("-agent", ""), f"{name}-agent"}
    if not fm_name or not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$", fm_name):
        result.add("metadata.name", f"Frontmatter name '{fm_name}' must be alphanumeric and hyphens (3–50 chars)", 2)
    elif fm_name not in valid_name_stems:
        result.add("metadata.name", f"Frontmatter name '{fm_name}' does not match filename '{name}'", 2)
    elif fm_name in GENERIC_NAMES:
        result.add("metadata.name", f"Frontmatter name '{fm_name}' is too generic", 2)

    # Check description
    desc = str(fm.get("description", "")).strip()
    result.metrics["description_len"] = len(desc)
    if not desc or len(desc) < 10:
        result.add("metadata.description", "Description is missing or too short (minimum 10 characters)")
    elif len(desc) > 5000:
        result.add("metadata.description", "Description is overly long (exceeds 5000 characters)")
    elif re.search(r"<[^>]+>", desc) and not re.search(r"<example>", desc):
        result.add("metadata.description", "Description contains prohibited XML tags (only <example> allowed)")

    example_count = desc.count("<example>")
    result.metrics["example_count"] = example_count
    if example_count < 2 or example_count > 4:
        result.add("metadata.examples", f"Description should include 2–4 <example> trigger blocks (found {example_count})")

    # Check model
    model = str(fm.get("model", "")).strip()
    if not model:
        result.add("metadata.model", "Missing required frontmatter field: model")
    elif model not in VALID_MODELS:
        result.add("metadata.model", f"Unknown model '{model}' (must be one of: {sorted(VALID_MODELS)})")

    # Check color
    color = str(fm.get("color", "")).strip()
    if not color:
        result.add("metadata.color", "Missing required frontmatter field: color")
    elif color not in VALID_COLORS:
        result.add("metadata.color", f"Unknown color '{color}' (must be one of: {sorted(VALID_COLORS)})")

    # Check system prompt
    sp = body.strip()
    result.metrics["system_prompt_len"] = len(sp)
    if not sp or len(sp) < 20:
        result.add("prompt.structure", "System prompt is missing or too short (minimum 20 characters)")
    else:
        if not re.search(r"\b(?:You are|You will|Your role)\b", sp):
            result.add("prompt.address", "System prompt should use second person (You are..., You will...)")
        if not re.search(r"\b(?:responsibilities|process|steps|workflow|rules|dimensions)\b", sp, re.I):
            result.add("prompt.structure", "System prompt should define clear responsibilities or process steps")

    # Check packaging location
    if path.parent.name != "agents":
        result.add("packaging.location", f"Agent file located in '{path.parent.name}', should be in an 'agents/' folder")

    return result


def discover_agents(target: Path) -> List[Path]:
    if target.is_file() and target.suffix == ".md":
        return [target]
    agents = []
    if (target / "agents").is_dir():
        agents.extend(sorted((target / "agents").glob("*.md")))
    elif target.name == "agents":
        agents.extend(sorted(target.glob("*.md")))
    else:
        agents.extend(sorted(target.glob("*/agents/*.md")))
        agents.extend(sorted(target.glob("plugins/*/agents/*.md")))
        agents.extend(sorted(target.glob(".claude/agents/*.md")))
        agents.extend(sorted(target.glob(".agents/agents/*.md")))
    return [a for a in sorted(set(agents)) if a.name.lower() != "readme.md"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=".", help="Path to agent markdown file or repository root")
    parser.add_argument("--all", action="store_true", help="Discover and scan all agents in target tree")
    parser.add_argument("--json", action="store_true", help="Output results in JSON envelope")
    parser.add_argument("--strict", action="store_true", help="Fail if any warnings are detected")
    args = parser.parse_args()

    raw_target = Path(args.target)
    if args.all or raw_target.is_dir():
        target_path = raw_target.resolve()
        agent_paths = discover_agents(target_path)
        if not agent_paths:
            parser.exit(2, f"No agent markdown files found in {target_path}\n")
    else:
        if not raw_target.exists():
            parser.exit(2, f"Target agent file not found: {raw_target}\n")
        agent_paths = [raw_target]

    results = []
    for p in agent_paths:
        res = audit_agent(p)
        results.append(res.to_dict())

    total = len(results)
    failed = [r for r in results if not r["passed"] or (args.strict and r["warnings"])]
    findings = [f for r in results for f in r["findings"]]

    envelope = {
        "schema_version": 2,
        "summary": {
            "total_agents": total,
            "passed_count": total - len(failed),
            "failed_count": len(failed),
            "by_rule": dict(Counter(f["rule_id"] for f in findings)),
            "by_severity": dict(Counter(f["severity"] for f in findings)),
        },
        "agents": results if len(results) > 1 else results[0]
    }

    if args.json:
        print(json.dumps(envelope if (args.all or len(results) > 1) else results[0], indent=2))
    else:
        print("=" * 70)
        print("SUB-AGENT STRUCTURAL & SPECIFICATION AUDIT REPORT")
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
