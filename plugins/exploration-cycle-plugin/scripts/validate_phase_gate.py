#!/usr/bin/env python3
"""
validate_phase_gate.py
=====================================
Purpose:
    Deterministic validator checking if phase-specific output files exist,
    align with the active session, and are free from stubs or placeholders.
"""
import os
import sys
import re
from pathlib import Path

MIN_FILE_SIZE_BYTES = 150
WORD_PLACEHOLDERS = ["TODO", "TBD", "FIXME", "XXX", "PLACEHOLDER"]
PHRASE_PLACEHOLDERS = [
    "fill in later",
    "insert here",
    r"\[needs human input\]",
    r"\[unconfirmed\]"
]

# Compile patterns for case-insensitive checks
word_regex = re.compile(r"\b(" + "|".join(WORD_PLACEHOLDERS) + r")\b", re.IGNORECASE)
phrase_regexes = [re.compile(p, re.IGNORECASE) for p in PHRASE_PLACEHOLDERS]

def load_session_title(dashboard_path: Path) -> str:
    if not dashboard_path.exists():
        return ""
    try:
        content = dashboard_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "Session:" in line:
                title = line.replace("**", "").replace("*", "")
                if ":" in title:
                    title = title.split(":", 1)[1]
                return title.strip()
    except Exception:
        pass
    return ""

def load_session_type(dashboard_path: Path) -> str:
    if not dashboard_path.exists():
        return ""
    try:
        content = dashboard_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "Session Type:" in line:
                sess_type = line.replace("**", "").replace("*", "")
                if ":" in sess_type:
                    sess_type = sess_type.split(":", 1)[1]
                return sess_type.strip()
    except Exception:
        pass
    return ""

def check_file_validity(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, f"File {path.name} is missing."
    if path.stat().st_size < MIN_FILE_SIZE_BYTES:
        return False, f"File {path.name} is too short (less than {MIN_FILE_SIZE_BYTES} bytes)."
        
    try:
        content = path.read_text(encoding="utf-8")
        word_match = word_regex.search(content)
        if word_match:
            return False, f"File {path.name} contains unresolved placeholder: '{word_match.group(0)}'"
        for pattern in phrase_regexes:
            phrase_match = pattern.search(content)
            if phrase_match:
                display_match = phrase_match.group(0)
                return False, f"File {path.name} contains unresolved placeholder: '{display_match}'"
    except Exception as e:
        return False, f"Failed to read file {path.name}: {str(e)}"
        
    return True, ""

def validate_phase(phase: int, project_dir: Path) -> tuple[bool, str]:
    exploration_dir = project_dir / "exploration"
    dashboard_path = exploration_dir / "exploration-dashboard.md"
    plans_dir = exploration_dir / "discovery-plans"
    captures_dir = exploration_dir / "captures"
    handoffs_dir = exploration_dir / "handoffs"
    
    session_title = load_session_title(dashboard_path)
    
    if phase == 1:
        if not plans_dir.exists() or not list(plans_dir.glob("*.md")):
            return False, "No Discovery Plan document found under exploration/discovery-plans/."
        
        latest_plan = sorted(plans_dir.glob("*.md"))[-1]
        ok, err = check_file_validity(latest_plan)
        if not ok:
            return False, err
            
        content = latest_plan.read_text(encoding="utf-8")
        required_headers = ["## Problem Statement", "## Success Criteria", "## Must-Have Requirements"]
        missing = [h for h in required_headers if h not in content]
        if missing:
            return False, f"Discovery Plan is missing sections: {', '.join(missing)}"
            
        return True, f"Phase 1 Validated: Plan {latest_plan.name} is compliant."

    elif phase == 2:
        blueprint = captures_dir / "layout-direction.md"
        blueprint_alt = captures_dir / "document-structure.md"
        
        if blueprint.exists():
            ok, err = check_file_validity(blueprint)
            if not ok:
                return False, err
        elif blueprint_alt.exists():
            ok, err = check_file_validity(blueprint_alt)
            if not ok:
                return False, err
        else:
            return False, "No visual layout or document structure artifact found under exploration/captures/."
            
        return True, "Phase 2 Validated: Visual layout direction is recorded."

    elif phase == 3:
        prototype_dir = exploration_dir / "prototype"
        readme = prototype_dir / "README.md"
        notes = captures_dir / "prototype-notes.md"
        
        # Verify stubs/existences
        ok, err = check_file_validity(readme)
        if not ok:
            return False, f"Prototype README error: {err}"
        ok, err = check_file_validity(notes)
        if not ok:
            return False, f"Prototype observations error: {err}"
            
        # Greenfield check for index.html
        session_type = load_session_type(dashboard_path)
        if "greenfield" in session_type.lower():
            index_html = prototype_dir / "index.html"
            ok, err = check_file_validity(index_html)
            if not ok:
                return False, f"Greenfield prototype index.html error: {err}"
            
        return True, "Phase 3 Validated: Prototype artifacts exist and are semantically complete."

    elif phase == 4:
        handoff = handoffs_dir / "handoff-package.md"
        ok, err = check_file_validity(handoff)
        if not ok:
            return False, err
            
        content = handoff.read_text(encoding="utf-8")
        if "## Risk Assessment" not in content or "**Tier:**" not in content:
            return False, "Handoff package is missing the mandatory TierGate Risk Assessment."
            
        # Verify session title alignment to prevent stale files (containment)
        if session_title:
            clean_title = session_title.replace("**", "").replace("*", "").strip().lower()
            clean_content = content.lower()
            if clean_title not in clean_content:
                return False, f"Handoff package session mismatch. Expected text to contain: '{session_title}'."
            
        return True, "Phase 4 Validated: Handoff package is complete and secure."

    return False, f"Unknown phase: {phase}"

def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python3 validate_phase_gate.py <phase_number>\n")
        sys.exit(2)
        
    try:
        phase = int(sys.argv[1])
    except ValueError:
        sys.stderr.write("Phase number must be an integer.\n")
        sys.exit(2)
        
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    
    success, message = validate_phase(phase, project_dir)
    if success:
        sys.stdout.write(f"SUCCESS: {message}\n")
        sys.exit(0)
    else:
        sys.stderr.write(f"FAILURE: {message}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
