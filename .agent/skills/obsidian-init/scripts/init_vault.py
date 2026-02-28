"""
Obsidian Vault Initialization Script

Purpose: Bootstrap any project directory as an Obsidian Vault.
Creates .obsidian/app.json with sensible exclusion filters for developer repos.
"""
import os
import sys
import json
import argparse
from pathlib import Path

DEFAULT_EXCLUSIONS = [
    "node_modules/",
    ".worktrees/",
    ".vector_data/",
    ".git/",
    "venv/",
    "__pycache__/",
    "*.json",
    "*.jsonl",
    "learning_package_snapshot.md",
    "bootstrap_packet.md",
    "learning_debrief.md",
    "*_packet.md",
    "*_digest.md",
    "dataset_package/",
    "rlm_summary_cache*",
    "rlm_tool_cache*"
]


def count_markdown_files(vault_root: Path) -> int:
    """Count .md files in the vault (non-recursive top-level scan for speed)."""
    count = 0
    for root, dirs, files in os.walk(vault_root):
        # Skip .git and other hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.md'):
                count += 1
    return count


def init_vault(vault_root: Path, extra_exclusions: list = None, validate_only: bool = False) -> dict:
    """Initialize an Obsidian Vault at the given root."""
    vault_root = vault_root.resolve()

    if not vault_root.exists():
        return {"error": f"Directory does not exist: {vault_root}"}

    if not vault_root.is_dir():
        return {"error": f"Not a directory: {vault_root}"}

    # Count markdown files
    md_count = count_markdown_files(vault_root)
    if md_count == 0:
        return {"error": f"No .md files found in {vault_root}. Is this the right directory?"}

    obsidian_dir = vault_root / ".obsidian"
    app_json = obsidian_dir / "app.json"

    result = {
        "vault_root": str(vault_root),
        "markdown_files_found": md_count,
        "obsidian_dir_exists": obsidian_dir.exists(),
        "app_json_exists": app_json.exists(),
    }

    if validate_only:
        result["mode"] = "validate_only"
        if obsidian_dir.exists():
            result["status"] = "vault_already_initialized"
        else:
            result["status"] = "ready_to_initialize"
        return result

    # Build exclusion list
    exclusions = list(DEFAULT_EXCLUSIONS)
    if extra_exclusions:
        exclusions.extend(extra_exclusions)

    # Create .obsidian directory
    obsidian_dir.mkdir(exist_ok=True)

    # Write or update app.json
    app_config = {}
    if app_json.exists():
        try:
            app_config = json.loads(app_json.read_text())
        except json.JSONDecodeError:
            pass

    app_config["userIgnoreFilters"] = exclusions

    app_json.write_text(json.dumps(app_config, indent=2) + "\n")

    # Add .obsidian to .gitignore if not already there
    gitignore = vault_root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".obsidian/" not in content:
            with open(gitignore, 'a') as f:
                f.write("\n# Obsidian local config (user-specific)\n.obsidian/\n")
            result["gitignore_updated"] = True
    else:
        gitignore.write_text("# Obsidian local config (user-specific)\n.obsidian/\n")
        result["gitignore_created"] = True

    result["status"] = "initialized"
    result["exclusions_applied"] = len(exclusions)
    result["next_steps"] = [
        "Open the Obsidian desktop app",
        f"Click 'Open Folder as Vault' and select: {vault_root}",
        "All non-excluded .md files will be indexed automatically"
    ]

    # Hint about SANCTUARY_VAULT_PATH
    if not os.environ.get("SANCTUARY_VAULT_PATH"):
        result["env_hint"] = f"Consider setting: export SANCTUARY_VAULT_PATH={vault_root}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Initialize an Obsidian Vault")
    parser.add_argument('--vault-root', required=True, help='Root directory for the vault')
    parser.add_argument('--exclude', nargs='*', help='Additional exclusion patterns')
    parser.add_argument('--validate-only', action='store_true', help='Check without making changes')

    args = parser.parse_args()
    result = init_vault(Path(args.vault_root), args.exclude, args.validate_only)
    print(json.dumps(result, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
