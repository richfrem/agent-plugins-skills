#!/usr/bin/env python3
"""
Agent Orchestrator (Core Script)
================================

Purpose:
  Standalone CLI for the agent-orchestrator plugin (~250 lines).
  Handles strategy packet generation, verification, correction, bundling, and scanning.
  Zero external dependencies (uses only stdlib).

Commands:
  scan      -> Check artifacts (spec/plan/tasks)
  packet    -> Generate strategy packet from WP
  verify    -> Check worktree diff against criteria
  correct   -> Generate correction packet (delta)
  bundle    -> Bundle files for review (red team context)
  retro     -> Generate retrospective template
"""

import os
import sys
import argparse
import json
import subprocess
import datetime
from pathlib import Path
from typing import List, Optional

# --- Constants & Templates ---

STRATEGY_TEMPLATE = """# Strategy Packet: {wp_id}

## Objective
{objective}

## Context
- **Spec**: {spec_path}
- **Plan**: {plan_path}

## Implementation Tasks
{tasks}

## Acceptance Criteria
{acceptance_criteria}

## Constraints
1. **NO GIT**: Do not run git commands. All version control is the outer loop's job.
2. **NO DELETIONS**: Do not delete files without explicit instruction.
3. **TESTS**: Run tests to verify your work.

## Handoff Instruction
You are the Inner Loop Agent.
1. Read this packet.
2. implement the changes in the current directory.
3. Verify your work against the Acceptance Criteria.
4. Signal completion when done.
"""

CORRECTION_TEMPLATE = """# Correction Packet: {wp_id} (Iteration {iteration})

## Context
This is a feedback loop from the Outer Loop verification.
Original Packet: {original_packet_path}

## Feedback / Failure Reason
{feedback}

## Required Fixes
{fixes}

## Instructions
1. Apply the fixes to the current worktree.
2. Re-verify against the original Acceptance Criteria.
3. Signal completion.
"""

REVIEW_BUNDLE_HEADER = """# Review Bundle: {title}
**Date**: {date}
**Files**: {file_count}

---
"""

RETRO_TEMPLATE = """# Retrospective: {session_id}
**Date**: {date}

## 1. What went well?
- [ ] 

## 2. What was frustrating / failed?
- [ ] 

## 3. Boy Scout Rule (Fix one thing NOW)
- [ ] Identification:
- [ ] Fix applied:

## 4. Metrics
- WPs completed: 
- Correction loops: 
"""

# --- Helpers ---

def run_command(cmd: List[str], cwd: Optional[Path] = None) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, 
            cwd=str(cwd) if cwd else None,
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e.stderr}", file=sys.stderr)
        return ""

def read_file(path: Path) -> str:
    """Read file content safely."""
    if not path.exists():
        return f"[MISSING] {path}"
    return path.read_text(encoding="utf-8", errors="replace")

# --- Commands ---

def cmd_scan(args):
    """Scan for spec artifacts."""
    root = Path.cwd()
    if args.spec_dir:
        spec_dir = root / args.spec_dir
    else:
        # Try to find a spec dir or assume current is root
        spec_dir = root
    
    required = ["spec.md", "plan.md", "tasks.md"]
    missing = []
    
    print(f"Scanning {spec_dir}...")
    for f in required:
        p = spec_dir / f
        if p.exists():
            print(f"  [OK] {f}")
        else:
            print(f"  [MISSING] {f}")
            missing.append(f)
            
    if missing:
        sys.exit(1)
    else:
        print("All artifacts present. Ready to delegate.")

