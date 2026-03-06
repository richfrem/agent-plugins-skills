import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_EXCLUDES = {
    ".git",
    ".github",
    ".vscode",
    ".venv",
    ".venv-1",
    "venv",
    "__pycache__",
    "node_modules",
}


def find_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def should_skip(path: Path, root: Path, excludes: set[str]) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in excludes for part in parts)


def find_markdown_files(root: Path, excludes: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if should_skip(path, root, excludes):
            continue
        files.append(path)
    return sorted(files)


def load_folder_config(config_path: Path) -> dict:
    """Load bulk conversion scope config from JSON file."""
    if not config_path.exists() or not config_path.is_file():
        raise FileNotFoundError(f"Folder config file not found: {config_path}")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON object")

    folders = data.get("folders", [])
    include_root = data.get("include_root_markdown", True)

    if not isinstance(folders, list) or not all(isinstance(item, str) for item in folders):
        raise ValueError("Config field 'folders' must be an array of strings")
    if not isinstance(include_root, bool):
        raise ValueError("Config field 'include_root_markdown' must be boolean")

    return {
        "folders": folders,
        "include_root_markdown": include_root,
    }


def find_markdown_files_from_config(repo_root: Path, excludes: set[str], config: dict) -> list[Path]:
    """Find markdown files only within configured folders and optional repo root."""
    files: set[Path] = set()

    if config.get("include_root_markdown", True):
        for path in repo_root.glob("*.md"):
            if path.is_file() and not should_skip(path, repo_root, excludes):
                files.add(path.resolve())

    for folder in config.get("folders", []):
        folder_path = (repo_root / folder).resolve()
        if not folder_path.exists() or not folder_path.is_dir():
            print(f"WARN    Config folder not found, skipping: {folder_path}")
            continue

        for path in folder_path.rglob("*.md"):
            if path.is_file() and not should_skip(path, repo_root, excludes):
                files.add(path.resolve())

    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert all Markdown files under a root folder by calling plugin-local md_to_docx.py once per file."
    )
    parser.add_argument("--root", default=".", help="Root path to scan for .md files")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parent / "folders_to_convert.json"),
        help="Path to folders JSON config",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .docx files")
    parser.add_argument("--dry-run", action="store_true", help="Show planned conversions only")
    parser.add_argument("--exclude", action="append", default=[], help="Additional folder names to exclude")
    parser.add_argument(
        "--python-exe",
        default=sys.executable,
        help="Python executable used for converter calls",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    converter_script = Path(__file__).resolve().parent / "md_to_docx.py"

    if not converter_script.exists():
        raise FileNotFoundError(f"Single-file converter script not found: {converter_script}")

    scan_root = (repo_root / args.root).resolve() if args.root == "." else Path(args.root).expanduser().resolve()
    if not scan_root.exists() or not scan_root.is_dir():
        raise FileNotFoundError(f"Root folder not found: {scan_root}")

    config_path = Path(args.config).expanduser().resolve()
    folder_config = load_folder_config(config_path)

    excludes = set(DEFAULT_EXCLUDES) | set(args.exclude)
    md_files = find_markdown_files_from_config(repo_root=scan_root, excludes=excludes, config=folder_config)

    print(f"Scanning root: {scan_root}")
    print(f"Folder config: {config_path}")
    print(f"Converter: {converter_script}")
    print(f"Markdown files found: {len(md_files)}")

    converted = 0
    skipped = 0
    failed = 0

    for md_path in md_files:
        output_path = md_path.with_suffix(".docx")

        if output_path.exists() and not args.overwrite:
            skipped += 1
            print(f"SKIP    {md_path} -> {output_path} (exists)")
            continue

        if args.dry_run:
            converted += 1
            print(f"PLAN    {md_path} -> {output_path}")
            continue

        cmd = [
            args.python_exe,
            str(converter_script),
            str(md_path),
            "--output",
            str(output_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            converted += 1
            print(f"OK      {md_path} -> {output_path}")
        else:
            failed += 1
            error_message = result.stderr.strip() or result.stdout.strip() or "Unknown error"
            print(f"FAILED  {md_path} -> {output_path}")
            print(f"        {error_message}")

    print("\nSummary")
    print(f"- Converted: {converted}")
    print(f"- Skipped:   {skipped}")
    print(f"- Failed:    {failed}")

    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
