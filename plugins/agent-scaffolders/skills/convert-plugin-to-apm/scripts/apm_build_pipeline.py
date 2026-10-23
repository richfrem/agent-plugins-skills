#!/usr/bin/env python3
"""
apm_build_pipeline.py (CLI)
=====================================

Purpose:
    Build-time APM packaging pipeline for one plugin (docs/plans/apm_migration_plan.md,
    Section 4). Runs five stages: inspect -> normalize -> validate -> package -> test deploy.
    All output goes to an isolated staging directory (default build/staging/<plugin>/);
    the authoring source tree is never modified.

    Symlinks are discovered from the git index (mode 120000) and their targets are read
    from the git blob, so a Windows checkout with core.symlinks=false (where each symlink
    is a short text stub) is dereferenced exactly like a real symlink.

    Symlink-free sharing: symlinks.json entries with strategy "copy" name one canonical
    source file and the skill paths that need a copy; the build creates those copies in
    staging only (plan Section 10.3), and --pack produces the bundle consumers install.

Usage:
    python3 apm_build_pipeline.py --plugin plugins/dev-utils
    python3 apm_build_pipeline.py --plugin plugins/dev-utils --skip-deploy
    python3 apm_build_pipeline.py --plugin plugins/dev-utils --pack
    python3 apm_build_pipeline.py --plugin plugins/dev-utils --apm /path/to/apm --targets copilot,claude

Outputs:
    <build-dir>/<plugin>/                 staged, symlink-free package with apm.yml
    <build-dir>/<plugin>.report.json      audit manifest + validation + deploy results
    <deploy-dir>/<plugin>/                throwaway fixture repo used by test deploy
    <dist-dir>/<plugin>-<version>.zip     installable bundle (--pack only)

Exit codes: 0 all stages passed, 1 validation or deploy errors, 2 usage error.

Key Input Dependencies:
    - git (repo must be a git work tree; symlinks are read from the index)
    - <plugin>/.claude-plugin/plugin.json or <plugin>/plugin.yaml (metadata; optional)
    - symlinks.json at the repo root (copy-manifest entries with strategy "copy"; optional)
    - APM CLI on PATH or via --apm (test deploy stage only; pinned in
      plugins/agent-scaffolders/requirements-dev.in)
    - PyYAML

Function Index:
    - git_symlink_entries(repo_root, plugin_rel) -> list[dict]
    - _still_a_link(path, link_text) -> bool
    - load_plugin_metadata(plugin_dir) -> dict
    - copy_manifest_entries(repo_root, plugin_rel) -> list[dict]
    - inspect_plugin(repo_root, plugin_dir) -> dict
    - _copy_ignore(directory, names) -> set[str]
    - _sha256(path) -> str
    - _materialize_link(staged_path, target_abs) -> None
    - normalize_plugin(inspection, staging_dir) -> dict
    - _materialize_copies(inspection, staging_dir) -> list[dict]
    - _finding(level, check, path, detail, suggestion) -> dict
    - _parse_frontmatter(text) -> dict
    - _check_skill_frontmatter(staged_dir) -> list[dict]
    - _iter_relative_links(text) -> list[str]
    - _check_unrewritten_paths(staged_dir) -> list[dict]
    - _check_relative_links(staged_dir) -> list[dict]
    - _check_plugin_config(staged_dir) -> list[dict]
    - _check_hook_scripts(staged_dir) -> list[dict]
    - _check_link_entries(normalized) -> list[dict]
    - _check_no_symlinks(staged_dir) -> list[dict]
    - validate_package(staged_dir, normalized) -> dict
    - package_plugin(staged_dir, inspection, targets) -> dict
    - _run_apm(apm_bin, args, cwd) -> dict
    - _deployed_skill_dirs(fixture, skill) -> list[Path]
    - _check_deployed_skills(fixture, staged_dir, skills) -> list[dict]
    - _links_resolve(md) -> bool
    - run_test_deploy(staged_dir, fixture, targets, apm_bin, skills) -> dict
    - pack_plugin(staged_dir, dist_dir, apm_bin) -> dict
    - run_pipeline(args) -> dict
    - main() -> None
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

SYMLINK_MODE = "120000"
DEFAULT_TARGETS = ["claude", "copilot", "agy", "codex"]
# CLI target names that a package apm.yml spells differently (APM 0.33.0).
MANIFEST_TARGET_NAMES = {"agents": "agent-skills", "agy": "antigravity"}
COPY_IGNORE = {"__pycache__", ".DS_Store"}
DEPLOYED_DIRS = ("skills", "agents", "commands")
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "#", "file://")


# ---------------------------------------------------------------------------
# Stage 1: Inspect
# ---------------------------------------------------------------------------

# Read every symlink under the plugin from the git index, with its link text.
def git_symlink_entries(repo_root: Path, plugin_rel: str) -> list[dict]:
    """Return [{path, link_text}] for each mode-120000 entry under plugin_rel.

    The link text comes from the git blob, not the filesystem, so the result is the
    same on a checkout where symlinks were materialized as plain text stubs.
    """
    listing = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-s", "--", plugin_rel],
        capture_output=True, text=True, check=True,
    ).stdout
    entries = []
    for line in listing.splitlines():
        meta, path = line.split("\t", 1)
        mode, sha, _stage = meta.split()
        if mode == SYMLINK_MODE:
            entries.append({"path": path, "sha": sha})
    if not entries:
        return []
    batch = "\n".join(e["sha"] for e in entries) + "\n"
    out = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "--batch"],
        input=batch.encode(), capture_output=True, check=True,
    ).stdout
    pos = 0
    for entry in entries:
        header_end = out.index(b"\n", pos)
        size = int(out[pos:header_end].split()[2])
        entry["link_text"] = out[header_end + 1:header_end + 1 + size].decode("utf-8")
        pos = header_end + 1 + size + 1
        del entry["sha"]
    return [e for e in entries if _still_a_link(repo_root / e["path"], e["link_text"])]


# An index symlink still counts only while the working tree holds the link itself (or, on
# a Windows checkout, its text stub); a path already replaced by real content is left alone.
def _still_a_link(path: Path, link_text: str) -> bool:
    """True if path is a symlink, or a regular file whose whole content is the link text."""
    if path.is_symlink():
        return True
    if not path.is_file() or path.stat().st_size > 4096:
        return False
    return path.read_text(encoding="utf-8", errors="replace").strip() == link_text.strip()


# Load plugin name/version/description/author from the plugin manifest.
def load_plugin_metadata(plugin_dir: Path) -> dict:
    """Read .claude-plugin/plugin.json, falling back to plugin.yaml, then the folder name."""
    data: dict = {}
    json_manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    yaml_manifest = plugin_dir / "plugin.yaml"
    if json_manifest.is_file():
        data = json.loads(json_manifest.read_text(encoding="utf-8"))
    elif yaml_manifest.is_file():
        data = yaml.safe_load(yaml_manifest.read_text(encoding="utf-8")) or {}
    author = data.get("author", "Unknown")
    if isinstance(author, dict):
        author = author.get("name", "Unknown")
    return {
        "name": data.get("name", plugin_dir.name),
        "version": str(data.get("version", "0.1.0")),
        "description": data.get("description", f"APM package for {plugin_dir.name}"),
        "author": author,
        "license": data.get("license", ""),
    }


# Read copy-manifest entries (symlinks.json, strategy "copy") whose destination is in the plugin.
def copy_manifest_entries(repo_root: Path, plugin_rel: str) -> list[dict]:
    """Return [{src, dst}] entries that the build must materialize as physical copies.

    This is the symlink-free form of hub-and-spoke sharing (plan Section 10.3): one
    canonical file in source, listed copies created only in staging.
    """
    manifest = repo_root / "symlinks.json"
    if not manifest.is_file():
        return []
    links = json.loads(manifest.read_text(encoding="utf-8")).get("links", [])
    prefix = plugin_rel.rstrip("/") + "/"
    return [{"src": e["src"], "dst": e["dst"]} for e in links
            if e.get("strategy") == "copy" and e.get("dst", "").startswith(prefix)]


# Stage 1: scan layout, manifest and symlinks without touching anything.
def inspect_plugin(repo_root: Path, plugin_dir: Path) -> dict:
    """Discover skills, agents, commands, hooks, rules and git symlinks for one plugin."""
    plugin_rel = plugin_dir.relative_to(repo_root).as_posix()
    skills_dir = plugin_dir / "skills"
    skills = sorted(p.parent.name for p in skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []

    def names(sub: str, pattern: str) -> list[str]:
        folder = plugin_dir / sub
        return sorted(p.name for p in folder.glob(pattern)) if folder.is_dir() else []

    return {
        "repo_root": str(repo_root),
        "plugin_dir": str(plugin_dir),
        "plugin_rel": plugin_rel,
        "metadata": load_plugin_metadata(plugin_dir),
        "skills": skills,
        "agents": names("agents", "*.md"),
        "commands": names("commands", "*.md"),
        "hooks": names("hooks", "*"),
        "rules": names("rules", "*.md"),
        "symlinks": git_symlink_entries(repo_root, plugin_rel),
        "copies": copy_manifest_entries(repo_root, plugin_rel),
    }


# ---------------------------------------------------------------------------
# Stage 2: Normalize
# ---------------------------------------------------------------------------

# shutil.copytree ignore callback: drop caches and OS noise from the staged copy.
def _copy_ignore(directory: str, names: list[str]) -> set[str]:
    """Return the names in directory that must not be staged."""
    return {n for n in names if n in COPY_IGNORE or n.endswith(".pyc")}


# Content hash used by the SHA-256 acceptance check (plan Section 2).
def _sha256(path: Path) -> str:
    """Return the hex SHA-256 of a file's bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Replace a staged link (or text stub) with a physical copy of its target.