def cmd_packet(args):
    """Generate strategy packet."""
    wp_id = args.wp
    # In a real implementation, we'd parse tasks.md to get the specific WP details.
    # For this standalone script, we'll placeholder reading tasks.md or specific prompt files.
    # Assuming spec-kitty: tasks/WP-NN.md exists.
    
    task_file = Path(args.spec_dir) / "tasks" / f"{wp_id}.md"
    if not task_file.exists():
        print(f"Error: Prompt file {task_file} not found. Run 'spec-kitty tasks' first.", file=sys.stderr)
        sys.exit(1)
        
    content = task_file.read_text()
    
    # Simple extraction (naive)
    objective = "Execute requirements from prompt file."
    criteria = "See prompt file."
    
    packet = STRATEGY_TEMPLATE.format(
        wp_id=wp_id,
        objective=objective,
        spec_path=f"{args.spec_dir}/spec.md",
        plan_path=f"{args.spec_dir}/plan.md",
        tasks=content, # Embed the full prompt content
        acceptance_criteria=criteria
    )
    out_dir = Path("handoffs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"task_packet_{wp_id}.md"
    out_file.write_text(packet)
    print(f"Packet generated: {out_file}")

def cmd_verify(args):
    """Verify worktree state."""
    print(f"Verifying {args.wp}...")
    
    # 1. Git Status (if git exists)
    diff = run_command(["git", "status", "--short"], cwd=Path(args.worktree) if args.worktree else None)
    if not diff:
        print("[WARNING] No changes detected in worktree.")
    else:
        print(f"Changes detected:\n{diff}")
        
    print("\n[MANUAL CHECK REQUIRED]")
    print(f"Please inspect {args.worktree} against criteria in {args.packet}.")
    print("If pass: commit and move task to done.")
    print("If fail: run 'agent-orchestrator correct ...'")

def cmd_correct(args):
    """Generate correction packet."""
    packet_path = Path(args.packet)
    if not packet_path.exists():
        print(f"Error: Original packet {packet_path} not found.", file=sys.stderr)
        sys.exit(1)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    iteration = args.iteration or "1"
    
    content = CORRECTION_TEMPLATE.format(
        wp_id=args.packet, # Simplified
        iteration=iteration,
        original_packet_path=args.packet,
        feedback=args.feedback,
        fixes="See feedback."
    )
    
    out_file = packet_path.parent / f"correction_packet_{packet_path.stem}_{timestamp}.md"
    out_file.write_text(content)
    print(f"Correction packet generated: {out_file}")

def cmd_bundle(args):
    """Bundle files for review."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Collect files
    files = []
    if args.manifest:
        try:
            m = json.loads(Path(args.manifest).read_text())
            files = m.get("files", [])
        except Exception as e:
            print(f"Error reading manifest: {e}", file=sys.stderr)
            sys.exit(1)
            
    if args.files:
        files.extend(args.files)
        
    # Build content
    out = REVIEW_BUNDLE_HEADER.format(title="Ad-Hoc Review", date=timestamp, file_count=len(files))
    
    for f in files:
        p = Path(f)
        out += f"\n## File: {f}\n"
        if not p.exists():
            out += "[MISSING]\n"
            continue
            
        ext = p.suffix.lstrip(".")
        content = read_file(p)
        out += f"```{ext}\n{content}\n```\n"
        
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out)
    print(f"Bundle created: {out_path}")

def cmd_retro(args):
    """Generate retrospective."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    content = RETRO_TEMPLATE.format(session_id="SESSION", date=timestamp)
    out_dir = Path("retros")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = out_dir / f"retro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_file.write_text(content)
    print(f"Retrospective template created: {out_file}")

# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Agent Orchestrator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Scan
    p_scan = subparsers.add_parser("scan")
    p_scan.add_argument("--spec-dir", help="Path to spec directory")
    
    # Packet
    p_packet = subparsers.add_parser("packet")
    p_packet.add_argument("--wp", required=True, help="Work Package ID (WP-NN)")
    p_packet.add_argument("--spec-dir", required=True, help="Path to spec directory")
    
    # Verify
    p_verify = subparsers.add_parser("verify")
    p_verify.add_argument("--packet", required=True, help="Path to strategy packet")
    p_verify.add_argument("--worktree", help="Path to worktree (optional)")
    
    # Correct
    p_correct = subparsers.add_parser("correct")
    p_correct.add_argument("--packet", required=True, help="Original packet path")
    p_correct.add_argument("--feedback", required=True, help="Feedback / Failure reason")
    p_correct.add_argument("--iteration", help="Iteration number")
    
    # Bundle
    p_bundle = subparsers.add_parser("bundle")
    p_bundle.add_argument("--files", nargs="+", help="List of files to bundle")
    p_bundle.add_argument("--manifest", help="JSON manifest file")
    p_bundle.add_argument("--output", required=True, help="Output markdown file")
    
    # Retro
    p_retro = subparsers.add_parser("retro")
    p_retro.add_argument("--spec-dir", help="Associated spec directory")
    p_retro.add_argument("--output", help="Output file (optional)")
    
    args = parser.parse_args()
    
    if args.command == "scan": cmd_scan(args)
    elif args.command == "packet": cmd_packet(args)
    elif args.command == "verify": cmd_verify(args)
    elif args.command == "correct": cmd_correct(args)
    elif args.command == "bundle": cmd_bundle(args)
    elif args.command == "retro": cmd_retro(args)

if __name__ == "__main__":
    main()
