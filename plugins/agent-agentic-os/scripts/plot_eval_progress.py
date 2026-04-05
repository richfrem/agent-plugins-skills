#!/usr/bin/env python3
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
def plot_progress(df: pd.DataFrame, metric_col: str, out_path: Path = None, ax: plt.Axes = None, title: str = None) -> None:
    """
    Generates the matplotlib step chart mapping the progression of eval scores.
    Plots CRASHes, DISCARDs, and KEPT iterations with trajectory connecting BEST scores.

    Args:
        df: DataFrame containing the data to plot.
        metric_col: Name of the column with the metric to plot.
        out_path: Path to save the generated plot.
        ax: Optional pre-existing axes for redrawing.
        title: Optional title to display on the chart.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(16, 8))
    else:
        ax.clear()
        fig = ax.get_figure()

    baseline_score = _detect_baseline_score(df, metric_col)

    # Isolate relevant scoring ranges for tighter charting
    margin = 0.2 if baseline_score > 0 else 0.5
    interesting_data = df[df[metric_col] >= (baseline_score - margin)]

    # Map status classes to visual points
    disc = interesting_data[interesting_data["status"] == "DISCARD"]
    if len(disc) > 0:
        ax.scatter(disc.index, disc[metric_col], c="#cccccc", s=30, alpha=0.5, zorder=2, label="Discarded")

    crash = interesting_data[interesting_data["status"] == "CRASH"]
    if len(crash) > 0:
        ax.scatter(crash.index, crash[metric_col], c="#e74c3c", s=40, marker="x", zorder=2, label="Crashed")

    # Map status classes to visual points
    disc = interesting_data[interesting_data["status"] == "DISCARD"]
    if len(disc) > 0:
        ax.scatter(disc.index, disc[metric_col], c="#cccccc", s=30, alpha=0.5, zorder=2, label="Discarded")

    crash = interesting_data[interesting_data["status"] == "CRASH"]
    if len(crash) > 0:
        ax.scatter(crash.index, crash[metric_col], c="#e74c3c", s=40, marker="x", zorder=2, label="Crashed")

    # Segment the data by 'BASELINE' events to handle session restarts
    effective_keeps = interesting_data[interesting_data["status"].isin(["KEEP", "BASELINE"])]
    if len(effective_keeps) > 0:
        baseline_indices = effective_keeps[effective_keeps["status"] == "BASELINE"].index.tolist()
        
        # Track added labels to prevent legend duplication
        added_labels = set()
        
        # Process each session segment separately
        for i, start_idx in enumerate(baseline_indices):
            # Define segment boundaries
            next_start = baseline_indices[i+1] if i+1 < len(baseline_indices) else effective_keeps.index[-1] + 1
            segment_df = effective_keeps.loc[start_idx : next_start-1]
            
            if len(segment_df) == 0: continue
            
            s_idx = segment_df.index
            s_scores = segment_df[metric_col]
            s_running_max = s_scores.cummax()
            
            # 1. Plot Segmented Running Best line
            label = "Running Best" if "Running Best" not in added_labels else None
            ax.step(s_idx, s_running_max, where="post", color="#27ae60",
                    linewidth=2.5, alpha=0.8, zorder=3, label=label)
            if label: added_labels.add(label)
            
            # 2. Plot Strictly Better points (New Best)
            # Find points where score > previous max IN THIS SEGMENT
            # For the very first point of a segment (the Baseline), we handle it separately
            k_df = segment_df[segment_df["status"] == "KEEP"].copy()
            if len(k_df) > 0:
                # We want STRICTOR better (score > running_max_of_previous_steps)
                is_best = []
                # Baseline of this segment
                local_best = segment_df.iloc[0][metric_col]
                
                for score in k_df[metric_col]:
                    if score > local_best:
                        is_best.append(True)
                        local_best = score
                    else:
                        is_best.append(False)
                
                k_df["is_best"] = is_best
                new_best = k_df[k_df["is_best"]]
                sub_optimal = k_df[~k_df["is_best"]]
                
                if len(new_best) > 0:
                    lbl = "New Best" if "New Best" not in added_labels else None
                    ax.scatter(new_best.index, new_best[metric_col], c="#2ecc71", s=80, 
                               zorder=5, label=lbl, edgecolors="black", linewidths=0.8)
                    _annotate_nodes(ax, df, new_best.index, new_best[metric_col])
                    if lbl: added_labels.add(lbl)
                
                if len(sub_optimal) > 0:
                    lbl = "Sub-optimal Keep" if "Sub-optimal Keep" not in added_labels else None
                    ax.scatter(sub_optimal.index, sub_optimal[metric_col], c="#f39c12", s=40, 
                               zorder=4, label=lbl, edgecolors="black", linewidths=0.5, alpha=0.6)
                    if lbl: added_labels.add(lbl)

            # 3. Plot Baseline Diamond for this segment
            baseline_only = segment_df[segment_df["status"] == "BASELINE"]
            if len(baseline_only) > 0:
                lbl = "Baseline" if "Baseline" not in added_labels else None
                ax.scatter(baseline_only.index, baseline_only[metric_col], c="#3498db", s=100, 
                           zorder=5, label=lbl, marker="D", edgecolors="black")
                _annotate_nodes(ax, df, baseline_only.index, baseline_only[metric_col])
                if lbl: added_labels.add(lbl)

    # Style grid
    ax.set_xlabel("Iteration Step", fontsize=12, fontweight='bold')
    ax.set_ylabel(f"Metric: {metric_col.upper()} (Higher is better)", fontsize=12, fontweight='bold')
    
    chart_title = title if title else f"Agentic Eval Progress Loop: {len(df)} Iterations"
    ax.set_title(chart_title, fontsize=15, pad=20)
    
    ax.grid(True, linestyle="--", alpha=0.4)
    # Ensure legend is clean and well-positioned
    ax.legend(loc="upper left", fontsize=10, frameon=True, fancybox=True, framealpha=0.9)
    
    # Ensure layout accounts for title padding
    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 

    # Save artifact if path provided
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        print(f"Success! Saved visualization to {out_path}")


# CLI entrypoint for plot_eval_progress
def main() -> None:
    """
    CLI entrypoint.
    """
    parser = argparse.ArgumentParser(description="Plot agentic eval loop progress from results.tsv.")
    parser.add_argument("--tsv", "--path", default="results.tsv", help="Path to results.tsv or directory containing it.")
    parser.add_argument("--metric", default="score", help="Metric column name to plot (default: score).")
    parser.add_argument("--out", help="Path to save the output plot image.")
    parser.add_argument("--live", action="store_true", help="Enable live monitoring and auto-refresh.")
    parser.add_argument("--interval", type=int, default=5, help="Refresh interval in seconds for live mode.")
    parser.add_argument("--headless", action="store_true", help="Run without opening a GUI window (best for background/CI).")
    
    args = parser.parse_args()
    
    # Path resolution
    input_path = Path(args.tsv)
    if input_path.is_dir():
        tsv_path = input_path / "results.tsv"
    else:
        tsv_path = input_path

    # Extract a friendly name for the title (e.g., from 'skills/convert-mermaid')
    parts = tsv_path.parts
    friendly_name = "Unknown Tool"
    if "skills" in parts:
        idx = parts.index("skills")
        if len(parts) > idx + 1:
            friendly_name = f"Skill: {parts[idx+1]}"
    elif "plugins" in parts:
        idx = parts.index("plugins")
        if len(parts) > idx + 1:
            friendly_name = f"Plugin: {parts[idx+1]}"
    else:
        # Fallback to parent directory name if not in standard skill/plugin structure
        friendly_name = f"Path: {tsv_path.parent.name}"

    metric_col = args.metric.strip().lower()
    out_path = Path(args.out) if args.out else None

    # Process
    if args.live:
        print(f"Entering LIVE mode for {friendly_name} (refreshing every {args.interval}s)...")
        if not args.headless:
            plt.ion()
        
        fig, ax = plt.subplots(figsize=(16, 8))
        if not args.headless:
            try:
                fig.canvas.manager.set_window_title(f"Eval Progress - {friendly_name}")
            except Exception:
                pass # Some backends don't support this
        
        try:
            while True:
                # Check for window closure to exit gracefully
                if not args.headless and not plt.fignum_exists(fig.number):
                    print("Window closed by user. Exiting live mode.")
                    break

                if tsv_path.exists():
                    try:
                        df = load_and_validate_data(tsv_path, metric_col)
                        # In live mode, we still want to save to out_path if requested
                        # Pass friendly_name to plot_progress to avoid truncation issues
                        full_title = f"{friendly_name}\nAgentic Eval Progress Loop: {len(df)} Iterations"
                        plot_progress(df, metric_col, out_path=out_path, ax=ax, title=full_title)
                        
                        if not args.headless:
                            fig.canvas.draw_idle()
                            fig.canvas.flush_events()
                            
                    except Exception as e:
                        print(f"[{time.strftime('%H:%M:%S')}] Update failed: {e}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Waiting for {tsv_path}...")
                
                if not args.headless:
                    plt.pause(args.interval)
                else:
                    time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nLive monitoring stopped.")
            if not args.headless:
                plt.ioff()
                plt.show()
    else:
        df = load_and_validate_data(tsv_path, metric_col)
        full_title = f"{friendly_name}\nAgentic Eval Progress Loop: {len(df)} Iterations"
        plot_progress(df, metric_col, out_path, title=full_title)


if __name__ == "__main__":
    main()