def _materialize_link(staged_path: Path, target_abs: Path) -> None:
    """Remove whatever is at staged_path and copy the target file or directory there."""
    if staged_path.is_symlink() or staged_path.is_file():
        staged_path.unlink()
    elif staged_path.is_dir():
        shutil.rmtree(staged_path)
    if target_abs.is_dir():
        shutil.copytree(target_abs, staged_path, ignore=_copy_ignore)
    else:
        shutil.copy2(target_abs, staged_path)


# Stage 2: copy the plugin into staging and dereference every git symlink there.
def normalize_plugin(inspection: dict, staging_dir: Path) -> dict:
    """Stage the plugin and resolve each symlink against the source tree.

    Returns an audit manifest: one entry per symlink with its resolved target, whether
    the target stays inside the plugin, the staged SHA-256 and a status of
    'resolved' or 'broken'.
    """
    repo_root = Path(inspection["repo_root"])
    plugin_dir = Path(inspection["plugin_dir"])
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(plugin_dir, staging_dir, symlinks=True, ignore=_copy_ignore)

    manifest = []
    for link in inspection["symlinks"]:
        source_link = repo_root / link["path"]
        target_abs = Path(os.path.normpath(source_link.parent / link["link_text"]))
        rel_in_plugin = source_link.relative_to(plugin_dir)
        staged_path = staging_dir / rel_in_plugin
        entry = {
            "kind": "symlink",
            "path": rel_in_plugin.as_posix(),
            "link_text": link["link_text"],
            "target": os.path.relpath(target_abs, repo_root),
            "inside_plugin": target_abs.is_relative_to(plugin_dir),
        }
        if not target_abs.exists():
            # Unresolvable: drop the dangling link from staging; the audit manifest keeps it.
            if staged_path.is_symlink() or staged_path.is_file():
                staged_path.unlink()
            entry["status"] = "broken"
        else:
            _materialize_link(staged_path, target_abs)
            entry["status"] = "resolved"
            if target_abs.is_file():
                entry["target_sha256"] = _sha256(target_abs)
                entry["staged_sha256"] = _sha256(staged_path)
        manifest.append(entry)
    manifest += _materialize_copies(inspection, staging_dir)
    return {"staging_dir": str(staging_dir), "links": manifest}


