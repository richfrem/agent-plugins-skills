#!/usr/bin/env python
"""
generate_report.py
=====================================

Purpose:
    Generates an HTML report from run_loop.py description optimization logic 
    detailing attempts and pass/fail checklist score matrixes on test cases.

Key Input Dependencies:
    - run_loop_output.json      — JSON execution history logs from the optimizer loop
    - argparse, html, json, sys — Standard library packages for HTML generation and JSON parsing

Layer: Investigate / Synthesis

Usage Examples:
    pythongenerate_report.py run_loop_output.json -o report.html
    cat run_loop_output.json | pythongenerate_report.py -

Supported Object Types:
    Optimizer cycle result JSON metadata.

CLI Arguments:
    input: Path to JSON output from run_loop.py (or - for stdin)
    -o|--output: Output HTML file (default: stdout)
    --skill-name: Skill name to include in output display title

Input Files:
    - Optimizer JSON streams.

Output:
    Visual visual HTML dashboard reporting checkpoints.

Key Functions:
    - generate_html()

Script Dependencies:
    - argparse
    - html
    - json
    - sys
    - Path (pathlib)

Consumed by:
    Human workflow reviews or visual diagnostic audits.
"""

import argparse
import html
import json
import sys
from pathlib import Path


def aggregate_runs(results: list[dict]) -> tuple[int, int]:
    """Compute correct and total validation checks across run samples."""
    correct = 0
    total = 0
    for r in results:
        runs = r.get("runs", 0)
        triggers = r.get("triggers", 0)
        total += runs
        if r.get("should_trigger", True):
            correct += triggers
        else:
            correct += runs - triggers
    return correct, total


def score_class(correct: int, total: int) -> str:
    """Map pass ratios to CSS styling highlights (good, ok, bad)."""
    if total > 0:
        ratio = correct / total
        if ratio >= 0.8:
            return "score-good"
        elif ratio >= 0.5:
            return "score-ok"
    return "score-bad"


def _extract_queries(history: list) -> tuple[list[dict], list[dict]]:
    """Extract unique train and test query info from the first history entry."""
    train_queries: list[dict] = []
    test_queries: list[dict] = []
    if not history:
        return train_queries, test_queries
    first = history[0]
    for r in first.get("train_results", first.get("results", [])):
        train_queries.append({"query": r["query"], "should_trigger": r.get("should_trigger", True)})
    for r in first.get("test_results", []):
        test_queries.append({"query": r["query"], "should_trigger": r.get("should_trigger", True)})
    return train_queries, test_queries


def _generate_html_head(title_prefix: str, refresh_tag: str) -> str:
    """Render the HTML <head> block including styles."""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
