---
concept: constants-templates
source: plugin-code
source_file: agent-loops/scripts/agent_orchestrator.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.271718+00:00
cluster: packet
content_hash: f790a46d06ecd24d
---

# --- Constants & Templates ---

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-loops/scripts/agent_orchestrator.py -->
#!/usr/bin/env python
"""
Agent Orchestrator (Core Script)
================================

Purpose:
  Standalone CLI for the agent-orchestrator plugin (~250 lines).
  Handles strategy packet generation, verification, correction, bundling, and scanning.
  Zero external dependencies (uses only stdlib).

Commands:
  packet    -> Generate strategy packet from inputs
  verify    -> Check worktree diff against criteria
  correct   -> Generate correction packet (delta)
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

STRATEGY_TEMPLATE = """# Strategy Packet: {id}

## Objective
{objective}

## Context
{context}

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

CORRECTION_TEMPLATE = """# Correction Packet: {id} (Iteration {iteration})

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

def cmd_packet(args: argparse.Namespace) -> None:
    """Generate strategy packet."""
    packet_id = args.id
    
    # Read context files
    context_str = ""
    if args.context:
        for c in args.context:
            cp = Path(c)
            if cp.exists():
                context_str += f"- **{cp.name}**:\n```\n{cp.read_text()}\n```\n"
            else:
                context_str += f"- **{cp.name}**: [MISSING]\n"
                
    if not context_str:
        context_str = "No additional context provided."
        
    # Read instruction files or string
    tasks_str = args.instructions
    ip = Path(args.instructions)
    if ip.exists():
        tasks_str = ip.read_text()
    
    packet = STRATEGY_TEMPLATE.format(
        id=packet_id,
        objective="Execute the provided instructions.",
        context=context_str,
        tasks=tasks_str,
        acceptance_criteria="See detailed instructions above."
    )
    
    out_dir = Path("handoffs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"task_packet_{packet_id}.md"
    out_file.write_text(packet)
    print(f"Packet generated: {out_file}")

def cmd_verify(args: argparse.Namespace) -> None:
    """Verify worktree state."""
    print(f"Verifying {args.packet}...")
    


*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/orchestrator/references/agent_orchestrator.py -->
#!/usr/bin/env python3
"""
Agent Orchestrator (Core Script)
================================

Purpose:
  Standalone CLI for the agent-orchestrator plugin (~250 lines).
  Handles strategy packet generation, verification, correction, bundling, and scanning.
  Zero external dependencies (uses only stdlib).

Commands:
  packet    -> Generate strategy packet from inputs
  verify    -> Check worktree diff against criteria
  correct   -> Generate correction packet (delta)
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

STRATEGY_TEMPLATE = """# Strategy Packet: {id}

## Objective
{objective}

## Context
{context}

##

*(combined content truncated)*

## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-loops/scripts/agent_orchestrator.py`
- **Indexed:** 2026-04-27T05:21:04.271718+00:00