# Create the physical copies listed in the copy manifest inside staging.
def _materialize_copies(inspection: dict, staging_dir: Path) -> list[dict]:
    """Copy each manifest src to its dst in staging; return audit entries like symlinks."""
    repo_root = Path(inspection["repo_root"])
    plugin_dir = Path(inspection["plugin_dir"])
    entries = []
    for item in inspection.get("copies", []):
        target_abs = (repo_root / item["src"]).resolve()
        rel_in_plugin = (repo_root / item["dst"]).relative_to(plugin_dir)
        staged_path = staging_dir / rel_in_plugin
        entry = {"kind": "copy", "path": rel_in_plugin.as_posix(), "link_text": item["src"],
                 "target": item["src"], "inside_plugin": target_abs.is_relative_to(plugin_dir.resolve())}
        if not target_abs.is_file():
            entry["status"] = "broken"
        else:
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            _materialize_link(staged_path, target_abs)
            entry.update(status="resolved", target_sha256=_sha256(target_abs),
                         staged_sha256=_sha256(staged_path))
        entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Stage 3: Validate
# ---------------------------------------------------------------------------

# Standard fix for every finding type (full text: references/apm-alignment-fixes.md).
# Each finding carries its fix id so the same misalignment is always fixed the same way.
STANDARD_FIXES = {
    "broken_symlink": "SF-1 delete the dummy symlink; cite the canonical file with a relative link",
    "cross_plugin_symlink": "SF-2 delete the symlink; reference the other plugin's skill by name (ADR-001)",
    "broken_relative_link": "SF-3 fix the markdown link so it resolves to a file inside the plugin",
    "link_escapes_package": "SF-3 link only to files inside the plugin; reference other plugins' skills by name",
    "path_not_rewritten": "SF-8 use a markdown link for documents; keep scripts a skill runs inside that skill",
    "symlink_in_package": "SF-4 re-run normalize; report if the link is not in the git index",
    "sha256_mismatch": "SF-4 re-run normalize; report if the link is not in the git index",
    "frontmatter_name": "SF-5 set frontmatter name to the skill folder name",
    "frontmatter_description": "SF-5 add a third-person description to the frontmatter",
    "skill_not_deployed": "SF-6 check the skill folder has SKILL.md with valid frontmatter",
    "deployed_content_mismatch": "SF-6 compare staged vs deployed file; report to APM if links do not resolve",
    "rules_not_deployed": "SF-9 none in the package: setup copies needed rules into .agent/rules/ (AGENTS.md lists them)",
    "lsp_config_invalid": "SF-10 use APM's flat lsp.json format ({name: {command, ...}}) or delete an empty file",
    "hook_script_harness_path": "SF-11 use Path(__file__) for own files and a harness-neutral state path (e.g. context/)",
    "agent_mirrors_skill": "SF-12 write the agent as its own short definition that uses the skill by name",
    "link_rewritten_by_apm": "none (expected: APM rewrites cross-skill links into apm_modules/)",
    "apm_install_failed": "SF-7 read the APM error; map target names (agents -> agent-skills in apm.yml)",
    "uninstall_left_files": "SF-6 compare lockfile deployed files against the fixture",
}


