#!/usr/bin/env python3
"""
Watch Eval Progress
=====================================

Purpose:
    Real-time polling viewer that monitors `results.tsv` for changes
    and automatically triggers `plot_eval_progress.py` to update the chart.

Layer: Investigate

Usage:
    python watch_eval_progress.py [--tsv results.tsv] [--metric score] [--out eval_progress.png] [--interval 2]
"""

import argparse
import os
import sys
import time
import subprocess
from pathlib import Path


def main() -> None:
    """CLI entrypoint for watch_eval_progress."""
    parser = argparse.ArgumentParser(description="Watch results.tsv and plot progress automatically.")
    parser.add_argument("--tsv", type=str, default="results.tsv", help="Path to results.tsv file")
    parser.add_argument("--metric", type=str, default="score", help="Metric column to plot (default: score)")
    parser.add_argument("--out", type=str, default="eval_progress.png", help="Output PNG path")
    parser.add_argument("--interval", type=int, default=2, help="Polling interval in seconds")

    args = parser.parse_args()
    tsv_path = Path(args.tsv)
    
    if not tsv_path.exists():
        print(f"Waiting for {tsv_path} to be created...")

    last_mtime = -1
    script_dir = Path(__file__).parent.resolve()
    plotter_script = script_dir / "plot_eval_progress.py"

    print(f"Watching {tsv_path} (polling every {args.interval}s)...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            if tsv_path.exists():
                current_mtime = os.stat(tsv_path).st_mtime
                if current_mtime != last_mtime:
                    last_mtime = current_mtime
                    print(f"\n[{time.strftime('%H:%M:%S')}] Change detected in {tsv_path}. Updating chart...")
                    
                    cmd = [
                        sys.executable, str(plotter_script),
                        "--tsv", str(tsv_path),
                        "--metric", args.metric,
                        "--out", str(args.out)
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"[{time.strftime('%H:%M:%S')}] Chart updated successfully: {args.out}")
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] Plotting failed:\n{result.stderr}")
                        
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nWatcher stopped by user.")


if __name__ == "__main__":
    main()
