"""
Obsidian Vault CRUD Operations

Purpose: Safe Create/Read/Update/Append operations for Obsidian Vault notes.
Implements atomic writes (T026), advisory locking (T027), concurrent edit
detection via mtime (T028), and lossless YAML frontmatter via ruamel.yaml (T029).
"""
import os
import sys
import json
import argparse
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# --- T029: Lossless YAML (ruamel.yaml preferred, fallback warning) ---
try:
    from ruamel.yaml import YAML
    _yaml = YAML()
    _yaml.preserve_quotes = True
    _yaml.default_flow_style = False
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False
    print("WARNING: ruamel.yaml not installed. Frontmatter operations will be unavailable.", file=sys.stderr)
    print("Install with: pip install ruamel.yaml", file=sys.stderr)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
VAULT_ROOT = Path(os.environ.get("SANCTUARY_VAULT_PATH", Path(__file__).resolve().parents[4]))
LOCK_FILE = VAULT_ROOT / ".agent-lock"


# ---------------------------------------------------------------------------
# T027: Advisory Lock Protocol
# ---------------------------------------------------------------------------
class AgentLock:
    """
    Advisory lock for agent-vs-agent write coordination.
    Creates `.agent-lock` at the vault root before write batches.
    """

    def __init__(self, vault_root: Path = VAULT_ROOT):
        self.lock_path = vault_root / ".agent-lock"
        self._acquired = False

    def acquire(self, agent_name: str = "Antigravity") -> bool:
        """Acquire the advisory lock. Returns False if already locked."""
        if self.lock_path.exists():
            try:
                lock_info = json.loads(self.lock_path.read_text())
                print(f"WARNING: Vault is locked by agent '{lock_info.get('agent', 'unknown')}' "
                      f"since {lock_info.get('timestamp', 'unknown')}", file=sys.stderr)
            except (json.JSONDecodeError, OSError):
                print("WARNING: Stale lock file detected.", file=sys.stderr)
            return False

        lock_data = {
            "agent": agent_name,
            "pid": os.getpid(),
            "timestamp": _now_iso()
        }
        self.lock_path.write_text(json.dumps(lock_data, indent=2))
        self._acquired = True
        return True

    def release(self):
        """Release the advisory lock."""
        if self._acquired and self.lock_path.exists():
            self.lock_path.unlink()
            self._acquired = False

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Failed to acquire agent lock. Another agent is writing.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


# ---------------------------------------------------------------------------
# T028: Concurrent Edit Detection (mtime guard)
# ---------------------------------------------------------------------------
def capture_mtime(filepath: Path) -> float:
    """Capture the modification time of a file."""
    return filepath.stat().st_mtime


def check_mtime_unchanged(filepath: Path, original_mtime: float) -> bool:
    """
    Returns True if the file's mtime has NOT changed since we read it.
    If it changed, another process (human or Obsidian) edited the file.
    """
    current_mtime = filepath.stat().st_mtime
    return current_mtime == original_mtime


# ---------------------------------------------------------------------------
# T026: Atomic Write Protocol
# ---------------------------------------------------------------------------
def atomic_write(filepath: Path, content: str) -> None:
    """
    Write content to a file atomically using POSIX os.rename().
    1. Write to <filepath>.agent-tmp
    2. os.rename() to <filepath> (atomic on POSIX)
    3. Cleanup on failure
    """
    tmp_path = filepath.parent / f"{filepath.name}.agent-tmp"
    try:
        tmp_path.write_text(content, encoding='utf-8')
        os.rename(str(tmp_path), str(filepath))
    except Exception:
        # Cleanup the temp file if rename failed
        if tmp_path.exists():
            tmp_path.unlink()
        raise


# ---------------------------------------------------------------------------
# T029: Frontmatter Handling (ruamel.yaml)
# ---------------------------------------------------------------------------
def split_frontmatter(content: str) -> Tuple[Optional[str], str]:
    """
    Split a markdown file into frontmatter (YAML) and body.
    Returns (frontmatter_str, body) where frontmatter_str may be None.
    """
    if not content.startswith('---'):
        return None, content

    # Find the closing ---
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return None, content

    # Find the actual end (after the ---)
    end_of_frontmatter = end_idx + 3
    # Skip optional newline after closing ---
    if end_of_frontmatter < len(content) and content[end_of_frontmatter] == '\n':
        end_of_frontmatter += 1

    frontmatter_str = content[3:end_idx].strip()
    body = content[end_of_frontmatter:]

    return frontmatter_str, body


def parse_frontmatter(frontmatter_str: str) -> Dict[str, Any]:
    """Parse YAML frontmatter string using ruamel.yaml for lossless round-tripping."""
    if not HAS_RUAMEL:
        raise RuntimeError("ruamel.yaml is required for frontmatter operations. Install with: pip install ruamel.yaml")

    from io import StringIO
    return dict(_yaml.load(StringIO(frontmatter_str)) or {})