# Build one finding with its standard fix attached.
def _finding(level: str, check: str, path: str, detail: object, suggestion: str = "") -> dict:
    """Return a finding dict; suggestion is a concrete replacement when one can be computed."""
    finding = {"level": level, "check": check, "path": path, "detail": detail,
               "fix": STANDARD_FIXES.get(check, "")}
    if suggestion:
        finding["suggestion"] = suggestion
    return finding


# Minimal YAML frontmatter reader for SKILL.md files.
def _parse_frontmatter(text: str) -> dict:
    """Return the YAML frontmatter dict, or {} if the file has none or it is invalid."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


# Each staged skill must declare a name matching its folder and a description.
def _check_skill_frontmatter(staged_dir: Path) -> list[dict]:
    """Return findings for SKILL.md files with missing or mismatched frontmatter."""
    findings = []
    for skill_md in sorted(staged_dir.glob("skills/*/SKILL.md")):
        meta = _parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
        rel = skill_md.relative_to(staged_dir).as_posix()
        if meta.get("name") != skill_md.parent.name:
            findings.append(_finding("error", "frontmatter_name", rel,
                                     f"name={meta.get('name')!r}, folder={skill_md.parent.name!r}"))
        if not meta.get("description"):
            findings.append(_finding("error", "frontmatter_description", rel, "missing description"))
    return findings


# Extract relative markdown link targets, ignoring fenced and inline code.
def _iter_relative_links(text: str) -> list[str]:
    """Return link targets from [text](target) that are relative file paths."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    links = []
    for raw in re.findall(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", text):
        if raw.startswith(SKIP_LINK_PREFIXES) or raw.startswith("<"):
            continue
        target = raw.split("#", 1)[0]
        if target:
            links.append(target)
    return links


# Every relative markdown link in deployed content must resolve inside the plugin package.
# APM copies only the skill folder, but rewrites markdown links that leave it to point into
# its package cache (apm_modules/ or ~/.apm/apm_modules/), so links to sibling skills and
# plugin-root files work after install. Links that leave the plugin are not rewritten.
def _check_relative_links(staged_dir: Path) -> list[dict]:
    """Return findings for deployed-content links that are broken or leave the package."""
    findings = []
    root = staged_dir.resolve()
    for deploy_root in (staged_dir / d for d in DEPLOYED_DIRS):
        if not deploy_root.is_dir():
            continue
        for md in sorted(deploy_root.rglob("*.md")):
            if md.is_symlink() or not md.is_file():
                continue
            rel = md.relative_to(staged_dir).as_posix()
            for target in _iter_relative_links(md.read_text(encoding="utf-8", errors="replace")):
                resolved = (md.parent / target).resolve()
                if not resolved.is_relative_to(root):
                    findings.append(_finding("error", "link_escapes_package", rel, target))
                elif not resolved.exists():
                    findings.append(_finding("error", "broken_relative_link", rel, target))
    return findings


# Paths outside markdown links (inline code, code blocks, plain text) are not rewritten by
# APM, so any such path that climbs out of its skill folder breaks after install.
def _check_unrewritten_paths(staged_dir: Path) -> list[dict]:
    """Return warnings for ../ paths outside markdown links that leave their skill folder."""
    findings = []
    link_spans = re.compile(r"\]\([^)]*\)")
    path_token = re.compile(r"(?:\.\./)+[\w./-]+")
    for skill_dir in sorted(p for p in (staged_dir / "skills").glob("*") if p.is_dir()):
        root = skill_dir.resolve()
        for md in sorted(skill_dir.rglob("*.md")):
            if md.is_symlink() or not md.is_file():
                continue
            text = link_spans.sub("", md.read_text(encoding="utf-8", errors="replace"))
            for token in sorted(set(path_token.findall(text))):
                if not (md.parent / token).resolve().is_relative_to(root):
                    findings.append(_finding("warning", "path_not_rewritten",
                                             md.relative_to(staged_dir).as_posix(), token))
    return findings


# Plugin-level config that APM does not deploy or cannot read.
def _check_plugin_config(staged_dir: Path) -> list[dict]:
    """Return findings for rules/ folders and lsp.json files APM will not use."""
    findings = []
    if (staged_dir / "rules").is_dir():
        count = len(list((staged_dir / "rules").glob("*.md")))
        findings.append(_finding("info", "rules_not_deployed", "rules/", f"{count} rule files"))
    for name in ("lsp.json", ".lsp.json"):
        path = staged_dir / name
        if not path.is_file():
            continue
        try:
            servers = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            findings.append(_finding("warning", "lsp_config_invalid", name, f"invalid JSON: {exc}"))
            continue
        bad = [k for k, v in servers.items() if not (isinstance(v, dict) and v.get("command"))]
        if bad:
            findings.append(_finding("warning", "lsp_config_invalid", name, f"entries without command: {bad}"))
    return findings


# Hook scripts run under every target harness, so they must not hardcode one harness's folder.
def _check_hook_scripts(staged_dir: Path) -> list[dict]:
    """Return warnings for hook scripts (from hooks/hooks.json) that name .claude/ or .agents/."""
    hooks_json = staged_dir / "hooks" / "hooks.json"
    if not hooks_json.is_file():
        return []
    commands = re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+\.py)", hooks_json.read_text(encoding="utf-8"))
    findings = []
    for rel in sorted(set(commands)):
        script = staged_dir / rel
        if not script.is_file():
            continue
        hits = sorted(set(re.findall(r"\.(?:claude|agents)/[\w./-]*", script.read_text(encoding="utf-8", errors="replace"))))
        if hits:
            findings.append(_finding("warning", "hook_script_harness_path", rel, hits[:5]))
    return findings


