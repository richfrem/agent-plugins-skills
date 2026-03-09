# Code File: vector_consistency_check.py

**Path:** `scripts/stabilizers/vector_consistency_check.py`
**Language:** Python
**Type:** Code Implementation

## Module Description

Vector Consistency Stabilizer - Protocol 126 Implementation

This module implements the Vector DB Consistency Stabilizer from Protocol 126:
QEC-Inspired AI Robustness (Virtual Stabilizer Architecture).

The stabilizer detects semantic drift by re-querying the vector database to verify
that fact atoms are still supported by the knowledge base.

Mission: LEARN-CLAUDE-003
Author: Antigravity AI
Date: 2025-12-14

## Dependencies

- `json`
- `re`
- `dataclasses.dataclass`
- `dataclasses.field`
- `datetime.datetime`
- `enum.Enum`
- `pathlib.Path`
- `typing.List`
- `typing.Dict`
- `typing.Any`
- ... and 2 more

## Class: `StabilizerStatus`

**Line:** 26

**Documentation:**

Status codes for stabilizer checks.

**Source Code:**

```python
class StabilizerStatus(Enum):
    """Status codes for stabilizer checks."""
    STABLE = "STABLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CONFIDENCE_DEGRADED = "CONFIDENCE_DEGRADED"
    ERROR = "ERROR"
```

## Class: `FactAtom`

**Line:** 35

**Documentation:**

Atomic unit of retrievable information (Virtual Qubit in Protocol 126).

Attributes:
    id: Unique identifier for the fact atom
    content: The actual fact content (monosemantic)
    source_file: Path to the source markdown file
    timestamp_created: When this fact was created
    confidence_score: Optional confidence score from metadata
    metadata: Additional YAML frontmatter metadata

**Source Code:**

```python
class FactAtom:
    """
    Atomic unit of retrievable information (Virtual Qubit in Protocol 126).
    
    Attributes:
        id: Unique identifier for the fact atom
        content: The actual fact content (monosemantic)
        source_file: Path to the source markdown file
        timestamp_created: When this fact was created
        confidence_score: Optional confidence score from metadata
        metadata: Additional YAML frontmatter metadata
    """
    id: str
    content: str
    source_file: str
    timestamp_created: datetime
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## Class: `StabilizerResult`

**Line:** 56

**Documentation:**

Result of a vector consistency check.

Attributes:
    fact_atom_id: ID of the checked fact atom
    status: Stabilizer status (STABLE, DRIFT_DETECTED, etc.)
    relevance_delta: Change in relevance score (0.0 = perfect match)
    source_in_top_results: Whether original source appears in top 3 results
    top_results: List of top result file paths
    execution_time_ms: Time taken for the check
    error_message: Optional error message if status is ERROR

**Source Code:**

```python
class StabilizerResult:
    """
    Result of a vector consistency check.
    
    Attributes:
        fact_atom_id: ID of the checked fact atom
        status: Stabilizer status (STABLE, DRIFT_DETECTED, etc.)
        relevance_delta: Change in relevance score (0.0 = perfect match)
        source_in_top_results: Whether original source appears in top 3 results
        top_results: List of top result file paths
        execution_time_ms: Time taken for the check
        error_message: Optional error message if status is ERROR
    """
    fact_atom_id: str
    status: StabilizerStatus
    relevance_delta: float
    source_in_top_results: bool
    top_results: List[str]
    execution_time_ms: float
    error_message: Optional[str] = None