def render_frontmatter(data: Dict[str, Any]) -> str:
    """Render frontmatter dict back to YAML string, preserving formatting."""
    if not HAS_RUAMEL:
        raise RuntimeError("ruamel.yaml is required for frontmatter operations.")

    from io import StringIO
    stream = StringIO()
    _yaml.dump(data, stream)
    yaml_text = stream.getvalue()
    return f"---\n{yaml_text}---\n"


# ---------------------------------------------------------------------------
# CRUD Operations
# ---------------------------------------------------------------------------
def read_note(filepath: Path) -> Dict[str, Any]:
    """Read a note and return its frontmatter and body."""
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    mtime = capture_mtime(filepath)
    content = filepath.read_text(encoding='utf-8')
    fm_str, body = split_frontmatter(content)

    result = {
        "file": str(filepath),
        "mtime": mtime,
        "body": body,
    }

    if fm_str and HAS_RUAMEL:
        try:
            result["frontmatter"] = parse_frontmatter(fm_str)
        except Exception as e:
            result["frontmatter_error"] = str(e)
            result["frontmatter_raw"] = fm_str

    return result


def create_note(filepath: Path, content: str, frontmatter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new note with optional frontmatter."""
    if filepath.exists():
        return {"error": f"File already exists: {filepath}. Use 'update' instead."}

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    full_content = ""
    if frontmatter:
        full_content = render_frontmatter(frontmatter)
    full_content += content

    with AgentLock():
        atomic_write(filepath, full_content)

    return {"status": "created", "file": str(filepath)}


def update_note(filepath: Path, content: str) -> Dict[str, Any]:
    """Update a note's body, preserving frontmatter. Aborts if concurrent edit detected."""
    if not filepath.exists():
        return {"error": f"File not found: {filepath}. Use 'create' instead."}

    original_mtime = capture_mtime(filepath)
    original_content = filepath.read_text(encoding='utf-8')
    fm_str, _ = split_frontmatter(original_content)

    # Reconstruct with preserved frontmatter
    if fm_str:
        new_content = f"---\n{fm_str}\n---\n{content}"
    else:
        new_content = content

    with AgentLock():
        # T028: Check for concurrent edits before writing
        if not check_mtime_unchanged(filepath, original_mtime):
            return {"error": "CONCURRENT_EDIT_DETECTED", "file": str(filepath),
                    "message": "File was modified by another process since we read it. Aborting to prevent data loss."}
        atomic_write(filepath, new_content)

    return {"status": "updated", "file": str(filepath)}


def append_to_note(filepath: Path, content: str) -> Dict[str, Any]:
    """Append content to an existing note."""
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    original_mtime = capture_mtime(filepath)
    original_content = filepath.read_text(encoding='utf-8')

    new_content = original_content.rstrip('\n') + '\n\n' + content + '\n'

    with AgentLock():
        if not check_mtime_unchanged(filepath, original_mtime):
            return {"error": "CONCURRENT_EDIT_DETECTED", "file": str(filepath),
                    "message": "File was modified by another process since we read it. Aborting."}
        atomic_write(filepath, new_content)

    return {"status": "appended", "file": str(filepath)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    """Return current UTC time in ISO format."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Obsidian Vault CRUD Operations")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Read
    read_p = subparsers.add_parser('read', help='Read a note')
    read_p.add_argument('--file', required=True, help='Path to note')

    # Create
    create_p = subparsers.add_parser('create', help='Create a new note')
    create_p.add_argument('--file', required=True, help='Path for new note')
    create_p.add_argument('--content', required=True, help='Note body content')
    create_p.add_argument('--frontmatter', nargs='*', help='Key=value pairs for frontmatter')

    # Update
    update_p = subparsers.add_parser('update', help='Update a note body')
    update_p.add_argument('--file', required=True, help='Path to note')
    update_p.add_argument('--content', required=True, help='New body content')

    # Append
    append_p = subparsers.add_parser('append', help='Append to a note')
    append_p.add_argument('--file', required=True, help='Path to note')
    append_p.add_argument('--content', required=True, help='Content to append')

    args = parser.parse_args()

    if args.command == 'read':
        result = read_note(Path(args.file))
        print(json.dumps(result, indent=2, default=str))

    elif args.command == 'create':
        fm = None
        if args.frontmatter:
            fm = {}
            for kv in args.frontmatter:
                k, v = kv.split('=', 1)
                fm[k] = v
        content = args.content.replace('\\n', '\n')
        result = create_note(Path(args.file), content, fm)
        print(json.dumps(result, indent=2))

    elif args.command == 'update':
        content = args.content.replace('\\n', '\n')
        result = update_note(Path(args.file), content)
        print(json.dumps(result, indent=2))

    elif args.command == 'append':
        content = args.content.replace('\\n', '\n')
        result = append_to_note(Path(args.file), content)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