# Symlink audit: broken targets, cross-plugin targets, and hash mismatches.
def _check_link_entries(normalized: dict) -> list[dict]:
    """Return findings from the normalize audit manifest."""
    findings = []
    for entry in normalized["links"]:
        if entry["status"] == "broken":
            findings.append(_finding("error", "broken_symlink", entry["path"],
                                     f"target {entry['target']} does not exist"))
            continue
        if entry["path"].startswith("agents/") and entry["target"].endswith("SKILL.md"):
            findings.append(_finding("warning", "agent_mirrors_skill", entry["path"],
                                     f"agent file is a copy of {entry['target']}; its skill-relative links break in agents/"))
        if not entry["inside_plugin"]:
            findings.append(_finding("error", "cross_plugin_symlink", entry["path"],
                                     f"target {entry['target']} is outside the plugin"))
        if "target_sha256" in entry and entry["target_sha256"] != entry["staged_sha256"]:
            findings.append(_finding("error", "sha256_mismatch", entry["path"],
                                     "staged file differs from its source target"))
    return findings


# The staged package must contain no symlinks at all.
def _check_no_symlinks(staged_dir: Path) -> list[dict]:
    """Return a finding for every symlink left in the staged tree."""
    findings = []
    for dirpath, dirnames, filenames in os.walk(staged_dir):
        for name in dirnames + filenames:
            path = Path(dirpath) / name
            if path.is_symlink():
                findings.append(_finding("error", "symlink_in_package",
                                         path.relative_to(staged_dir).as_posix(),
                                         f"-> {os.readlink(path)}"))
    return findings


