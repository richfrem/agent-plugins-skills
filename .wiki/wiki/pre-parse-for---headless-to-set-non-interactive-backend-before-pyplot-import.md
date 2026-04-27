---
concept: pre-parse-for---headless-to-set-non-interactive-backend-before-pyplot-import
source: plugin-code
source_file: agent-agentic-os/scripts/plot_eval_progress.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.703568+00:00
cluster: metric_col
content_hash: be2272420ff8b014
---

# Pre-parse for --headless to set non-interactive backend before pyplot import

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
Plot Eval Progress
=====================================

Purpose:
    Visualizes autoresearch eval loops from `results.tsv` outputs.
    Generates a step-progress chart tracking KEPT mutations and their scores.

Layer: Investigate

Arguments:
    --tsv, --path: Path to the `results.tsv` file OR a directory containing it.
                   Defaults to the current directory's `results.tsv`.
    --metric:      The column name in the TSV to plot (default: "score").
    --out:         Path to save the generated PNG plot.
    --live:        Enable live monitoring. Opens an interactive window and 
                   refreshes the plot automatically.
    --interval:    Refresh interval in seconds for live mode (default: 5).
    --headless:    Run in non-interactive mode. No GUI window will open.
                   Useful for background tasks or over SSH. Best combined 
                   with --live and --out for automated image generation.

Usage Examples:
    1. Basic one-off plot generation:
       python plot_eval_progress.py --tsv ./evals/ --out progress.png

    2. Live interactive dashboard (opens a window):
       python plot_eval_progress.py --tsv ./evals/ --live --interval 2

    3. Headless background watcher (auto-saves PNG on every change):
       python plot_eval_progress.py --path ./evals/ --live --headless --out monitor.png
"""

import argparse
import sys
import time
from pathlib import Path

# Pre-parse for --headless to set non-interactive backend before pyplot import
if "--headless" in sys.argv:
    try:
        import matplotlib
        matplotlib.use("Agg")
    except ImportError:
        pass

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    print("ERROR: Missing required dependencies. Run: pip install pandas matplotlib numpy")
    sys.exit(1)


# Load and validate eval results data from TSV
def load_and_validate_data(tsv_path: Path, metric_col: str) -> pd.DataFrame:
    """
    Loads eval results from TSV and enforces expected schema constraints.
    Returns a cleaned, normalized DataFrame restricted to valid metrics.

    Args:
        tsv_path: Path to the TSV file.
        metric_col: Name of the column containing the metric.

    Returns:
        DataFrame containing cleaned and validated data.
    """
    if not tsv_path.exists():
        print(f"ERROR: Cannot find {tsv_path}")
        sys.exit(1)

    print(f"Loading {tsv_path}...")
    try:
        df = pd.read_csv(tsv_path, sep="\t")
    except Exception as e:
        print(f"Failed to read TSV: {e}")
        sys.exit(1)

    # Standardize schema (lowercase column headers)
    df.columns = [c.strip().lower() for c in df.columns]

    if metric_col not in df.columns:
        print(f"ERROR: Metric '{metric_col}' not found in columns: {list(df.columns)}")
        sys.exit(1)

    # Enforce numeric typing
    df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")
    
    if "status" not in df.columns:
        print(f"ERROR: No 'status' column found.")
        sys.exit(1)

    # Normalize categorical columns
    df["status"] = df["status"].fillna("").str.strip().str.upper()
    df["description"] = df.get("description", df.get("desc", ""))

    # Drop fully invalid rows
    valid_df = df[df[metric_col].notna()].copy()
    valid_df = valid_df.reset_index(drop=True)

    if len(valid_df) == 0:
        print("No valid numeric data found for the given metric.")
        sys.exit(0)

    return valid_df


# Detect baseline score for y-axis framing
def _detect_baseline_score(df: pd.DataFrame, metric_col: str) -> float:
    """
    Detects baseline score for y-axis framing from the dataframe.

    Args:
        df: The dataframe containing eval data.
        metric_col: The column containing the metric score.

    Returns:
        The detected baseline float score.
    """
    baseline_rows = df[df["status"] == "BASELINE"]
    if len(baseline_rows) > 0:
        baseline_score = float(baselin

*(content truncated)*

## See Also

- [[try-to-import-rlm-for-code-context-injection]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]
- [[function-parse-xml-to-markdown]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/scripts/plot_eval_progress.py`
- **Indexed:** 2026-04-27T05:21:03.703568+00:00
