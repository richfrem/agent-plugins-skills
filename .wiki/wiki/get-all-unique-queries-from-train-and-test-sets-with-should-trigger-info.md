---
concept: get-all-unique-queries-from-train-and-test-sets-with-should-trigger-info
source: plugin-code
source_file: agent-scaffolders/scripts/benchmarking/generate_report.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.208486+00:00
cluster: html
content_hash: ce0e549fc799ed1f
---

# Get all unique queries from train and test sets, with should_trigger info

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/benchmarking/generate_report.py -->
#!/usr/bin/env python
"""
generate_report.py (CLI)
=====================================

Purpose:
    Generate an HTML report from run_loop.py output showing description optimization attempts.
    Takes the JSON output from run_loop.py and generates a visual HTML report
    showing each description attempt with check/x for each test case.

Layer: Meta-Execution

Usage Examples:
    python generate_report.py run_loop_output.json -o report.html

Supported Object Types:
    - JSON outputs from continuous skill description runner (run_loop.py)

CLI Arguments:
    input: Path to JSON output from run_loop.py (or - for stdin)
    -o/--output: Output HTML file path
    --skill-name: Name of the skill to include in title

Input Files:
    - run_loop_output.json

Output:
    - HTML dashboard report

Key Functions:
    - generate_html(): Generate visual dashboard table with pass/fail metrics.

Script Dependencies:
    - argparse, html, json, sys, pathlib

Consumed by:
    - User (CLI)
    - Continuous skill optimizer

Credits:
    Inspired by and adapted from Anthropic's skill-creator.
"""

import argparse
import html
import json
import sys
from pathlib import Path


def generate_html(data: dict, auto_refresh: bool = False, skill_name: str = "") -> str:
    """Generate HTML report from loop output data. If auto_refresh is True, adds a meta refresh tag."""
    history = data.get("history", [])
    holdout = data.get("holdout", 0)
    title_prefix = html.escape(skill_name + " \u2014 ") if skill_name else ""

    # Get all unique queries from train and test sets, with should_trigger info
    train_queries: list[dict] = []
    test_queries: list[dict] = []
    if history:
        for r in history[0].get("train_results", history[0].get("results", [])):
            train_queries.append({"query": r["query"], "should_trigger": r.get("should_trigger", True)})
        if history[0].get("test_results"):
            for r in history[0].get("test_results", []):
                test_queries.append({"query": r["query"], "should_trigger": r.get("should_trigger", True)})

    refresh_tag = '    <meta http-equiv="refresh" content="5">\n' if auto_refresh else ""

    html_parts = ["""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
""" + refresh_tag + """    <title>""" + title_prefix + """Skill Description Optimization</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600&family=Lora:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Lora', Georgia, serif;
            max-width: 100%;
            margin: 0 auto;
            padding: 20px;
            background: #faf9f5;
            color: #141413;
        }
        h1 { font-family: 'Poppins', sans-serif; color: #141413; }
        .explainer {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #e8e6dc;
            color: #b0aea5;
            font-size: 0.875rem;
            line-height: 1.6;
        }
        .summary {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border: 1px solid #e8e6dc;
        }
        .summary p { margin: 5px 0; }
        .best { color: #788c5d; font-weight: bold; }
        .table-container {
            overflow-x: auto;
            width: 100%;
        }
        table {
            border-collapse: collapse;
            background: white;
            border: 1px solid #e8e6dc;
            border-radius: 6px;
            font-size: 12px;
            min-width: 100%;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #e8e6dc;
            white-space: normal;
            word-wrap: break-word;
        }
        t

*(content truncated)*

<!-- Source: plugin-code/agent-scaffolders/scripts/generate_report.py -->
#!/usr/bin/env python
"""
generate_report.py
=====================================

Purpose:
    Generates an HTML report from run_loop.py description optimization logic 
    detailing attempts and pass/fail checklist score matrixes on test cases.

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
    -

*(combined content truncated)*

## See Also

- [[load-and-validate-eval-results-data-from-tsv]]
- [[prefer-remaining-broken-linksjson-post-fix-output-from-step-4-if-present-and]]
- [[separate-by-should-trigger]]
- [[1-basic-summarize-all-documents]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/benchmarking/generate_report.py`
- **Indexed:** 2026-04-27T05:21:04.208486+00:00
