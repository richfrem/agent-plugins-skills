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

from capability_probe import detect_runtime


def prepare_source_assisted_answers(
    question_ids: List[str],
    sources: List[Dict[str, Any]],
    confirmed_answers: Optional[Dict[str, str]] = None,
    approval_question_ids: Optional[set[str]] = None,
) -> Dict[str, Any]:
    """Return document-derived candidates without treating documents as consent."""
    confirmed = dict(confirmed_answers or {})
    approvals = set(approval_question_ids or set())
    candidates: Dict[str, Dict[str, Any]] = {}
    conflicts: Dict[str, List[str]] = {}
    rejected_authority: Dict[str, str] = {}
    ignored_sources: List[str] = []
    values: Dict[str, List[tuple[str, bool, str]]] = {qid: [] for qid in question_ids}
    for source in sources:
        path = str(source.get("path", "<unknown>"))
        if not source.get("authorized", False):
            ignored_sources.append(path)
            continue
        for qid, answer in (source.get("answers") or {}).items():
            if qid not in values or not str(answer).strip():
                continue
            if qid in approvals:
                rejected_authority[qid] = "document_cannot_grant_approval"
                continue
            values[qid].append((str(answer), bool(source.get("stale", False)), path))
    for qid, entries in values.items():
        if qid in confirmed:
            continue
        unique = {answer for answer, _, _ in entries}
        if len(unique) > 1:
            conflicts[qid] = sorted(unique)
        elif len(unique) == 1:
            answer, stale, path = entries[0]
            candidates[qid] = {"answer": answer, "source": path, "stale": stale,
                               "requires_human_confirmation": True}
    unresolved = [qid for qid in question_ids if qid not in confirmed and qid not in candidates]
    return {"candidates": candidates, "conflicts": conflicts, "unresolved": unresolved,
            "confirmed_answers": confirmed, "ignored_sources": ignored_sources,
            "rejected_authority": rejected_authority}


def review_round_budget(complexity: str, elapsed_minutes: float, reviewer_count: int) -> Dict[str, Any]:
    ceilings = {"QUICK": 5, "STANDARD": 15, "SIGNIFICANT": 30}
    ceiling = ceilings[complexity.upper()]
    return {"ceiling_minutes": ceiling, "scope": "whole_round", "reviewer_count": reviewer_count,
            "status": "partial_timeout" if elapsed_minutes > ceiling else "within_budget"}


def summarize_precompletion_gate(gate: Dict[str, bool]) -> Dict[str, Any]:
    map_debt = any((gate.get("existing_capability_failed_or_bypassed"), gate.get("next_agent_friction_found")))
    summary = "The machine compatibility check found no follow-up action for you."
    if map_debt:
        summary = ("The machine compatibility check recorded map debt for future agents; this is not a request for you to do anything now. "
                   "It means the team should preserve the finding and address it in a later improvement package.")
    return {"machine_gate": {"MAP_DEBT": map_debt}, "user_summary": summary}


def detect_intake_mode() -> str:
    """
    Detects whether the runtime environment possesses native interactive intake capabilities.
    Checks session environment variables FIRST to avoid false positives from global binaries.
    """
    runtime = detect_runtime()

    # Copilot and Codex currently use the governed Socratic/portable path.
    if runtime in {"copilot", "codex", "unknown"}:
        return "EXECUTE_SOCRATIC_FALLBACK"

    if runtime == "claude-code":
        return "DEFER_CLAUDE_NATIVE"

    if runtime == "agy":
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


if __name__ == "__main__":
    print(detect_intake_mode())
