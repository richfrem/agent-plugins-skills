#!/usr/bin/env python3
"""Read-only structural audit for source and installed agent skills.

Purpose:
    Report metadata, navigation, evaluation and packaging findings without mutation.
Key Input Dependencies:
    ../references/skill-authoring-contract.json; the supplied skill or repository tree.
Usage:
    python3 scripts/audit_skill.py <skill> --mode source --json
    python3 scripts/audit_skill.py <repository> --all --json
"""
import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote, urlsplit

CONTRACT_PATH = Path(__file__).absolute().parent.parent / "references/skill-authoring-contract.json"


def load_contract() -> dict:
    """Load the bundled contract without resolving a source spoke into its hub."""
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("report_schema_version") != 2 or not contract.get("rules"):
        raise ValueError("Unsupported or empty skill authoring contract")
    return contract


@dataclass
class SkillAuditResult:
    """Observed facts and evidence; migration decisions belong to task tracking."""
    skill_name: str
    skill_dir: Path
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    findings: list = field(default_factory=list)
    mode: str = "source"
    profile: str = "repository"
    contract: dict = field(default_factory=load_contract)
    content_hash: str = ""
    aliases: list = field(default_factory=list)

    def add(self, rule: str, message: str, path: Path, line: int | None = None) -> None:
        """Apply contract-owned severity and append exact evidence."""
        definition = self.contract["rules"][rule]
        finding = {"rule_id": rule, **definition, "path": str(path), "line": line, "message": message}
        self.findings.append(finding)
        if definition["severity"] == "error":
            self.errors.append(message)
            self.passed = False
        else:
            self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize a versioned result while retaining legacy fields."""
        return {"schema_version": 2, "contract_version": self.contract["version"],
                "skill_name": self.skill_name, "skill_dir": str(self.skill_dir),
                "canonical_path": str(self.skill_dir), "plugin": self.skill_dir.parent.parent.name
                if self.skill_dir.parent.name == "skills" else None,
                "representation": self.mode, "profile": self.profile, "aliases": self.aliases,
                "content_hash": self.content_hash, "passed": self.passed,
                "errors": self.errors, "warnings": self.warnings, "findings": self.findings,
                "fixes_applied": self.fixes_applied, "metrics": self.metrics,
                "ai_review": {"status": "not_requested"}}


def parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Parse scalar frontmatter used by skills, including folded and quoted strings.

    Preserve unknown fields; nested YAML is not interpreted as a required scalar.
    """
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
            value = ("\n" if clean_val.startswith("|") else " ").join(p for p in parts if p).strip()
        elif value.startswith('"'):
            try:
                value = json.JSONDecoder().raw_decode(value)[0]
            except ValueError:
                value = value.strip('"')
        elif value.startswith("'"):
            value = value[1:value.rfind("'")].replace("''", "'")
        else:
            value = clean_val
        data[key] = value
        i += 1
    return data



def prose_lines(content: str) -> list:
    """Return numbered Markdown lines excluding fenced examples and frontmatter."""
    result = []
    fence = None
    frontmatter = content.startswith("---\n")
    for number, line in enumerate(content.splitlines(), 1):
        if frontmatter:
            if number > 1 and line.strip() == "---":
                frontmatter = False
            continue
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            result.append((number, line))
    return result


