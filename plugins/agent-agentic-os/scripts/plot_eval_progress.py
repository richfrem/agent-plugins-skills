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
def plot_progress(df: pd.DataFrame, metric_col: str, out_path: Path) -> None:
    """
    Generates the matplotlib step chart mapping the progression of eval scores.
    Plots CRASHes, DISCARDs, and KEPT iterations with trajectory connecting BEST scores.

    Args:
        df: DataFrame containing the data to plot.
        metric_col: Name of the column with the metric to plot.
        out_path: Path to save the generated plot.
    """
    fig, ax = plt.subplots(figsize=(16, 8))

    baseline_score = _detect_baseline_score(df, metric_col)

    # Isolate relevant scoring ranges for tighter charting
    margin = 0.2 if baseline_score > 0 else 0.5
    interesting_data = df[df[metric_col] >= (baseline_score - margin)]

    # Map status classes to visual points
    disc = interesting_data[interesting_data["status"] == "DISCARD"]
    ax.scatter(disc.index, disc[metric_col], c="#cccccc", s=30, alpha=0.5, zorder=2, label="Discarded")

    crash = interesting_data[interesting_data["status"] == "CRASH"]
    ax.scatter(crash.index, crash[metric_col], c="#e74c3c", s=40, marker="x", zorder=2, label="Crashed")

    kept_only = interesting_data[interesting_data["status"] == "KEEP"]
    ax.scatter(kept_only.index, kept_only[metric_col], c="#2ecc71", s=80, zorder=4, label="Kept", edgecolors="black", linewidths=0.8)

    baseline_only = interesting_data[interesting_data["status"] == "BASELINE"]
    ax.scatter(baseline_only.index, baseline_only[metric_col], c="#3498db", s=100, zorder=4, label="Baseline", marker="D", edgecolors="black")

    # Map the progressive running maximum
    effective_keeps = interesting_data[interesting_data["status"].isin(["KEEP", "BASELINE"])]
    if len(effective_keeps) > 0:
        kept_idx = effective_keeps.index
        kept_scores = effective_keeps[metric_col]
        running_max = kept_scores.cummax()  # Eval engine operates on 'higher is better'
        
        ax.step(kept_idx, running_max, where="post", color="#27ae60",
                linewidth=2.5, alpha=0.8, zorder=3, label="Running Best")

        _annotate_nodes(ax, df, kept_idx, kept_scores)

    # Style grid
    ax.set_xlabel("Iteration Step", fontsize=12, fontweight='bold')
    ax.set_ylabel(f"Metric: {metric_col.upper()} (Higher is better)", fontsize=12, fontweight='bold')
    ax.set_title(f"Agentic Eval Progress Loop: {len(df)} Iterations | {len(kept_only)} Improvements Kept", fontsize=15, pad=15)
    
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="best", fontsize=10)
    plt.tight_layout()

    # Save artifact
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Success! Saved visualization to {out_path}")


# CLI entrypoint for plot_eval_progress
def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Plot progress of agentic eval iterations.")
    parser.add_argument("--tsv", type=str, default="results.tsv", help="Path to results.tsv file")
    parser.add_argument("--metric", type=str, default="score", help="Metric column to plot (default: score)")
    parser.add_argument("--out", type=str, default="eval_progress.png", help="Output PNG path")
    
    args = parser.parse_args()
    tsv_path = Path(args.tsv)
    out_path = Path(args.out)
    metric_col = args.metric.lower()

    # Process
    df = load_and_validate_data(tsv_path, metric_col)
    plot_progress(df, metric_col, out_path)


if __name__ == "__main__":
    main()
