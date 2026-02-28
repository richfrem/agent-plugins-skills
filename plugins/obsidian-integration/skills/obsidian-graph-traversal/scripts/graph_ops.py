"""
Obsidian Graph Traversal Engine

Purpose: Builds an in-memory graph index from wikilinks found across vault .md files.
Provides instant forward-link, backlink, and multi-degree connection queries.
Integrates with obsidian-parser from WP05 for link extraction.

Performance target: < 2 seconds for deep queries across 1000+ notes.
"""
import os
import re
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Set, List, Any, Optional
from collections import defaultdict


# ---------------------------------------------------------------------------
# Inline Link Extraction (T036: Hook into obsidian-parser logic)
# ---------------------------------------------------------------------------
# We inline the core regex from obsidian-parser to avoid import path issues
# across worktrees. At merge time, this can be refactored to import directly.

def extract_wikilinks(text: str) -> List[str]:
    """
    Extract all wikilink targets from text, excluding embeds (![[...]]).
    Returns a list of target note names (stripped of headings/blocks/aliases).
    """
    results = []
    # Negative lookbehind to skip embeds
    pattern = re.compile(r'(?<!\!)\[\[(.*?)\]\]')

    for match in pattern.finditer(text):
        inner = match.group(1)

        # Strip alias (everything after |)
        if '|' in inner:
            inner = inner.split('|', 1)[0]

        # Strip heading/block anchors (everything after #)
        if '#' in inner:
            inner = inner.split('#', 1)[0]

        target = inner.strip()
        if target:
            results.append(target)

    return results


