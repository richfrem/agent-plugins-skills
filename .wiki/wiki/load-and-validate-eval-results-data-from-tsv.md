---
concept: load-and-validate-eval-results-data-from-tsv
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-eval-runner/scripts/plot_eval_progress.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.280104+00:00
cluster: metric_col
content_hash: 4a495854679b9cf3
---

# Load and validate eval results data from TSV

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python3
"""
Plot Eval Progress
=====================================

Purpose:
    Visualizes autoresearch eval loops from `results.tsv` outputs.
    Generates a step-progress chart tracking KEPT mutations and their scores.

Layer: Investigate

Usage:
    python plot_eval_progress.py [--tsv results.tsv] [--metric score] [--out eval_progress.png]
"""

import argparse
import sys
from pathlib import Path

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
        baseline_score = float(baseline_rows.iloc[-1][metric_col])
        print(f"Baseline Score detected at: {baseline_score:.4f}")
    else:
        baseline_score = float(df.iloc[0][metric_col])
        print(f"No explicit baseline found. Using first row: {baseline_score:.4f}")
    return baseline_score


# Annotate kept iteration nodes on the chart
def _annotate_nodes(ax: plt.Axes, df: pd.DataFrame, kept_idx: pd.Index, kept_scores: pd.Series) -> None:
    """
    Annotates the line chart with descriptions from the kept nodes.

    Args:
        ax: The matplotlib axes.
        df: Dataframe containing textual descriptions.
        kept_idx: The indices of the kept models.
        kept_scores: The score series.
    """
    for idx, score in zip(kept_idx, kept_scores):
        desc = str(df.loc[idx, "description"]).strip()
        if not desc or desc.lower() == "nan": 
            continue
        if len(desc) > 50:
            desc = desc[:47] + "..."
            
        ax.annotate(desc, (idx, score), textcoords="offset points",
                    xytext=(8, -8), fontsize=9.0, color="#145a32", alpha=0.9,
                    rotation=15, ha="left", va="top")


# Generate plot visualizing eval progress
def plot_progress(df: pd.DataFrame, metric_col: str, 

*(content truncated)*

## See Also

- [[get-all-unique-queries-from-train-and-test-sets-with-should-trigger-info]]
- [[load-input-from-files-or-stdin]]
- [[prefer-remaining-broken-linksjson-post-fix-output-from-step-4-if-present-and]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-eval-runner/scripts/plot_eval_progress.py`
- **Indexed:** 2026-04-27T05:21:04.280104+00:00