# Stage 3: run every check and summarize.
def validate_package(staged_dir: Path, normalized: dict) -> dict:
    """Return {passed, error_count, warning_count, findings} for the staged package."""
    findings = (
        _check_link_entries(normalized)
        + _check_no_symlinks(staged_dir)
        + _check_skill_frontmatter(staged_dir)
        + _check_relative_links(staged_dir)
        + _check_unrewritten_paths(staged_dir)
        + _check_plugin_config(staged_dir)
        + _check_hook_scripts(staged_dir)
    )
    errors = sum(1 for f in findings if f["level"] == "error")
    return {
        "passed": errors == 0,
        "error_count": errors,
        "warning_count": sum(1 for f in findings if f["level"] == "warning"),
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Stage 4: Package
# ---------------------------------------------------------------------------

# Stage 4: write apm.yml into the staged package (never into the source plugin).
def package_plugin(staged_dir: Path, inspection: dict, targets: list[str]) -> dict:
    """Write <staged_dir>/apm.yml from the plugin metadata and requested targets."""
    meta = inspection["metadata"]
    manifest = {
        "name": meta["name"],
        "version": meta["version"],
        "description": meta["description"],
        "author": {"name": meta["author"]},
        "targets": [MANIFEST_TARGET_NAMES.get(t, t) for t in targets],
        # apm pack only produces an installable bundle when a dependencies block exists.
        "dependencies": {},
    }
    if meta.get("license"):
        manifest["license"] = meta["license"]
    apm_yml = staged_dir / "apm.yml"
    apm_yml.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return {"apm_yml": str(apm_yml), "manifest": manifest}


# ---------------------------------------------------------------------------
# Stage 5: Test Deploy
# ---------------------------------------------------------------------------

# Run one APM command and capture its result.
def _run_apm(apm_bin: str, args: list[str], cwd: Path) -> dict:
    """Run apm with args in cwd; return {cmd, exit_code, output_tail}."""
    env = dict(os.environ, NO_COLOR="1")
    proc = subprocess.run([apm_bin, *args], cwd=cwd, capture_output=True, text=True, env=env)
    output = (proc.stdout + proc.stderr).strip().splitlines()
    return {"cmd": " ".join(["apm", *args]), "exit_code": proc.returncode, "output_tail": output[-15:]}


# Project-scope locations where APM may deploy a skill.
def _deployed_skill_dirs(fixture: Path, skill: str) -> list[Path]:
    """Return existing deployed copies of one skill inside the fixture repo."""
    candidates = [fixture / ".agents" / "skills" / skill,
                  fixture / ".claude" / "skills" / skill,
                  fixture / ".github" / "skills" / skill]
    return [c for c in candidates if (c / "SKILL.md").is_file()]


# Every staged skill must deploy, and each deployed file must match the staged bytes.
def _check_deployed_skills(fixture: Path, staged_dir: Path, skills: list[str]) -> list[dict]:
    """Return findings for missing skills or deployed files that differ from staging."""
    findings = []
    for skill in skills:
        deployed = _deployed_skill_dirs(fixture, skill)
        if not deployed:
            findings.append(_finding("error", "skill_not_deployed", skill, ""))
            continue
        staged_skill = staged_dir / "skills" / skill
        for copy in deployed:
            for f in copy.rglob("*"):
                src = staged_skill / f.relative_to(copy)
                if not (f.is_file() and src.is_file()) or _sha256(f) == _sha256(src):
                    continue
                rel = f.relative_to(fixture).as_posix()
                if f.suffix == ".md" and _links_resolve(f):
                    findings.append(_finding("info", "link_rewritten_by_apm", rel,
                                             "APM rewrote cross-skill links into apm_modules/; all resolve"))
                else:
                    findings.append(_finding("error", "deployed_content_mismatch", rel, ""))
    return findings


# True when every relative markdown link in a deployed file resolves on disk.
def _links_resolve(md: Path) -> bool:
    """Check the relative links of one deployed markdown file."""
    text = md.read_text(encoding="utf-8", errors="replace")
    return all((md.parent / t).resolve().exists() for t in _iter_relative_links(text))


# Stage 5: dry-run, install, verify, then uninstall into a throwaway fixture repo.
def run_test_deploy(staged_dir: Path, fixture: Path, targets: list[str], apm_bin: str, skills: list[str]) -> dict:
    """Install the staged package into a fresh fixture repo and check the result."""
    if fixture.exists():
        shutil.rmtree(fixture)
    fixture.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=fixture, check=True)
    target_arg = ",".join(targets)
    steps = [_run_apm(apm_bin, ["install", str(staged_dir), "--target", target_arg, "--dry-run"], fixture),
             _run_apm(apm_bin, ["install", str(staged_dir), "--target", target_arg], fixture)]
    findings = [] if steps[-1]["exit_code"] == 0 else [
        _finding("error", "apm_install_failed", "", steps[-1]["output_tail"][-3:])]
    deployed_roots: list[str] = []
    if not findings:
        findings = _check_deployed_skills(fixture, staged_dir, skills)
        deployed_roots = sorted({p.relative_to(fixture).parts[0] for p in fixture.glob(".*/skills/*/SKILL.md")})
        steps.append(_run_apm(apm_bin, ["uninstall", f"_local/{staged_dir.name}"], fixture))
        leftovers = [s for s in skills if _deployed_skill_dirs(fixture, s)]
        if leftovers:
            findings.append(_finding("error", "uninstall_left_files", "", f"{len(leftovers)} skills still deployed"))
    return {"fixture": str(fixture), "steps": steps, "deployed_roots": deployed_roots,
            "passed": not any(f["level"] == "error" for f in findings), "findings": findings}


