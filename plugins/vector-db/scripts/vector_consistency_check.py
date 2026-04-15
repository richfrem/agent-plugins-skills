#!/usr/bin/env python3
"""
vector_consistency_check.py
=====================================

Purpose:
    Implements the Vector DB Consistency Stabilizer (Protocol 126).
    Detects semantic drift by verifying that atomic facts still resolve to their 
    original source documents within the Vector index.

Layer: Retrieve / Curate

Usage:
    python vector_consistency_check.py --profile wiki --topic .agent/learning/
"""

import sys
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional

# Optional dependency for frontmatter
try:
    import frontmatter
except ImportError:
    frontmatter = None

# Robustly discover the Project Root
def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

# Ensure local imports work correctly
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from vector_config import VectorConfig
    from operations import VectorDBOperations
except ImportError as e:
    print(f"[ERROR] Could not import vector dependencies: {e}")
    sys.exit(1)


class StabilizerStatus(Enum):
    """Status codes for semantic stability checks."""
    STABLE = "STABLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CONFIDENCE_DEGRADED = "CONFIDENCE_DEGRADED"
    ERROR = "ERROR"


@dataclass
class FactAtom:
    """Atomic unit of retrievable information extracted from source docs."""
    id: str
    content: str
    source_file: str
    timestamp_created: datetime
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StabilizerResult:
    """Result metrics for a single fact atom consistency check."""
    fact_atom_id: str
    status: StabilizerStatus
    relevance_delta: float
    source_in_top_results: bool
    top_results: List[str]
    execution_time_ms: float
    error_message: Optional[str] = None


@dataclass
class StabilizerReport:
    """Consolidated report of an entire consistency audit run."""
    topic_dir: str
    total_facts_checked: int
    stable_count: int
    drift_count: int
    degraded_count: int
    error_count: int
    results: List[StabilizerResult]
    recommendations: List[str]
    execution_time_ms: float
    timestamp: datetime


def extract_fact_atoms(markdown_file: Path) -> List[FactAtom]:
    """
    Parses a Markdown file and extracts atomic, monosemantic fact chunks.

    Args:
        markdown_file: Path to the .md file to parse.

    Returns:
        List of extracted FactAtom objects.
    """
    if not markdown_file.exists():
        return []
    
    try:
        content = markdown_file.read_text(encoding='utf-8', errors='replace')
        metadata = {}
        
        if frontmatter:
            try:
                post = frontmatter.loads(content)
                metadata = post.metadata
                content = post.content
            except Exception:
                pass
        
        timestamp = datetime.fromtimestamp(markdown_file.stat().st_mtime)
        fact_atoms: List[FactAtom] = []
        fact_id_counter = 0
        
        # Split into paragraphs/bullets
        lines = content.split('\n')
        current_paragraph: List[str] = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith(('#', '```')):
                if current_paragraph:
                    text = ' '.join(current_paragraph).strip()
                    if len(text) > 20:
                        fact_atoms.append(FactAtom(
                            f"{markdown_file.stem}_{fact_id_counter}", text, str(markdown_file), timestamp, metadata=metadata
                        ))
                        fact_id_counter += 1
                    current_paragraph = []
                continue
            
            if line.startswith(('-', '*', '+')):
                list_content = re.sub(r'^[-*+]\s+', '', line)
                if len(list_content) > 20:
                    fact_atoms.append(FactAtom(
                        f"{markdown_file.stem}_{fact_id_counter}", list_content, str(markdown_file), timestamp, metadata=metadata
                    ))
                    fact_id_counter += 1
            else:
                current_paragraph.append(line)
        
        return fact_atoms
    except Exception as e:
        print(f"[WARN] Failed to parse facts from {markdown_file}: {e}")
        return []


def run_consistency_check(
    fact_atom: FactAtom,
    cortex: VectorDBOperations,
    max_results: int = 5,
    relevance_threshold: float = 0.2
) -> StabilizerResult:
    """
    Re-queries the Vector DB to verify the fact remains highly relevant to its source.

    Args:
        fact_atom: The atomic fact to verify.
        cortex: Initialized VectorDBOperations instance.
        max_results: Results to consider for top-N ranking.
        relevance_threshold: Threshold for drift detection.

    Returns:
        StabilizerResult indicating stability status.
    """
    start_time = time.time()
    try:
        results = cortex.query(fact_atom.content, max_results=max_results)
        
        if not results:
            return StabilizerResult(
                fact_atom.id, StabilizerStatus.ERROR, 1.0, False, [], (time.time() - start_time) * 1000, 
                "No results returned"
            )
        
        top_results = [res['source'] for res in results[:3]]
        source_rel = Path(fact_atom.source_file).resolve().name
        
        source_in_top_3 = False
        for top_res in top_results:
            if Path(top_res).name == source_rel:
                source_in_top_3 = True
                break
        
        status = StabilizerStatus.STABLE if source_in_top_3 else StabilizerStatus.DRIFT_DETECTED
        
        return StabilizerResult(
            fact_atom.id, status, 0.0 if source_in_top_3 else 0.5, source_in_top_3, top_results, 
            (time.time() - start_time) * 1000
        )
    except Exception as e:
        return StabilizerResult(
            fact_atom.id, StabilizerStatus.ERROR, 1.0, False, [], (time.time() - start_time) * 1000, str(e)
        )


def main() -> None:
    """Orchestrates the consistency audit over a target directory."""
    import argparse
    parser = argparse.ArgumentParser(description="Vector Consistency Stabilizer (Protocol 126)")
    parser.add_argument("--profile", type=str, required=True, help="Vector profile to check")
    parser.add_argument("--topic", type=str, required=True, help="Directory of markdown notes to check")
    args = parser.parse_args()
    
    config = VectorConfig(profile_name=args.profile, project_root=str(PROJECT_ROOT))
    cortex = VectorDBOperations(
        str(PROJECT_ROOT),
        child_collection=config.child_collection,
        parent_collection=config.parent_collection,
        chroma_host=config.chroma_host,
        chroma_port=config.chroma_port,
        chroma_data_path=config.chroma_data_path,
        embedding_model=config.embedding_model,
        parent_chunk_size=config.parent_chunk_size,
        parent_chunk_overlap=config.parent_chunk_overlap,
        child_chunk_size=config.child_chunk_size,
        child_chunk_overlap=config.child_chunk_overlap
    )
    
    topic_path = Path(args.topic).resolve()
    print(f"[RUN] Checking consistency of notes in: {topic_path}")
    
    notes = list(topic_path.rglob("*.md"))
    all_facts: List[FactAtom] = []
    for note in notes:
        all_facts.extend(extract_fact_atoms(note))
    
    print(f"[SYNC] Extracted {len(all_facts)} fact atoms from {len(notes)} documents.")
    
    stable = 0
    for fact in all_facts:
        res = run_consistency_check(fact, cortex)
        if res.status == StabilizerStatus.STABLE:
            stable += 1
            print(f"  [OK] {fact.id} (Stable)")
        else:
            print(f"  [DRIFT] {fact.id} -> Top match was {res.top_results[0] if res.top_results else 'None'}")
            
    print(f"\n[DONE] Audit Complete. Stability: {stable}/{len(all_facts)} ({(stable/len(all_facts)*100) if all_facts else 0:.1f}%)")


if __name__ == "__main__":
    main()