def heading_anchors(content: str) -> set:
    """Build GitHub-style Unicode heading slugs with duplicate suffixes."""
    seen = Counter()
    anchors = set()
    for _, line in prose_lines(content):
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)(?:\s+#+)?$", line)
        if match:
            title = re.sub(r"<[^>]*>", "", match.group(1)).lower()
            slug = "".join(c for c in title if not unicodedata.category(c).startswith(("P", "S")) or c in "-_")
            slug = slug.replace(" ", "-")
            suffix = f"-{seen[slug]}" if seen[slug] else ""
            anchors.add(slug + suffix)
            seen[slug] += 1
    return anchors


def links_in(content: str) -> list:
    """Extract inline local links and backtick resource routes from prose."""
    links = []
    for number, line in prose_lines(content):
        for match in re.finditer(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", line):
            links.append((number, match.group(1).strip("<>"), "markdown"))
        for match in re.finditer(r"`((?:references|assets)/[^`\s<>]+)`", line):
            links.append((number, match.group(1), "skill-root"))
    return list(dict.fromkeys(links))


def has_contents(content: str, preview: int) -> bool:
    """Require an early contents heading with at least one real navigation link."""
    early = [(n, line) for n, line in prose_lines(content) if n <= preview]
    return any(re.match(r"^#{1,6}\s+(?:table of )?(?:contents|navigation)\b", line, re.I) for _, line in early) and any(
        re.search(r"\[[^\]]+\]\([^)]+\)", line) for _, line in early)


def check_document(res: SkillAuditResult, path: Path, content: str) -> set:
    """Verify direct link targets and anchors without recursively crawling docs."""
    targets = set()
    root = res.skill_dir
    for number, text in prose_lines(content):
        if re.search(r"\[[^\]]+\]\[[^\]]*\]", text):
            res.add("links.unsupported", "Reference-style Markdown link requires manual resolution", path, number)
    for line, link, kind in links_in(content):
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc or link.startswith("mailto:"):
            continue
        if any(token in link for token in ("<", "{", "*")):
            continue
        base = root if kind == "skill-root" else path.parent
        target = base / unquote(parsed.path) if parsed.path else path
        if not (target.is_file() or target.is_dir()):
            res.add("links.resolve", f"Missing local link: {link}", path, line)
            continue

        if res.mode == "installed" and not target.resolve().is_relative_to(root.resolve()):
            res.add("packaging.resource", f"Installed link escapes the skill: {link}", path, line)
        if parsed.fragment and target.suffix.lower() == ".md":
            if unquote(parsed.fragment) not in heading_anchors(target.read_text(encoding="utf-8")):
                res.add("links.resolve", f"Missing heading anchor: {link}", path, line)
        if parsed.path and target.suffix.lower() == ".md":
            targets.add(target.absolute())
    return targets


def check_evals(res: SkillAuditResult) -> None:
    """Validate routing and task-success contracts separately, without inference."""
    for filename, rule in (("evals.json", "evals.routing"), ("task-success.json", "evals.task-success")):
        path = res.skill_dir / "evals" / filename
        if not path.exists():
            if filename == "evals.json":
                res.add("evals.missing", "Missing evals/evals.json - routing verification evals are recommended", path)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            entries = data if isinstance(data, list) else None
            if entries is None:
                res.add(rule, f"{filename} must be a root JSON array with {'should_trigger booleans' if rule == 'evals.routing' else 'expected_behavior cases'}", path)
                continue
            if rule == "evals.routing":
                res.metrics["eval_count"] = len(entries)
            for index, entry in enumerate(entries):
                valid = isinstance(entry, dict)
                if rule == "evals.routing":
                    valid = valid and type(entry.get("should_trigger")) is bool
                else:
                    valid = valid and isinstance(entry.get("expected_behavior"), list) and bool(entry["expected_behavior"]) and all(isinstance(x, str) and x.strip() for x in entry["expected_behavior"])
                if not valid:
                    res.add(rule, f"{filename} entry #{index} requires {'should_trigger: bool' if rule == 'evals.routing' else 'a nonempty expected_behavior string list'}", path)
        except (OSError, ValueError) as error:
            res.add(rule, f"{filename} is malformed: {error}", path)

def check_canonical_headings(res: SkillAuditResult, path: Path, content: str) -> None:
    """Validate presence of canonical template sections and absence of legacy sections."""
    lines_with_numbers = prose_lines(content)
    h2_headings = []
    for line_no, line in lines_with_numbers:
        m = re.match(r"^\s{0,3}##\s+(.+?)(?:\s+#+)?$", line)
        if m:
            h2_headings.append((line_no, m.group(1).strip()))

    h2_titles_lower = [h[1].lower() for h in h2_headings]

    # Check 1: ## Contents with local anchor links
    has_contents_heading = any(re.match(r"^(?:table of )?(?:contents|navigation)\b", t) for t in h2_titles_lower)
    has_anchor_links = any(re.search(r"\[[^\]]+\]\((#[^)]+)\)", line) for _, line in lines_with_numbers)
    if not (has_contents_heading and has_anchor_links):
        res.add("navigation.canonical-headings", "Missing canonical ## Contents section with local navigation links", path)

    # Check 2: ## Constraints or ## Critical Constraints
    has_constraints = any(re.match(r"^(?:critical\s+)?constraints\b", t) for t in h2_titles_lower)
    if not has_constraints:
        res.add("navigation.canonical-headings", "Missing canonical ## Constraints or ## Critical Constraints section", path)

    # Check 3: ## Quick start
    has_quick_start = any(re.match(r"^quick\s*start\b", t) for t in h2_titles_lower)
    if not has_quick_start:
        res.add("navigation.canonical-headings", "Missing canonical ## Quick start section", path)

    # Check 4: ## Workflow
    has_workflow = any(re.match(r"^workflow\b", t) for t in h2_titles_lower)
    if not has_workflow:
        res.add("navigation.canonical-headings", "Missing canonical ## Workflow section", path)

    # Check 5: ## Verification
    has_verification = any(re.match(r"^verification\b", t) for t in h2_titles_lower)
    if not has_verification:
        res.add("navigation.canonical-headings", "Missing canonical ## Verification section", path)

    # Check 6: References if skill directory has references/ with .md files
    refs_dir = res.skill_dir / "references"
    if refs_dir.is_dir() and any(f.suffix == ".md" for f in refs_dir.iterdir()):
        has_references_heading = any(re.match(r"^references\b", t) for t in h2_titles_lower)
        has_ref_links = any("references/" in link for _, link, _ in links_in(content))
        if not (has_references_heading or has_ref_links):
            res.add("navigation.canonical-headings", "Skill has references/ directory but no references are linked in SKILL.md", path)

    # Check 7: Legacy sections
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
                res.add("navigation.legacy-headings", f"Found legacy section '{legacy_name}'; refactor into canonical template sections", path, line_no)


def audit_skill(skill_path: Path | str, plugin_root: Optional[Path | str] = None,
                fix: bool = False, mode: str = "source", profile: str = "repository") -> SkillAuditResult:
    """Audit one skill with explicit representation; never modify its files."""
    skill = Path(skill_path).absolute()
    res = SkillAuditResult(skill.name, skill, mode=mode, profile=profile)
    path = skill / "SKILL.md"
    if fix:
        res.add("repair.disabled", "Automatic fixes are disabled; propose reviewed edits without inferring eval outcomes", path)
        return res
    if not path.is_file():
        res.add("input.target", f"Missing required SKILL.md in {skill}", path)
        return res
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        res.add("input.target", f"Cannot read SKILL.md: {error}", path)
        return res
    res.content_hash = hashlib.sha256(content.encode()).hexdigest()
    limits = res.contract["thresholds"]
    lines = content.splitlines()
    fm = parse_frontmatter(content)
    end = next((i + 1 for i in range(1, len(lines)) if lines[i].strip() == "---"), 0) if fm is not None else 0
    res.metrics.update(line_count=len(lines), frontmatter_lines=end, body_lines=len(lines) - end)
    if len(lines) > limits["lean_lines"]:
        res.add("size.lean", f"SKILL.md ({len(lines)} lines) exceeds progressive disclosure budget (target <= {limits['lean_lines']} lines)." + (" It exceeds 100 lines." if len(lines) > limits["preview_lines"] else ""), path)
    if len(lines) - end >= limits["body_lines"]:
        res.add("size.body", "SKILL.md body should be under 500 lines; split by topic", path)
    if len(lines) > limits["preview_lines"] and not has_contents(content, limits["preview_lines"]):
        res.add("navigation.entry-toc", "Long entry point needs useful contents in its first 100 lines", path)
    if fm is None:
        res.add("metadata.required", "Missing valid YAML frontmatter", path, 1)
    else:
        name, description = fm.get("name", ""), fm.get("description", "")
        if not re.fullmatch(r"[a-z0-9-]{1,64}", str(name)) or name != skill.name:
            res.add("metadata.name", f"Frontmatter name '{name}' must match directory and contain 1–64 lowercase slug characters", path, 2)
        if not isinstance(description, str) or not description.strip() or len(description) > limits["description_chars"] or re.search(r"<[^>]+>", description):
            res.add("metadata.description", "Description must be nonempty, <=1024 characters and contain no XML tags", path)
        res.metrics["description_len"] = len(str(description))
        if re.match(r"^(I\b|My\b|You\b)", str(description), re.I):
            res.add("metadata.voice", "Description should explain what the skill does and when to use it in third person", path)
        if profile == "anthropic" and any(word in str(name) for word in ("anthropic", "claude")):
            res.add("metadata.reserved", "Anthropic reserves claude/anthropic in skill names; preserve repository identity", path)
    check_evals(res)
    check_canonical_headings(res, path, content)
    direct = check_document(res, path, content)
    for reference in sorted(direct):
        if reference == path or reference.suffix != ".md":
            continue
        text = reference.read_text(encoding="utf-8")
        if len(text.splitlines()) > limits["preview_lines"] and not has_contents(text, limits["preview_lines"]):
            res.add("navigation.reference-toc", "Reference over 100 lines needs early contents", reference)
        nested = check_document(res, reference, text)
        for target in nested - direct - {path}:
            if target.is_relative_to(skill) and target.suffix == ".md":
                res.add("navigation.direct-reference", f"Required reference route is nested; link directly from SKILL.md: {target.relative_to(skill)}", reference)
    for category in res.contract["resources"]:
        folder = skill / category
        if not folder.is_dir():
            continue
        for resource in folder.rglob("*"):
            if any(part in ("__pycache__", ".git") for part in resource.parts) or resource.name.startswith("."):
                continue
            if resource.is_symlink() and resource.is_dir():
                res.add("packaging.resource", "Directory resource symlinks are forbidden", resource)
            elif resource.is_symlink() and not resource.exists():
                res.add("packaging.pending-link", "Broken or pending managed resource link", resource)
            elif resource.is_file():
                if mode == "source" and not resource.is_symlink():
                    res.add("packaging.resource", f"Source resource '{resource.name}' is a real file, not a symlink to plugin-root ownership", resource)
                elif mode == "installed" and resource.is_symlink():
                    res.add("packaging.resource", "Installed resources must be materialized hard copies", resource)
    # Folder structure template checks
    allowed_dirs = {"evals", "scripts", "references", "assets", "examples", "templates", "tests", "agents", ".history"}
    for item in skill.iterdir():
        if item.name.startswith("."):
            continue
        if item.is_dir() and item.name not in allowed_dirs:
            res.add("packaging.folder-structure", f"Disallowed directory in skill: '{item.name}/'; only {sorted(allowed_dirs)} allowed", item)

    evals_dir = skill / "evals"
    if not evals_dir.is_dir():
        res.add("packaging.folder-structure", "Missing required evals/ directory in skill structure", evals_dir)

    for bad in ("wiki", "traces", ".agent", "raw"):
        if (skill / bad).exists():
            res.add("packaging.hygiene", f"Spoke hygiene violation: {bad}", skill / bad)
    return res


def load_installed_ownership(root: Path) -> Dict[Path, Path]:
    """Map installed artifact paths to canonical skill paths using .agents/ownership."""
    ownership = {}
    ownership_dir = root / ".agents/ownership"
    if not ownership_dir.is_dir():
        return ownership
    for p in ownership_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            plugin = data.get("plugin")
            if not plugin:
                continue
            skills = data.get("components", {}).get("skills", {})
            for skill_name, info in skills.items():
                canonical = (root / "plugins" / plugin / "skills" / skill_name).absolute()
                for art in info.get("artifacts", []):
                    ownership[(root / art).resolve()] = canonical
                    ownership[(root / art).absolute()] = canonical
        except (OSError, ValueError):
            continue
    return ownership


def discover(root: Path) -> tuple:
    """Classify canonical locations and noncanonical entry points explicitly."""
    canonical = sorted(set(root.glob("plugins/*/skills/*/SKILL.md")) | set(root.glob("skills/*/SKILL.md")))
    canonical_dirs = {p.parent.absolute() for p in canonical}
    aliases, noncanonical = {}, []
    resolved = {p.parent.resolve(): p.parent.absolute() for p in canonical}
    ownership = load_installed_ownership(root)
    for path in sorted(root.rglob("SKILL.md")):
        if any(part in (".git", ".worktrees", "node_modules", ".venv", "temp", "tmp", ".tmp") for part in path.relative_to(root).parts):
            continue
        directory = path.parent.absolute()
        if directory in canonical_dirs:
            continue
        parts = path.relative_to(root).parts
        classification = "fixture" if "fixtures" in parts or "tests" in parts else "archive" if any(x in parts for x in (".history", "archive", "archives")) else "installed" if any(x in parts for x in (".agents", ".claude", ".codex", ".gemini")) else "external_or_generated"
        owner = resolved.get(directory.resolve())
        ambiguous = None
        if not owner and classification == "installed":
            owner = ownership.get(directory.resolve()) or ownership.get(directory)
            if not owner:
                matching = [c for c in canonical_dirs if c.name == directory.name]
                if len(matching) == 1:
                    owner = matching[0]
                elif len(matching) > 1:
                    ambiguous = [str(c) for c in matching]
        item = {"path": str(directory), "classification": classification, "canonical_path": str(owner) if owner else None}
        if ambiguous:
            item["ambiguous_candidates"] = ambiguous
        if owner:
            canonical_skill_md = owner / "SKILL.md"
            installed_skill_md = directory / "SKILL.md"
            if canonical_skill_md.is_file() and installed_skill_md.is_file():
                try:
                    item["hash_match"] = (hashlib.sha256(canonical_skill_md.read_bytes()).hexdigest() ==
                                          hashlib.sha256(installed_skill_md.read_bytes()).hexdigest())
                except OSError:
                    item["hash_match"] = False
            aliases.setdefault(owner, []).append(str(directory))
        noncanonical.append(item)
    return [p.parent.absolute() for p in canonical], noncanonical, aliases



def main() -> int:
    """Execute an explicit single-skill or repository scan with versioned reports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_path", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--plugin-root")
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--legacy-json", action="store_true", help="Repository list compatibility")
    parser.add_argument("--mode", choices=("source", "installed"), default="source")
    parser.add_argument("--profile", choices=("repository", "anthropic"), default="repository")
    parser.add_argument("--strict", action="store_true", help="Fail if any warnings are detected")
    args = parser.parse_args()
    if args.fix:
        parser.error("--fix is disabled for read-only rollout; no automatic inference or mutations")
    if not args.skill_path:
        parser.error("Explicit skill or repository path is required")
    root = Path(args.skill_path).absolute()
    try:
        if args.all:
            skills, noncanonical, aliases = discover(root)
            if not skills:
                parser.error("No canonical skills found; inventory is incomplete")
        else:
            if not (root / "SKILL.md").is_file():
                parser.error("Invalid skill target; repository mode requires --all")
            skills, noncanonical, aliases = [root], [], {}
        results = []
        failures = []
        for skill in skills:
            try:
                result = audit_skill(skill, args.plugin_root, mode=args.mode, profile=args.profile)
                result.aliases = aliases.get(skill, [])
                results.append(result.to_dict())
            except (OSError, ValueError, UnicodeError) as error:
                failures.append({"path": str(skill), "error": str(error)})
        findings = [f for result in results for f in result["findings"]]
        envelope = {"schema_version": 2, "contract_version": load_contract()["version"], "skills": results,
                    "noncanonical": noncanonical, "scan_failures": failures,
                    "summary": {"skills": len(results), "failed": sum(not r["passed"] for r in results),
                                "by_rule": dict(Counter(f["rule_id"] for f in findings)),
                                "by_severity": dict(Counter(f["severity"] for f in findings)),
                                "by_plugin": dict(Counter(str(r["plugin"]) for r in results))}}
        if args.json or args.legacy_json:
            print(json.dumps(results if args.legacy_json else envelope if args.all or failures else results[0], indent=2))
        else:
            for result in results:
                print(f"{'PASS' if result['passed'] else 'FAIL'} {result['canonical_path']}")
                for finding in result["findings"]:
                    print(f"  {finding['severity']} {finding['rule_id']}: {finding['message']}")
            for failure in failures:
                print(f"SCAN FAILURE {failure}")
        return 2 if failures else 1 if any(not r["passed"] or (args.strict and r["warnings"]) for r in results) else 0
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"Audit input/contract failure: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