# Optional Stage 6: pack the staged package into an installable bundle (plan Section 10.3).
def pack_plugin(staged_dir: Path, dist_dir: Path, apm_bin: str) -> dict:
    """Run apm install (to write the lockfile) then apm pack --archive into dist_dir."""
    dist_dir.mkdir(parents=True, exist_ok=True)
    steps = [_run_apm(apm_bin, ["install"], staged_dir),
             _run_apm(apm_bin, ["pack", "--archive", "-o", str(dist_dir)], staged_dir)]
    bundles = sorted(str(b) for b in dist_dir.glob(f"{staged_dir.name}-*.zip"))
    passed = all(st["exit_code"] == 0 for st in steps) and bool(bundles)
    return {"steps": steps, "bundles": bundles, "passed": passed}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

# Run all five stages and write the JSON report.
def run_pipeline(args: argparse.Namespace) -> dict:
    """Execute inspect -> normalize -> validate -> package -> test deploy."""
    repo_root = Path(args.repo_root).resolve()
    plugin_dir = (repo_root / args.plugin).resolve()
    build_dir = (repo_root / args.build_dir).resolve()
    staged_dir = build_dir / plugin_dir.name
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]

    report: dict = {"plugin": plugin_dir.name, "targets": targets}
    inspection = inspect_plugin(repo_root, plugin_dir)
    report["inspect"] = {k: v for k, v in inspection.items() if k != "symlinks"}
    report["inspect"]["symlink_count"] = len(inspection["symlinks"])
    report["normalize"] = normalize_plugin(inspection, staged_dir)
    report["validate"] = validate_package(staged_dir, report["normalize"])
    report["package"] = package_plugin(staged_dir, inspection, targets)
    if args.skip_deploy:
        report["test_deploy"] = {"skipped": True}
    else:
        fixture = (repo_root / args.deploy_dir).resolve() / plugin_dir.name
        report["test_deploy"] = run_test_deploy(staged_dir, fixture, targets, args.apm, inspection["skills"])
    if args.pack:
        report["pack"] = pack_plugin(staged_dir, (repo_root / args.dist_dir).resolve(), args.apm)
    report["passed"] = (report["validate"]["passed"] and report["test_deploy"].get("passed", True)
                        and report.get("pack", {}).get("passed", True))
    report_path = build_dir / f"{plugin_dir.name}.report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