""" + refresh_tag + """    <title>""" + title_prefix + """Skill Description Optimization</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Lora:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Lora', Georgia, serif; max-width: 100%; margin: 0 auto; padding: 20px; background: #faf9f5; color: #141413; }
        h1 { font-family: 'Poppins', sans-serif; color: #141413; }
        .explainer { background: white; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #e8e6dc; color: #b0aea5; font-size: 0.875rem; line-height: 1.6; }
        .summary { background: white; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #e8e6dc; }
        .summary p { margin: 5px 0; }
        .best { color: #788c5d; font-weight: bold; }
        .table-container { overflow-x: auto; width: 100%; }
        table { border-collapse: collapse; background: white; border: 1px solid #e8e6dc; border-radius: 6px; font-size: 12px; min-width: 100%; }
        th, td { padding: 8px; text-align: left; border: 1px solid #e8e6dc; white-space: normal; word-wrap: break-word; }
        th { font-family: 'Poppins', sans-serif; background: #141413; color: #faf9f5; font-weight: 500; }
        th.test-col { background: #6a9bcc; }
        th.query-col { min-width: 200px; }
        td.description { font-family: monospace; font-size: 11px; word-wrap: break-word; max-width: 400px; }
        td.result { text-align: center; font-size: 16px; min-width: 40px; }
        td.test-result { background: #f0f6fc; }
        .pass { color: #788c5d; } .fail { color: #c44; }
        .rate { font-size: 9px; color: #b0aea5; display: block; }
        tr:hover { background: #faf9f5; }
        .score { display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }
        .score-good { background: #eef2e8; color: #788c5d; } .score-ok { background: #fef3c7; color: #d97706; } .score-bad { background: #fceaea; color: #c44; }
        .best-row { background: #f5f8f2; }
        th.positive-col { border-bottom: 3px solid #788c5d; } th.negative-col { border-bottom: 3px solid #c44; }
        .legend { font-family: 'Poppins', sans-serif; display: flex; gap: 20px; margin-bottom: 10px; font-size: 13px; align-items: center; }
        .legend-item { display: flex; align-items: center; gap: 6px; }
        .legend-swatch { width: 16px; height: 16px; border-radius: 3px; display: inline-block; }
        .swatch-positive { background: #141413; border-bottom: 3px solid #788c5d; } .swatch-negative { background: #141413; border-bottom: 3px solid #c44; }
        .swatch-test { background: #6a9bcc; } .swatch-train { background: #141413; }
    </style>
</head>
<body>
    <h1>""" + title_prefix + """Skill Description Optimization</h1>
    <div class="explainer">
        <strong>Optimizing your skill's description.</strong> This page updates automatically as Claude tests different versions of your skill's description. Each row is an iteration — a new description attempt. The columns show test queries: green checkmarks mean the skill triggered correctly (or correctly didn't trigger), red crosses mean it got it wrong. The "Train" score shows performance on queries used to improve the description; the "Test" score shows performance on held-out queries the optimizer hasn't seen. When it's done, Claude will apply the best-performing description to your skill.
    </div>
"""


def _generate_table_header(data: dict, train_queries: list, test_queries: list) -> str:
    """Render the summary block, legend, and table <thead>."""
    best_test_score = data.get('best_test_score')
    parts = [f"""
    <div class="summary">
        <p><strong>Original:</strong> {html.escape(data.get('original_description', 'N/A'))}</p>
        <p class="best"><strong>Best:</strong> {html.escape(data.get('best_description', 'N/A'))}</p>
        <p><strong>Best Score:</strong> {data.get('best_score', 'N/A')} {'(test)' if best_test_score else '(train)'}</p>
        <p><strong>Iterations:</strong> {data.get('iterations_run', 0)} | <strong>Train:</strong> {data.get('train_size', '?')} | <strong>Test:</strong> {data.get('test_size', '?')}</p>
    </div>
""",
    """
    <div class="legend">
        <span style="font-weight:600">Query columns:</span>
        <span class="legend-item"><span class="legend-swatch swatch-positive"></span> Should trigger</span>
        <span class="legend-item"><span class="legend-swatch swatch-negative"></span> Should NOT trigger</span>
        <span class="legend-item"><span class="legend-swatch swatch-train"></span> Train</span>
        <span class="legend-item"><span class="legend-swatch swatch-test"></span> Test</span>
    </div>
""",
    """
    <div class="table-container">
    <table>
        <thead>
            <tr>
                <th>Iter</th>
                <th>Train</th>
                <th>Test</th>
                <th class="query-col">Description</th>
"""]
    for qinfo in train_queries:
        polarity = "positive-col" if qinfo["should_trigger"] else "negative-col"
        parts.append(f'                <th class="{polarity}">{html.escape(qinfo["query"])}</th>\n')
    for qinfo in test_queries:
        polarity = "positive-col" if qinfo["should_trigger"] else "negative-col"
        parts.append(f'                <th class="test-col {polarity}">{html.escape(qinfo["query"])}</th>\n')
    parts.append("""            </tr>
        </thead>
        <tbody>
""")
    return "".join(parts)


def _render_query_cells(queries: list, by_query: dict, css_extra: str = "") -> str:
    """Render result <td> cells for a list of queries using a lookup dict."""
    parts = []
    for qinfo in queries:
        r = by_query.get(qinfo["query"], {})
        did_pass = r.get("pass", False)
        triggers = r.get("triggers", 0)
        runs = r.get("runs", 0)
        icon = "\u2713" if did_pass else "\u2717"
        css_class = "pass" if did_pass else "fail"
        td_class = f"result {css_extra} {css_class}".strip()
        parts.append(f'                <td class="{td_class}">{icon}<span class="rate">{triggers}/{runs}</span></td>\n')
    return "".join(parts)


def _generate_table_row(h: dict, train_queries: list, test_queries: list, best_iter: int) -> str:
    """Render a single <tr> for one history entry."""
    iteration = h.get("iteration", "?")
    description = h.get("description", "")
    train_results = h.get("train_results", h.get("results", []))
    test_results = h.get("test_results", [])
    train_by_query = {r["query"]: r for r in train_results}
    test_by_query = {r["query"]: r for r in test_results}
    train_correct, train_runs = aggregate_runs(train_results)
    test_correct, test_runs = aggregate_runs(test_results)
    train_cls = score_class(train_correct, train_runs)
    test_cls = score_class(test_correct, test_runs)
    row_class = "best-row" if iteration == best_iter else ""
    row = (f'            <tr class="{row_class}">\n'
           f'                <td>{iteration}</td>\n'
           f'                <td><span class="score {train_cls}">{train_correct}/{train_runs}</span></td>\n'
           f'                <td><span class="score {test_cls}">{test_correct}/{test_runs}</span></td>\n'
           f'                <td class="description">{html.escape(description)}</td>\n')
    row += _render_query_cells(train_queries, train_by_query)
    row += _render_query_cells(test_queries, test_by_query, css_extra="test-result")
    row += "            </tr>\n"
    return row


def generate_html(data: dict, auto_refresh: bool = False, skill_name: str = "") -> str:
    """Generate HTML report from loop output data."""
    history = data.get("history", [])
    title_prefix = html.escape(skill_name + " \u2014 ") if skill_name else ""
    refresh_tag = '    <meta http-equiv="refresh" content="5">\n' if auto_refresh else ""
    train_queries, test_queries = _extract_queries(history)
    parts = [
        _generate_html_head(title_prefix, refresh_tag),
        _generate_table_header(data, train_queries, test_queries),
    ]
    if test_queries:
        best_iter = max(history, key=lambda h: h.get("test_passed") or 0).get("iteration")
    else:
        best_iter = max(history, key=lambda h: h.get("train_passed", h.get("passed", 0))).get("iteration") if history else -1
    for h in history:
        parts.append(_generate_table_row(h, train_queries, test_queries, best_iter))
    parts.append("""        </tbody>\n    </table>\n    </div>\n</body>\n</html>\n""")
    return "".join(parts)


def main() -> None:
    """CLI entry point: parses optimizer loop JSON details and outputs dashboard HTML page."""
    parser = argparse.ArgumentParser(description="Generate HTML report from run_loop output")
    parser.add_argument("input", help="Path to JSON output from run_loop.py (or - for stdin)")
    parser.add_argument("-o", "--output", default=None, help="Output HTML file (default: stdout)")
    parser.add_argument("--skill-name", default="", help="Skill name to include in the report title")
    args = parser.parse_args()

    if args.input == "-":
        data = json.load(sys.stdin)
    else:
        data = json.loads(Path(args.input).read_text())

    html_output = generate_html(data, skill_name=args.skill_name)

    if args.output:
        Path(args.output).write_text(html_output)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(html_output)


if __name__ == "__main__":
    main()
