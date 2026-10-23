#!/usr/bin/env python3
"""
decouple_agent_paths.py (CLI)
=====================================

Purpose:
    Rewrites hardcoded install-folder references (`.agents/skills/...`) in markdown
    instructions to the install-location-independent form required by the APM migration
    plan (docs/plans/apm_migration_plan.md, Section 6.2). Dry-run by default.

    Automatic rewrites (only where the result is unambiguous):
      R1  A skill's own script:    `.agents/skills/<self>/scripts/x.py` -> `scripts/x.py`
      R2  A skill's own file:      `.agents/skills/<self>/<path>`       -> `<path>`
      R3  Another skill's SKILL.md: `[t](.agents/skills/<n>/SKILL.md)`  -> `t (the `<n>` skill)`
                                    bare `.agents/skills/<n>/SKILL.md`  -> `the `<n>` skill`
    Everything else that mentions `.agents/` is reported for manual review with a reason
    (cross-skill script or file paths, folder-only mentions, Python code, ownership files).

Usage:
    python3 decouple_agent_paths.py --path <repo-root>              # dry-run report
    python3 decouple_agent_paths.py --path <repo-root> --apply      # write R1-R3 rewrites
    python3 decouple_agent_paths.py --path <repo-root> --json out.json

Exit codes: 0 success, 2 usage error.

Key Input Dependencies:
    - git (files are taken from `git ls-files` under --path)
    - Default exclusions: plugins/plugin-manager/ (the legacy installer, retired later),
      *ignore files, tests/, docs/plans/, .agent/rules/ (synced copies of plugin rules),
      history/ledger files (map-debt.md, evolution-log.md, CHANGELOG.md, backlog.md), research/

Function Index:
    - tracked_files(root) -> list[Path]
    - is_excluded(rel) -> bool
    - owning_skill(rel) -> str | None
    - rewrite_text(text, own_skill) -> tuple[str, list[dict]]
    - review_items(text, rel) -> list[dict]
    - scan(root, apply) -> dict
    - main() -> None
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

EXCLUDED_PREFIXES = ("plugins/plugin-manager/", "docs/plans/", ".agent/rules/")
EXCLUDED_PARTS = ("/tests/", "/test/", "/research/", "/design-artifacts/")
# History and ledger files record what was true at the time; never rewrite them.
EXCLUDED_NAMES = ("map-debt.md", "evolution-log.md", "CHANGELOG.md", "backlog.md")
FENCE = re.compile(r"(```.*?```)", re.DOTALL)
INLINE_CODE = re.compile(r"(`[^`\n]+`)")
SKILL_REF = r"\.agents/skills/([\w-]+)/"
LINK_TO_SKILL = re.compile(r"\[([^\]]+)\]\(\.agents/skills/([\w-]+)/SKILL\.md\)")
BARE_SKILL_MD = re.compile(r"(?<![\w./-])\.agents/skills/([\w-]+)/SKILL\.md")
WHOLE_SPAN_SKILL_MD = re.compile(r"`\.agents/skills/([\w-]+)/SKILL\.md`")
OWN_PATH = r"\.agents/skills/{skill}/((?:[\w.-]+/)*[\w.-]+)"
ANY_AGENTS = re.compile(r"\.agents/[\w./-]*")


# List tracked files under the root (git keeps generated and ignored files out).
def tracked_files(root: Path) -> list[Path]:
    """Return tracked file paths relative to root."""
    out = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True)
    return [Path(p) for p in out.stdout.splitlines()]


# Files that legitimately talk about the install folder, or are derived copies.
def is_excluded(rel: str) -> bool:
    """True for the legacy installer, ignore files, tests, plans and synced rule copies."""
    name = rel.rsplit("/", 1)[-1]
    if name.endswith("ignore") or name in EXCLUDED_NAMES or rel.startswith(EXCLUDED_PREFIXES):
        return True
    return any(part in "/" + rel for part in EXCLUDED_PARTS)


# The skill a file belongs to (plugins/<p>/skills/<skill>/...), if any.
def owning_skill(rel: str) -> str | None:
    """Return the skill folder name for a path inside plugins/*/skills/*/, else None."""
    parts = rel.split("/")
    if len(parts) > 4 and parts[0] == "plugins" and parts[2] == "skills":
        return parts[3]
    return None


# Apply R1-R3 to one markdown text; return the new text and the changes made.
# Only prose is rewritten: fenced code is skipped, and an inline code span is rewritten only
# when it is exactly a path (paths inside commands, JSON or tables of external repos stay).
def rewrite_text(text: str, own_skill: str | None) -> tuple[str, list[dict]]:
    """Rewrite unambiguous install-folder references; leave everything else untouched."""
    changes: list[dict] = []

    def record(rule: str, old: str, new: str) -> str:
        changes.append({"rule": rule, "old": old, "new": new})
        return new

    own = re.compile(OWN_PATH.format(skill=re.escape(own_skill))) if own_skill else None

    def own_sub(segment: str, whole_span: bool) -> str:
        def repl(m: re.Match) -> str:
            rule = "R1" if m.group(1).startswith("scripts/") else "R2"
            return record(rule, m.group(0), m.group(1))
        if not own:
            return segment
        if whole_span:
            inner = segment[1:-1]
            return f"`{own.sub(repl, inner)}`" if own.fullmatch(inner) else segment
        return own.sub(repl, segment)

    def prose(segment: str) -> str:
        parts = INLINE_CODE.split(segment)
        for i, part in enumerate(parts):
            if part.startswith("`") and part.endswith("`") and len(part) > 1:
                if WHOLE_SPAN_SKILL_MD.fullmatch(part):
                    name = WHOLE_SPAN_SKILL_MD.fullmatch(part).group(1)
                    parts[i] = record("R3", part, f"the `{name}` skill")
                else:
                    parts[i] = own_sub(part, whole_span=True)
                continue
            part = own_sub(part, whole_span=False)
            part = LINK_TO_SKILL.sub(lambda m: record("R3", m.group(0), f"{m.group(1)} (the `{m.group(2)}` skill)"), part)
            parts[i] = BARE_SKILL_MD.sub(lambda m: record("R3", m.group(0), f"the `{m.group(1)}` skill"), part)
        return "".join(parts)

    pieces = FENCE.split(text)
    return "".join(p if p.startswith("```") else prose(p) for p in pieces), changes


# Remaining `.agents/` mentions after rewriting, each with a review reason.
def review_items(text: str, rel: str) -> list[dict]:
    """Return manual-review items for install-folder mentions that were not rewritten."""
    items = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for match in ANY_AGENTS.finditer(line):
            ref = match.group(0)
            if re.match(SKILL_REF + r"scripts/", ref):
                reason = "another skill's script: delegate to that skill by name (ADR-001) or share via the copy manifest"
            elif re.match(SKILL_REF, ref):
                reason = "another skill's file: markdown link within the plugin, or the skill by name"
            elif ref.startswith(".agents/ownership"):
                reason = "plugin-manager ownership manifest: replace with APM (--skill selections) in Phase 4"
            else:
                reason = "install-folder mention: describe by harness-neutral wording (plan Section 6.2)"
            items.append({"file": rel, "line": line_no, "ref": ref, "reason": reason})
    return items


# Walk tracked files, rewrite markdown (optionally writing), collect review items.
def scan(root: Path, apply: bool) -> dict:
    """Return {changed_files, changes, review} for the repository at root."""
    changed, review = [], []
    for rel_path in tracked_files(root):
        rel = rel_path.as_posix()
        path = root / rel_path
        if is_excluded(rel) or path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if ".agents/" not in text:
            continue
        new_text, changes = (rewrite_text(text, owning_skill(rel)) if rel.endswith(".md") else (text, []))
        if changes:
            changed.append({"file": rel, "changes": changes})
            if apply:
                path.write_text(new_text, encoding="utf-8")
        review += review_items(new_text, rel)
    return {"applied": apply, "changed_files": changed, "review": review,
            "change_count": sum(len(c["changes"]) for c in changed)}


# CLI entry point.
def main() -> None:
    """Parse arguments, scan, print a summary and optionally write a JSON report."""
    parser = argparse.ArgumentParser(description="Decouple hardcoded .agents/ references (plan Section 6)")
    parser.add_argument("--path", default=".", help="Repository root (default: .)")
    parser.add_argument("--apply", action="store_true", help="Write R1-R3 rewrites (default: dry-run)")
    parser.add_argument("--json", help="Write the full report to this JSON file")
    args = parser.parse_args()
    result = scan(Path(args.path).resolve(), args.apply)
    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"{mode}: {result['change_count']} rewrites in {len(result['changed_files'])} files; "
          f"{len(result['review'])} mentions need manual review")
    for item in result["changed_files"]:
        for change in item["changes"]:
            print(f"  [{change['rule']}] {item['file']}: {change['old']} -> {change['new']}")
    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Report: {args.json}")
    sys.exit(0)


if __name__ == "__main__":
    main()