# ---------------------------------------------------------------------------
# Graph Index (T037)
# ---------------------------------------------------------------------------
class VaultGraph:
    """
    In-memory bidirectional graph index of vault wikilinks.

    Stores:
    - forward_links: {source_note: {target1, target2, ...}}
    - back_links:    {target_note: {source1, source2, ...}}
    - file_mtimes:   {note_name: mtime} for incremental rebuilds
    """

    def __init__(self):
        self.forward_links: Dict[str, Set[str]] = defaultdict(set)
        self.back_links: Dict[str, Set[str]] = defaultdict(set)
        self.file_mtimes: Dict[str, float] = {}
        self.all_notes: Set[str] = set()
        self.vault_root: Optional[Path] = None
        self.build_time: float = 0.0

    def build(self, vault_root: Path, exclusions: List[str] = None) -> Dict[str, Any]:
        """
        Full scan of the vault, building the graph from scratch.
        """
        self.vault_root = vault_root
        self.forward_links.clear()
        self.back_links.clear()
        self.file_mtimes.clear()
        self.all_notes.clear()

        if exclusions is None:
            exclusions = [
                '.git', '.obsidian', '.worktrees', 'node_modules',
                '.vector_data', '.venv', '__pycache__', 'ARCHIVE',
                'archive_mcp_servers', 'archive-tests', 'dataset_package'
            ]

        start = time.time()
        files_scanned = 0

        for root, dirs, files in os.walk(vault_root):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d not in exclusions]

            for filename in files:
                if not filename.endswith('.md'):
                    continue

                filepath = Path(root) / filename
                note_name = filepath.stem
                self.all_notes.add(note_name)

                try:
                    content = filepath.read_text(encoding='utf-8')
                    mtime = filepath.stat().st_mtime
                    self.file_mtimes[note_name] = mtime

                    targets = extract_wikilinks(content)
                    for target in targets:
                        self.forward_links[note_name].add(target)
                        self.back_links[target].add(note_name)

                    files_scanned += 1
                except (OSError, UnicodeDecodeError):
                    continue

        self.build_time = time.time() - start

        return {
            "status": "built",
            "vault_root": str(vault_root),
            "files_scanned": files_scanned,
            "unique_notes": len(self.all_notes),
            "total_edges": sum(len(v) for v in self.forward_links.values()),
            "build_time_seconds": round(self.build_time, 3)
        }

    def get_forward_links(self, note_name: str) -> List[str]:
        """Get all notes that this note links TO (outbound)."""
        return sorted(self.forward_links.get(note_name, set()))

    def get_backlinks(self, note_name: str) -> List[str]:
        """Get all notes that link TO this note (inbound)."""
        return sorted(self.back_links.get(note_name, set()))

    def get_connections(self, note_name: str, depth: int = 1) -> Dict[str, Any]:
        """
        Get all notes connected within N degrees.
        Returns a dict with the connection graph.
        """
        visited: Set[str] = set()
        layers: Dict[int, Set[str]] = {}
        current_layer = {note_name}
        visited.add(note_name)

        for d in range(1, depth + 1):
            next_layer: Set[str] = set()
            for note in current_layer:
                # Forward + backward connections
                connections = self.forward_links.get(note, set()) | self.back_links.get(note, set())
                for conn in connections:
                    if conn not in visited:
                        next_layer.add(conn)
                        visited.add(conn)

            if next_layer:
                layers[d] = next_layer
            current_layer = next_layer

        return {
            "center": note_name,
            "depth": depth,
            "total_connected": len(visited) - 1,
            "layers": {str(k): sorted(v) for k, v in layers.items()}
        }

    def find_orphans(self) -> List[str]:
        """Find notes with no incoming OR outgoing links."""
        linked_notes = set(self.forward_links.keys()) | set(self.back_links.keys())
        orphans = self.all_notes - linked_notes
        return sorted(orphans)

    def save_index(self, filepath: Path) -> None:
        """Save the graph index to a JSON cache file."""
        data = {
            "vault_root": str(self.vault_root) if self.vault_root else None,
            "build_time": self.build_time,
            "forward_links": {k: sorted(v) for k, v in self.forward_links.items()},
            "back_links": {k: sorted(v) for k, v in self.back_links.items()},
            "file_mtimes": self.file_mtimes,
            "all_notes": sorted(self.all_notes),
        }
        filepath.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def load_index(self, filepath: Path) -> bool:
        """Load a previously saved graph index. Returns True on success."""
        if not filepath.exists():
            return False

        try:
            data = json.loads(filepath.read_text(encoding='utf-8'))
            self.vault_root = Path(data["vault_root"]) if data.get("vault_root") else None
            self.build_time = data.get("build_time", 0)
            self.forward_links = defaultdict(set, {k: set(v) for k, v in data.get("forward_links", {}).items()})
            self.back_links = defaultdict(set, {k: set(v) for k, v in data.get("back_links", {}).items()})
            self.file_mtimes = data.get("file_mtimes", {})
            self.all_notes = set(data.get("all_notes", []))
            return True
        except (json.JSONDecodeError, KeyError):
            return False


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Obsidian Graph Traversal")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    build_p = subparsers.add_parser('build', help='Build the graph index')
    build_p.add_argument('--vault-root', required=True)

    fwd_p = subparsers.add_parser('forward', help='Get forward links')
    fwd_p.add_argument('--note', required=True)
    fwd_p.add_argument('--vault-root', default='.')

    back_p = subparsers.add_parser('backlinks', help='Get backlinks')
    back_p.add_argument('--note', required=True)
    back_p.add_argument('--vault-root', default='.')

    conn_p = subparsers.add_parser('connections', help='Get N-degree connections')
    conn_p.add_argument('--note', required=True)
    conn_p.add_argument('--depth', type=int, default=2)
    conn_p.add_argument('--vault-root', default='.')

    orph_p = subparsers.add_parser('orphans', help='Find orphaned notes')
    orph_p.add_argument('--vault-root', required=True)

    args = parser.parse_args()
    graph = VaultGraph()

    vault_root = Path(args.vault_root) if hasattr(args, 'vault_root') else Path('.')
    index_path = vault_root / '.graph-index.json'

    if args.command == 'build':
        result = graph.build(Path(args.vault_root))
        graph.save_index(index_path)
        print(json.dumps(result, indent=2))

    elif args.command in ('forward', 'backlinks', 'connections', 'orphans'):
        # Try to load cached index first
        if not graph.load_index(index_path):
            result = graph.build(vault_root)
            graph.save_index(index_path)

        if args.command == 'forward':
            links = graph.get_forward_links(args.note)
            print(json.dumps({"note": args.note, "forward_links": links, "count": len(links)}, indent=2))
        elif args.command == 'backlinks':
            links = graph.get_backlinks(args.note)
            print(json.dumps({"note": args.note, "backlinks": links, "count": len(links)}, indent=2))
        elif args.command == 'connections':
            result = graph.get_connections(args.note, args.depth)
            print(json.dumps(result, indent=2))
        elif args.command == 'orphans':
            orphans = graph.find_orphans()
            print(json.dumps({"orphans": orphans, "count": len(orphans)}, indent=2))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