```

## Class: `StabilizerReport`

**Line:** 79

**Documentation:**

Comprehensive report for a stabilizer run.

Attributes:
    topic_dir: Directory that was checked
    total_facts_checked: Total number of fact atoms checked
    stable_count: Number of STABLE facts
    drift_count: Number of DRIFT_DETECTED facts
    degraded_count: Number of CONFIDENCE_DEGRADED facts
    error_count: Number of ERROR facts
    results: List of individual stabilizer results
    recommendations: List of recommended actions
    execution_time_ms: Total execution time
    timestamp: When the report was generated

**Source Code:**

```python
class StabilizerReport:
    """
    Comprehensive report for a stabilizer run.
    
    Attributes:
        topic_dir: Directory that was checked
        total_facts_checked: Total number of fact atoms checked
        stable_count: Number of STABLE facts
        drift_count: Number of DRIFT_DETECTED facts
        degraded_count: Number of CONFIDENCE_DEGRADED facts
        error_count: Number of ERROR facts
        results: List of individual stabilizer results
        recommendations: List of recommended actions
        execution_time_ms: Total execution time
        timestamp: When the report was generated
    """
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
```

## Function: `extract_fact_atoms`

**Line:** 107
**Signature:** `extract_fact_atoms(markdown_file: Path) -> List[FactAtom]`

**Documentation:**

Parse markdown file and extract fact atoms.

This function extracts individual facts from markdown content. Each paragraph
or list item is treated as a potential fact atom. YAML frontmatter is parsed
for metadata.

Args:
    markdown_file: Path to the markdown file to parse
    
Returns:
    List of FactAtom objects extracted from the file
    
Raises:
    FileNotFoundError: If the markdown file doesn't exist
    ValueError: If the file cannot be parsed

**Source Code:**

```python
def extract_fact_atoms(markdown_file: Path) -> List[FactAtom]:
    """
    Parse markdown file and extract fact atoms.
    
    This function extracts individual facts from markdown content. Each paragraph
    or list item is treated as a potential fact atom. YAML frontmatter is parsed
    for metadata.
    
    Args:
        markdown_file: Path to the markdown file to parse
        
    Returns:
        List of FactAtom objects extracted from the file
        
    Raises:
        FileNotFoundError: If the markdown file doesn't exist
        ValueError: If the file cannot be parsed
    """
    if not markdown_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
    
    try:
        # Parse frontmatter and content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        metadata = post.metadata
        content = post.content
        
        # Extract timestamp from metadata or file stats
        if 'last_verified' in metadata:
            timestamp = datetime.fromisoformat(str(metadata['last_verified']))
        else:
            timestamp = datetime.fromtimestamp(markdown_file.stat().st_mtime)
        
        # Extract fact atoms from content
        fact_atoms = []
        
        # Split content into paragraphs and list items
        lines = content.split('\n')
        current_paragraph = []
        fact_id_counter = 0
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines, headers, and code blocks
            if not line or line.startswith('#') or line.startswith('```'):
                if current_paragraph:
                    # Process accumulated paragraph
                    paragraph_text = ' '.join(current_paragraph).strip()
                    if len(paragraph_text) > 20:  # Minimum fact length
                        fact_atoms.append(FactAtom(
                            id=f"{markdown_file.stem}_fact_{fact_id_counter}",
                            content=paragraph_text,
                            source_file=str(markdown_file),
                            timestamp_created=timestamp,
                            metadata=metadata
                        ))
                        fact_id_counter += 1
                    current_paragraph = []
                continue
            
            # Handle list items as individual facts
            if line.startswith(('-', '*', '+')):
                # Process previous paragraph if any
                if current_paragraph:
                    paragraph_text = ' '.join(current_paragraph).strip()
                    if len(paragraph_text) > 20:
                        fact_atoms.append(FactAtom(
                            id=f"{markdown_file.stem}_fact_{fact_id_counter}",
                            content=paragraph_text,
                            source_file=str(markdown_file),
                            timestamp_created=timestamp,
                            metadata=metadata
                        ))
                        fact_id_counter += 1
                    current_paragraph = []
                
                # Add list item as fact
                list_content = re.sub(r'^[-*+]\s+', '', line)
                if len(list_content) > 20:
                    fact_atoms.append(FactAtom(
                        id=f"{markdown_file.stem}_fact_{fact_id_counter}",
                        content=list_content,
                        source_file=str(markdown_file),
                        timestamp_created=timestamp,
                        metadata=metadata
                    ))
                    fact_id_counter += 1
            else:
                # Accumulate paragraph
                current_paragraph.append(line)
        
        # Process final paragraph
        if current_paragraph:
            paragraph_text = ' '.join(current_paragraph).strip()
            if len(paragraph_text) > 20:
                fact_atoms.append(FactAtom(
                    id=f"{markdown_file.stem}_fact_{fact_id_counter}",
                    content=paragraph_text,
                    source_file=str(markdown_file),
                    timestamp_created=timestamp,
                    metadata=metadata
                ))
        
        return fact_atoms
        
    except Exception as e:
        raise ValueError(f"Failed to parse markdown file {markdown_file}: {e}")
