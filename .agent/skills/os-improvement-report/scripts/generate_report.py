"""
loop_progress_report.generate_report
-------------------------------------
Reads per-skill results.tsv files (same format as autoresearch) and the improvement ledger
to produce progress charts and a text summary.

Per-skill TSV format (tab-separated):
    cycle_id  score  status  change_summary
    (status: KEEP / DISCARD / BASELINE)

Output:
    context/memory/reports/progress_YYYYMMDD_HHMM.png   -- one subplot per skill + north star
    context/memory/reports/summary_YYYYMMDD_HHMM.md     -- text summary

Usage:
    python3 generate_report.py --plugin-dir /path/to/agent-agentic-os [--project-dir /path/to/project]

Dependencies: pandas, matplotlib (see requirements.txt)
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import pandas as pd
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


KEEP_COLOR    = "#2ecc71"
DISCARD_COLOR = "#cccccc"
LINE_COLOR    = "#27ae60"


# ---------------------------------------------------------------------------
# Data loading — results.tsv (primary, per-skill, like autoresearch)
# ---------------------------------------------------------------------------

def find_results_tsvs(plugin_dir: Path) -> dict[str, Path]:
    """Return {skill_name: path_to_results.tsv} for every non-empty results.tsv."""
    found: dict[str, Path] = {}
    for tsv in plugin_dir.glob("skills/*/evals/results.tsv"):
        if tsv.stat().st_size > 0:
            found[tsv.parent.parent.name] = tsv
    # Also check skills/*/results.tsv (alternate location)
    for tsv in plugin_dir.glob("skills/*/results.tsv"):
        skill_name = tsv.parent.name
        if skill_name not in found and tsv.stat().st_size > 0:
            found[skill_name] = tsv
    return found


def load_results_tsv(path: Path, skill_name: str) -> pd.DataFrame:
    """
    Load a results.tsv.  Expected columns (flexible):
      cycle_id | score | status | change_summary
    Falls back gracefully if columns differ.
    """
    try:
        df = pd.read_csv(path, sep="\t", dtype=str)
    except Exception as e:
        print(f"[warn] Could not read {path}: {e}")
        return pd.DataFrame()

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Normalise the score column (accept: score, val_bpb, eval_score)
    for alias in ("val_bpb", "eval_score", "bpb"):
        if alias in df.columns and "score" not in df.columns:
            df = df.rename(columns={alias: "score"})

    # Normalise the status column
    if "status" in df.columns:
        df["status"] = df["status"].str.strip().str.upper()
    else:
        df["status"] = "UNKNOWN"

    if "score" in df.columns:
        df["score"] = pd.to_numeric(df["score"], errors="coerce")

    # Normalise description / change_summary
    for alias in ("description", "change_summary", "change", "summary"):
        if alias in df.columns and "change_summary" not in df.columns:
            df = df.rename(columns={alias: "change_summary"})

    if "change_summary" not in df.columns:
        df["change_summary"] = ""

    df["skill"] = skill_name
    return df


# ---------------------------------------------------------------------------
# Ledger loading (secondary — for north star + survey trace)
# ---------------------------------------------------------------------------

def _parse_md_table(section_text: str) -> pd.DataFrame:
    lines = [l.strip() for l in section_text.strip().splitlines() if l.strip()]
    header: list[str] | None = None
    rows: list[list[str]] = []
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.match(r"^-+$", c.replace(" ", "")) for c in cells if c):
            continue
        if header is None:
            header = cells
        else:
            rows.append(cells)
    if not header or not rows:
        return pd.DataFrame()
    rows = [r + [""] * (len(header) - len(r)) for r in rows]
    return pd.DataFrame(rows, columns=header)


def load_north_star(ledger_path: Path) -> pd.DataFrame:
    if not ledger_path.exists():
        return pd.DataFrame()
    text = ledger_path.read_text()
    m = re.search(r"## North Star Metric.*?\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not m:
        return pd.DataFrame()
    df = _parse_md_table(m.group(1))
    if df.empty:
        return df
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    for col in ("total_cycles", "completed_without_human_rescue",
                "human_interventions", "friction_events_total"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "completion_rate" in df.columns:
        df["rate_num"] = pd.to_numeric(
            df["completion_rate"].str.rstrip("%"), errors="coerce"
        )
    return df


# ---------------------------------------------------------------------------
# Plotting — autoresearch style
# ---------------------------------------------------------------------------

def plot_skill(ax: Any, df: pd.DataFrame, title: str) -> None:
    """Single skill progress chart — mirrors autoresearch analysis.ipynb."""
    if df.empty or "score" not in df.columns:
        ax.text(0.5, 0.5, "No data yet — run a loop cycle to populate results.tsv",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=10, color="#aaaaaa")
        ax.set_title(title, fontsize=11)
        return

    df = df.reset_index(drop=True)

    kept    = df[df["status"] == "KEEP"]
    disc    = df[df["status"] == "DISCARD"]
    base    = df[df["status"] == "BASELINE"]

    # Discarded — faint grey dots
    if not disc.empty:
        ax.scatter(disc.index.tolist(), disc["score"].tolist(),
                   c=DISCARD_COLOR, s=12, alpha=0.5, zorder=2, label="Discarded")

    # Baseline — hollow dot
    if not base.empty:
        ax.scatter(base.index.tolist(), base["score"].tolist(),
                   c="white", s=40, zorder=3, edgecolors="#888888",
                   linewidths=1, label="Baseline")

    # Kept — green dots
    if not kept.empty:
        ax.scatter(kept.index.tolist(), kept["score"].tolist(),
                   c=KEEP_COLOR, s=55, zorder=4,
                   edgecolors="black", linewidths=0.5, label="Kept")

        # Running best step line
        scores = kept["score"].tolist()
        running_best = [max(scores[: i + 1]) for i in range(len(scores))]
        ax.step(kept.index.tolist(), running_best, where="post",
                color=LINE_COLOR, linewidth=2.0, alpha=0.75, zorder=3,
                label="Running best")

        # Annotate each kept point with what changed
        for idx, row in kept.iterrows():
            desc = str(row.get("change_summary", "")).strip()
            if len(desc) > 50:
                desc = desc[:47] + "..."
            if desc:
                ax.annotate(
                    desc, (idx, row["score"]),
                    textcoords="offset points",
                    xytext=(6, 6), fontsize=7.5,
                    color="#1a7a3a", alpha=0.9,
                    rotation=28, ha="left", va="bottom",
                )

    n_total = len(df)
    n_keep  = len(kept)
    n_disc  = len(disc)
    keep_rate = f"{n_keep / (n_keep + n_disc):.0%}" if (n_keep + n_disc) > 0 else "n/a"

    ax.set_title(f"{title}   ({n_total} cycles  |  {n_keep} kept  |  keep rate {keep_rate})",
                 fontsize=10)
    ax.set_xlabel("Cycle #", fontsize=9)
    ax.set_ylabel("Eval Score (higher = better)", fontsize=9)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.2)

    # Annotate baseline on y-axis if we have a first score
    if not df.empty and "score" in df.columns:
        first_score = df["score"].dropna().iloc[0] if not df["score"].dropna().empty else None
        if first_score is not None:
            ax.axhline(first_score, color="#aaaaaa", linestyle="--",
                       linewidth=0.8, alpha=0.6)
            ax.annotate(f"baseline {first_score:.4f}", (0, first_score),
                        textcoords="offset points", xytext=(4, 3),
                        fontsize=7, color="#999999")


def plot_north_star(ax: Any, ns_df: pd.DataFrame) -> None:
    if ns_df.empty or "rate_num" not in ns_df.columns:
        ax.text(0.5, 0.5, "No session data yet",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=11, color="#aaaaaa")
        ax.set_title("North Star: Autonomous Completion Rate", fontsize=10)
        return

    x = list(range(len(ns_df)))
    rate_strs: list[str] = ns_df["rate_num"].astype(str).tolist()
    y: list[float] = [float(s) if s not in ("", "nan", "None", "<NA>") else 0.0
                      for s in rate_strs]

    ax.plot(x, y, marker="o", color="#3498db", linewidth=2, markersize=7, zorder=3)
    ax.fill_between(x, y, alpha=0.15, color="#3498db")
    for xi, yi in zip(x, y):
        ax.annotate(f"{yi:.0f}%", (xi, yi),
                    textcoords="offset points", xytext=(0, 8),
                    fontsize=8, ha="center", color="#2980b9")
    ax.axhline(100, color="#e74c3c", linestyle="--", alpha=0.4, linewidth=1)
    ax.set_ylim(0, 115)
    sessions: list[str] = [ns_df.iloc[i].get("session", f"S{i+1}") for i in range(len(ns_df))]
    ax.set_xticks(x)
    ax.set_xticklabels(sessions, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Completion Rate (%)", fontsize=9)
    ax.set_title("North Star: Autonomous Workflow Completion Rate", fontsize=10)
    ax.grid(True, alpha=0.2)


def plot_friction(ax: Any, ns_df: pd.DataFrame) -> None:
    if ns_df.empty or "friction_events_total" not in ns_df.columns:
        ax.text(0.5, 0.5, "No friction data yet",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=11, color="#aaaaaa")
        ax.set_title("Friction Events per Session (goal: decrease)", fontsize=10)
        return

    x = list(range(len(ns_df)))
    fric_strs: list[str] = ns_df["friction_events_total"].astype(str).tolist()
    y_vals: list[float] = [float(s) if s not in ("", "nan", "None", "<NA>") else 0.0
                           for s in fric_strs]
    ax.bar(x, y_vals, color="#e74c3c", alpha=0.65, zorder=3)
    for xi, yi in zip(x, y_vals):
        ax.text(xi, yi + 0.05, str(int(yi)), ha="center", va="bottom", fontsize=8)
    sessions: list[str] = [ns_df.iloc[i].get("session", f"S{i+1}") for i in range(len(ns_df))]
    ax.set_xticks(x)
    ax.set_xticklabels(sessions, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Total Friction Events", fontsize=9)
    ax.set_title("Friction Events per Session (goal: decrease)", fontsize=10)
    ax.grid(True, alpha=0.2, axis="y")


# ---------------------------------------------------------------------------
# Summary text (like autoresearch summary cells)
# ---------------------------------------------------------------------------

def generate_summary(skill_frames: dict[str, pd.DataFrame],
                     ns_df: pd.DataFrame, date_str: str) -> str:
    lines = [f"# Loop Progress Report — {date_str}", ""]

    # North star
    if not ns_df.empty and "rate_num" in ns_df.columns:
        latest = ns_df.iloc[-1]
        rate = latest.get("rate_num", "?")
        trend = latest.get("trend", "")
        lines += [f"## North Star: {rate}%  (trend: {trend})", ""]

    total_cycles = sum(len(df) for df in skill_frames.values())
    total_kept   = sum(len(df[df["status"] == "KEEP"]) for df in skill_frames.values()
                       if "status" in df.columns)
    lines += [
        f"## Overall: {total_cycles} cycles across {len(skill_frames)} skills, "
        f"{total_kept} kept improvements", ""
    ]

    for skill, df in skill_frames.items():
        if df.empty or "score" not in df.columns:
            continue
        kept = df[df["status"] == "KEEP"]
        disc = df[df["status"] == "DISCARD"]
        scores = df["score"].dropna()
        if scores.empty:
            continue

        baseline = scores.iloc[0]
        best     = kept["score"].max() if not kept.empty else baseline
        delta    = best - baseline

        lines.append(f"### {skill}")
        lines.append(f"- Cycles: {len(df)} total  |  {len(kept)} KEEP  |  {len(disc)} DISCARD")
        lines.append(f"- Baseline: {baseline:.4f}  ->  Best: {best:.4f}  (total improvement: {delta:+.4f})")

        if not kept.empty:
            lines.append("")
            lines.append("**Top improvements by delta:**")
            if len(kept) > 1:
                kept_sorted = kept.copy()
                prev_scores: list[float] = [baseline] + kept_sorted["score"].tolist()[:-1]
                kept_sorted["prev"] = prev_scores
                kept_sorted["delta"] = kept_sorted["score"] - kept_sorted["prev"]
                top = kept_sorted.sort_values(by="delta", ascending=False).head(5)  # type: ignore[call-overload]
            else:
                top = kept.copy()
                top["delta"] = kept["score"] - baseline

            for _, row in top.iterrows():
                d = float(row.get("delta") or 0)
                s = str(row.get("change_summary") or "")
                lines.append(f"  {d:+.4f}  {s}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Agentic OS loop progress report")
    parser.add_argument("--plugin-dir", required=True,
                        help="Path to agent-agentic-os plugin root (contains skills/)")
    parser.add_argument("--project-dir", default=None,
                        help="Path to project root (for improvement-ledger.md)")
    parser.add_argument("--skill", default=None,
                        help="Filter to a single skill name")
    parser.add_argument("--output-dir", default=None,
                        help="Override output directory (default: project-dir/context/memory/reports)")
    args = parser.parse_args()

    plugin_dir  = Path(args.plugin_dir)
    project_dir = Path(args.project_dir) if args.project_dir else plugin_dir.parent
    ledger_path = project_dir / "context" / "memory" / "improvement-ledger.md"

    ts_str   = datetime.now().strftime("%Y%m%d_%H%M")
    date_str = datetime.now().strftime("%Y-%m-%d")

    out_dir = Path(args.output_dir) if args.output_dir else (
        project_dir / "context" / "memory" / "reports"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Load per-skill data from results.tsv files (primary source)
    # ------------------------------------------------------------------
    tsvs = find_results_tsvs(plugin_dir)
    if args.skill:
        tsvs = {k: v for k, v in tsvs.items() if k.lower() == args.skill.lower()}

    skill_frames: dict[str, pd.DataFrame] = {}
    for skill_name, path in tsvs.items():
        df = load_results_tsv(path, skill_name)
        if not df.empty:
            skill_frames[skill_name] = df
            print(f"[os-improvement-report] Loaded {len(df)} rows from {path}")

    if not skill_frames:
        print("[os-improvement-report] No results.tsv data found. "
              "Run at least one eval cycle to populate results.tsv files.")
        print(f"  Looked in: {plugin_dir}/skills/*/evals/results.tsv")
        print("  Generating placeholder chart...")

    # ------------------------------------------------------------------
    # Load north star from improvement ledger (secondary source)
    # ------------------------------------------------------------------
    ns_df = load_north_star(ledger_path)
    if not ns_df.empty:
        print(f"[os-improvement-report] Loaded {len(ns_df)} session rows from ledger")

    # ------------------------------------------------------------------
    # Figure layout — one subplot per skill + north star row
    # ------------------------------------------------------------------
    n_skills  = max(1, len(skill_frames))
    n_rows    = n_skills + 1
    fig       = plt.figure(figsize=(16, 5 * n_rows))
    gs        = gridspec.GridSpec(n_rows, 2, figure=fig, hspace=0.60, wspace=0.35)

    for i, (skill_name, df) in enumerate(sorted(skill_frames.items())):
        ax = fig.add_subplot(gs[i, :])
        plot_skill(ax, df, title=skill_name.replace("-", " ").title())

    if not skill_frames:
        ax = fig.add_subplot(gs[0, :])
        plot_skill(ax, pd.DataFrame(), title="No skill data yet")

    ax_ns = fig.add_subplot(gs[n_rows - 1, 0])
    plot_north_star(ax_ns, ns_df)

    ax_fr = fig.add_subplot(gs[n_rows - 1, 1])
    plot_friction(ax_fr, ns_df)

    total_kept = sum(len(df[df["status"] == "KEEP"])
                     for df in skill_frames.values() if "status" in df.columns)
    total_cycles = sum(len(df) for df in skill_frames.values())

    fig.suptitle(
        f"Agentic OS — Loop Improvement Progress\n"
        f"{total_cycles} cycles  |  {total_kept} kept improvements  |  {date_str}",
        fontsize=14, y=1.01,
    )

    chart_path = out_dir / f"progress_{ts_str}.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[os-improvement-report] Chart saved: {chart_path}")

    # ------------------------------------------------------------------
    # Text summary
    # ------------------------------------------------------------------
    summary = generate_summary(skill_frames, ns_df, date_str)
    summary_path = out_dir / f"summary_{ts_str}.md"
    summary_path.write_text(summary)
    print(f"[os-improvement-report] Summary saved: {summary_path}")
    print()
    print(summary)


if __name__ == "__main__":
    main()
