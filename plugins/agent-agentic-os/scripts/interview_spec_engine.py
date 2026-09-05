#!/usr/bin/env python3
"""
interview_spec_engine.py — Universal Intake & 4-Pillar Spec Engine
==================================================================

Purpose:
    Session-aware intake router and Socratic Defaulting engine for compiling
    standardized 4-Pillar TASK_SPEC.md files across CLI and IDE agent runtimes.

Key Input Dependencies:
    - Session environment variables: CLAUDE_CODE_ENTRY, ANTIGRAVITY_IDE, GITHUB_COPILOT_CLI
    - Standard input / console prompts during interactive fallback sessions

Key Functions:
    - detect_intake_mode() — Detects native vs fallback environment mode
    - format_socratic_question() — Formats 1-3 Socratic questions with recommended defaults
    - render_4pillar_spec() — Compiles 4-pillar specification markdown
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def detect_intake_mode() -> str:
    """
    Detects whether the runtime environment possesses native interactive intake capabilities.
    Checks session environment variables FIRST to avoid false positives from global binaries.
    """
    # 1. Running in GitHub Copilot CLI session or headless loop -> Fallback Socratic
    if os.environ.get("GITHUB_COPILOT_CLI") or os.environ.get("COPILOT_CLI"):
        return "EXECUTE_SOCRATIC_FALLBACK"

    # 2. Claude Code session marker (active Claude runtime)
    if os.environ.get("CLAUDE_CODE_ENTRY") or os.environ.get("CLAUDE_PROJECT_DIR"):
        return "DEFER_CLAUDE_NATIVE"

    # 3. Antigravity IDE session marker
    if os.environ.get("ANTIGRAVITY_IDE") or os.environ.get("ANTIGRAVITY_AGENT"):
        return "DEFER_ANTIGRAVITY"

    # Default fallback for standalone / headless scripts
    return "EXECUTE_SOCRATIC_FALLBACK"


def locate_and_parse_diagnostic_brief(search_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Automatically locates and extracts diagnostic findings from DIAGNOSTIC_BRIEF.md
    emitted by the upstream exploration-cycle-plugin.
    """
    if search_dir is None:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        search_dir = repo_root

    candidates = [
        search_dir / "exploration" / "DIAGNOSTIC_BRIEF.md",
        search_dir / "DIAGNOSTIC_BRIEF.md",
        search_dir / "docs" / "DIAGNOSTIC_BRIEF.md"
    ]
    for c in candidates:
        if c.exists():
            try:
                content = c.read_text(encoding="utf-8")
                return {
                    "path": str(c),
                    "content": content,
                    "has_coupling_surface": "## 1. Coupling Surface" in content,
                    "has_hidden_assumptions": "## 2. Hidden Assumptions" in content,
                    "has_architectural_forks": "## 3. Candidate Architectural Forks" in content,
                }
            except Exception:
                pass
    return None


def format_socratic_question(
    question: str,
    option_a_title: str,
    option_a_rationale: str,
    option_b_title: str,
    option_b_tradeoff: str,
    recommended: str = "A"
) -> str:
    """
    Formats an interrogation turn following the Socratic Defaulting rule:
    1 question at a time with structured options and an explicit recommended default.
    """
    rec_a = " [Recommended]" if recommended == "A" else ""
    rec_b = " [Recommended]" if recommended == "B" else ""
    
    return f"""### {question}

- **Option A{rec_a}:** {option_a_title}  
  *Rationale:* {option_a_rationale}

- **Option B{rec_b}:** {option_b_title}  
  *Tradeoff:* {option_b_tradeoff}
"""


def render_4pillar_spec(
    task_id: str,
    title: str,
    job_objective: str,
    target_subsystems: List[str],
    problem_statement: str,
    user_impact: str,
    guardrails: List[Dict[str, str]],
    definitions_of_done: List[str]
) -> str:
    """
    Renders the standardized markdown representation of the 4-Pillar Specification contract.
    """
    subsystems_md = "\n".join(f"- `{s}`" for s in target_subsystems)
    
    guardrails_rows = "\n".join(
        f"| {g.get('boundary', '')} | {g.get('reason', '')} |"
        for g in guardrails
    )
    
    dod_md = "\n".join(f"- [ ] {d}" for d in definitions_of_done)

    return f"""# TASK SPEC: {title}
**Task ID:** `{task_id}`  
**Status:** DRAFT  

## 1. The Job
- **Objective:** {job_objective}
- **Target Subsystems:**
{subsystems_md}

## 2. The Why (Rationale & Context)
- **Problem Statement:** {problem_statement}
- **User / System Impact:** {user_impact}

## 3. Semantic Guardrails & Operational Reasons
| Guardrail Boundary | Operational Reason ("Why") |
| :--- | :--- |
{guardrails_rows}

## 4. Objective Definition of Done (DoD)
{dod_md}
"""