```

## Function: `vector_consistency_check`

**Line:** 219
**Signature:** `vector_consistency_check(fact_atom: FactAtom, cortex_query_func: callable, max_results: int, relevance_threshold: float) -> StabilizerResult`

**Documentation:**

Re-query vector DB to verify fact still supported.

Implementation from Protocol 126:
1. Re-query cortex with fact_atom.content
2. Check if original source_file in top 3 results
3. Calculate relevance_delta
4. Return STABLE, DRIFT_DETECTED, or CONFIDENCE_DEGRADED

Args:
    fact_atom: The fact atom to verify
    cortex_query_func: Function to query the Cortex MCP (cortex_query)
    max_results: Maximum number of results to retrieve (default: 5)
    relevance_threshold: Threshold for confidence degradation (default: 0.2)
    
Returns:
    StabilizerResult with status and metrics

**Source Code:**

```python
def vector_consistency_check(
    fact_atom: FactAtom,
    cortex_query_func: callable,
    max_results: int = 5,
    relevance_threshold: float = 0.2
) -> StabilizerResult:
    """
    Re-query vector DB to verify fact still supported.
    
    Implementation from Protocol 126:
    1. Re-query cortex with fact_atom.content
    2. Check if original source_file in top 3 results
    3. Calculate relevance_delta
    4. Return STABLE, DRIFT_DETECTED, or CONFIDENCE_DEGRADED
    
    Args:
        fact_atom: The fact atom to verify
        cortex_query_func: Function to query the Cortex MCP (cortex_query)
        max_results: Maximum number of results to retrieve (default: 5)
        relevance_threshold: Threshold for confidence degradation (default: 0.2)
        
    Returns:
        StabilizerResult with status and metrics
    """
    import time
    start_time = time.time()
    
    try:
        # Query the vector database with the fact content
        query_result = cortex_query_func(
            query=fact_atom.content,
            max_results=max_results
        )
        
        # Parse the query result
        if isinstance(query_result, str):
            query_data = json.loads(query_result)
        else:
            query_data = query_result
        
        # Extract results
        results = query_data.get('results', [])
        
        if not results:
            execution_time = (time.time() - start_time) * 1000
            return StabilizerResult(
                fact_atom_id=fact_atom.id,
                status=StabilizerStatus.ERROR,
                relevance_delta=1.0,
                source_in_top_results=False,
                top_results=[],
                execution_time_ms=execution_time,
                error_message="No results returned from vector database"
            )
        
        # Extract top result file paths
        top_results = []
        source_in_top_3 = False
        
        for i, result in enumerate(results[:3]):
            result_file = result.get('file_path', '')
            top_results.append(result_file)
            
            # Check if original source is in top 3
            if Path(result_file).resolve() == Path(fact_atom.source_file).resolve():
                source_in_top_3 = True
        
        # Calculate relevance delta
        # If source is in top 3, delta is low; otherwise, it's high
        if source_in_top_3:
            # Source found - calculate position-based delta
            relevance_delta = 0.0  # Perfect match
        else:
            # Source not in top 3 - high delta
            relevance_delta = 0.5
        
        # Determine status
        if source_in_top_3:
            status = StabilizerStatus.STABLE
        elif relevance_delta > relevance_threshold:
            status = StabilizerStatus.DRIFT_DETECTED
        else:
            status = StabilizerStatus.CONFIDENCE_DEGRADED
        
        execution_time = (time.time() - start_time) * 1000
        
        return StabilizerResult(
            fact_atom_id=fact_atom.id,
            status=status,
            relevance_delta=relevance_delta,
            source_in_top_results=source_in_top_3,
            top_results=top_results,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return StabilizerResult(
            fact_atom_id=fact_atom.id,
            status=StabilizerStatus.ERROR,
            relevance_delta=1.0,
            source_in_top_results=False,
            top_results=[],
            execution_time_ms=execution_time,
            error_message=str(e)
        )
```

## Function: `run_stabilizer_check`

**Line:** 327
**Signature:** `run_stabilizer_check(topic_dir: Path, cortex_query_func: callable, max_results: int, relevance_threshold: float) -> StabilizerReport`

**Documentation:**

Run stabilizer on all notes in a topic directory.

Args:
    topic_dir: Path to the topic directory containing markdown notes
    cortex_query_func: Function to query the Cortex MCP
    max_results: Maximum results per query (default: 5)
    relevance_threshold: Threshold for confidence degradation (default: 0.2)
    
Returns:
    StabilizerReport with comprehensive results and recommendations

**Source Code:**

```python
def run_stabilizer_check(
    topic_dir: Path,
    cortex_query_func: callable,
    max_results: int = 5,
    relevance_threshold: float = 0.2
) -> StabilizerReport:
    """
    Run stabilizer on all notes in a topic directory.
    
    Args:
        topic_dir: Path to the topic directory containing markdown notes
        cortex_query_func: Function to query the Cortex MCP
        max_results: Maximum results per query (default: 5)
        relevance_threshold: Threshold for confidence degradation (default: 0.2)
        
    Returns:
        StabilizerReport with comprehensive results and recommendations
    """
    import time
    start_time = time.time()
    
    if not topic_dir.exists():
        raise FileNotFoundError(f"Topic directory not found: {topic_dir}")
    
    # Find all markdown files in the topic directory
    markdown_files = list(topic_dir.rglob('*.md'))
    
    if not markdown_files:
        raise ValueError(f"No markdown files found in {topic_dir}")
    
    # Extract fact atoms from all files
    all_fact_atoms = []
    for md_file in markdown_files:
        try:
            fact_atoms = extract_fact_atoms(md_file)
            all_fact_atoms.extend(fact_atoms)
        except Exception as e:
            print(f"Warning: Failed to extract facts from {md_file}: {e}")
    
    # Run stabilizer check on each fact atom
    results = []
    stable_count = 0
    drift_count = 0
    degraded_count = 0
    error_count = 0
    
    for fact_atom in all_fact_atoms:
        result = vector_consistency_check(
            fact_atom,
            cortex_query_func,
            max_results,
            relevance_threshold
        )
        results.append(result)
        
        # Update counters
        if result.status == StabilizerStatus.STABLE:
            stable_count += 1
        elif result.status == StabilizerStatus.DRIFT_DETECTED:
            drift_count += 1
        elif result.status == StabilizerStatus.CONFIDENCE_DEGRADED:
            degraded_count += 1
        elif result.status == StabilizerStatus.ERROR:
            error_count += 1
    
    # Generate recommendations
    recommendations = []
    
    if drift_count > 0:
        recommendations.append(
            f"⚠️ DRIFT DETECTED: {drift_count} fact(s) no longer supported by vector DB. "
            "Consider re-ingesting or updating source documents."
        )
    
    if degraded_count > 0:
        recommendations.append(
            f"⚡ CONFIDENCE DEGRADED: {degraded_count} fact(s) have reduced relevance. "
            "Review and potentially refresh these facts."
        )
    
    if error_count > 0:
        recommendations.append(
            f"❌ ERRORS: {error_count} fact(s) could not be verified. "
            "Check vector database connectivity and data integrity."
        )
    
    if stable_count == len(all_fact_atoms):
        recommendations.append(
            "✅ ALL STABLE: All fact atoms are well-supported by the vector database."
        )
    
    execution_time = (time.time() - start_time) * 1000
    
    return StabilizerReport(
        topic_dir=str(topic_dir),
        total_facts_checked=len(all_fact_atoms),
        stable_count=stable_count,
        drift_count=drift_count,
        degraded_count=degraded_count,
        error_count=error_count,
        results=results,
        recommendations=recommendations,
        execution_time_ms=execution_time,
        timestamp=datetime.now()
    )
```

## Function: `format_report`

**Line:** 434
**Signature:** `format_report(report: StabilizerReport) -> str`

**Documentation:**

Format a stabilizer report as human-readable text.

Args:
    report: The stabilizer report to format
    
Returns:
    Formatted report string

**Source Code:**

```python
def format_report(report: StabilizerReport) -> str:
    """
    Format a stabilizer report as human-readable text.
    
    Args:
        report: The stabilizer report to format
        
    Returns:
        Formatted report string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("VECTOR CONSISTENCY STABILIZER REPORT")
    lines.append("Protocol 126: QEC-Inspired AI Robustness")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Topic Directory: {report.topic_dir}")
    lines.append(f"Timestamp: {report.timestamp.isoformat()}")
    lines.append(f"Execution Time: {report.execution_time_ms:.2f}ms")
    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Facts Checked: {report.total_facts_checked}")
    lines.append(f"✅ Stable: {report.stable_count}")
    lines.append(f"⚠️  Drift Detected: {report.drift_count}")
    lines.append(f"⚡ Confidence Degraded: {report.degraded_count}")
    lines.append(f"❌ Errors: {report.error_count}")
    lines.append("")
    
    if report.recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        for rec in report.recommendations:
            lines.append(f"• {rec}")
        lines.append("")
    
    # Show details for non-stable facts
    non_stable = [r for r in report.results if r.status != StabilizerStatus.STABLE]
    if non_stable:
        lines.append("DETAILED RESULTS (Non-Stable Facts Only)")
        lines.append("-" * 80)
        for result in non_stable:
            lines.append(f"\nFact ID: {result.fact_atom_id}")
            lines.append(f"Status: {result.status.value}")
            lines.append(f"Relevance Delta: {result.relevance_delta:.3f}")
            lines.append(f"Source in Top 3: {result.source_in_top_results}")
            lines.append(f"Execution Time: {result.execution_time_ms:.2f}ms")
            if result.error_message:
                lines.append(f"Error: {result.error_message}")
            if result.top_results:
                lines.append("Top Results:")
                for i, top_result in enumerate(result.top_results, 1):
                    lines.append(f"  {i}. {top_result}")
    
    lines.append("")
    lines.append("=" * 80)
    
    return '\n'.join(lines)
```

## Function: `export_report_json`

**Line:** 494
**Signature:** `export_report_json(report: StabilizerReport, output_file: Path) -> None`

**Documentation:**

Export stabilizer report as JSON for machine readability.

Args:
    report: The stabilizer report to export
    output_file: Path to the output JSON file

**Source Code:**

```python
def export_report_json(report: StabilizerReport, output_file: Path) -> None:
    """
    Export stabilizer report as JSON for machine readability.
    
    Args:
        report: The stabilizer report to export
        output_file: Path to the output JSON file
    """
    report_dict = {
        'topic_dir': report.topic_dir,
        'timestamp': report.timestamp.isoformat(),
        'execution_time_ms': report.execution_time_ms,
        'summary': {
            'total_facts_checked': report.total_facts_checked,
            'stable_count': report.stable_count,
            'drift_count': report.drift_count,
            'degraded_count': report.degraded_count,
            'error_count': report.error_count
        },
        'recommendations': report.recommendations,
        'results': [
            {
                'fact_atom_id': r.fact_atom_id,
                'status': r.status.value,
                'relevance_delta': r.relevance_delta,
                'source_in_top_results': r.source_in_top_results,
                'top_results': r.top_results,
                'execution_time_ms': r.execution_time_ms,
                'error_message': r.error_message
            }
            for r in report.results
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=2)
```

---

**Generated by:** Code Ingestion Shim (Task 110)
**Source File:** `scripts/stabilizers/vector_consistency_check.py`
**Total Lines:** 536