# CLI entry point: parse arguments, run the pipeline, print a summary.
def main() -> None:
    """Parse CLI arguments and run the APM build pipeline for one plugin."""
    parser = argparse.ArgumentParser(description="Build-time APM packaging pipeline (plan Section 4)")
    parser.add_argument("--plugin", required=True, help="Plugin path relative to --repo-root, e.g. plugins/dev-utils")
    parser.add_argument("--repo-root", default=".", help="Git work tree root (default: .)")
    parser.add_argument("--build-dir", default="build/staging", help="Staging root (default: build/staging)")
    parser.add_argument("--deploy-dir", default="build/test-deploy", help="Fixture root (default: build/test-deploy)")
    parser.add_argument("--targets", default=",".join(DEFAULT_TARGETS), help="Comma-separated APM targets")
    parser.add_argument("--apm", default="apm", help="APM CLI executable (default: apm on PATH)")
    parser.add_argument("--skip-deploy", action="store_true", help="Skip Stage 5 (no APM needed)")
    parser.add_argument("--pack", action="store_true", help="Also pack an installable bundle (apm pack)")
    parser.add_argument("--dist-dir", default="build/dist", help="Bundle output root (default: build/dist)")
    args = parser.parse_args()

    report = run_pipeline(args)
    val, dep = report["validate"], report["test_deploy"]
    print(f"Plugin:     {report['plugin']}  ({len(report['inspect']['skills'])} skills, "
          f"{report['inspect']['symlink_count']} symlinks)")
    print(f"Staged:     {report['normalize']['staging_dir']}")
    print(f"Validate:   {'PASS' if val['passed'] else 'FAIL'} ({val['error_count']} errors)")
    for f in val["findings"][:20]:
        print(f"  [{f['level'].upper()}] {f['check']}: {f['path']} {f['detail']}")
        print(f"      fix: {f['fix']}" + (f"  ->  {f['suggestion']}" if f.get("suggestion") else ""))
    print(f"Test deploy: {'SKIPPED' if dep.get('skipped') else ('PASS' if dep['passed'] else 'FAIL')}")
    for f in dep.get("findings", [])[:20]:
        print(f"  [{f['level'].upper()}] {f['check']}: {f['path']} {f['detail']}")
    if "pack" in report:
        print(f"Pack:       {'PASS' if report['pack']['passed'] else 'FAIL'} {', '.join(report['pack']['bundles'])}")
    print(f"Report:     {report['report_path']}")
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
