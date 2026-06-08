# Exploration Cycle Plugin: Workflow Enforcement & Integration Plan (Revised)

> **For agentic workers:** Use `superpowers:brainstorming` and `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the `exploration-cycle-plugin` runtime to transition from an *advisory* workflow guide to a *programmatically enforced* agentic loop, drawing directly on the structural security and gatekeeping patterns of `obra/superpowers`.

---

## 1. Architectural Decisions & Session Hygiene

### State Authority
* **Runtime Database as Source of Truth:** The SQLite database managed by `state_engine.py` is the absolute source of truth for session status, phase progression, and transaction logs.
* **Dashboard as a Projection:** The file `exploration/exploration-dashboard.md` is a prompt-visible and human-readable projection of the database. All state updates must be processed through database-level transactions, which subsequently rewrite the dashboard Markdown file. The LLM is prohibited from modifying checkboxes in the dashboard without triggering a state transaction check.

### Session Hygiene & Resume Rules
* **Stale Session Detection:** When the orchestrator bootstraps, if `exploration/exploration-dashboard.md` exists and is `In Progress`, the orchestrator must prompt the user: *"You have an active session in progress. Would you like to resume, or archive it and start fresh?"*
* **Archiving Handler:** If a new session is requested, the hook must rename the existing `exploration/` directory to `exploration-archive-YYYYMMDD-HHMMSS/` before initializing a fresh state database.

---

## 2. Upgrade Steps

### Pre-Work: Establish Development Branch

- [ ] **Step 1: Check out a new branch in the repository**

```bash
git checkout -b feat/workflow-enforcement-upgrade
```

---

## Task 1: Create `using-exploration-cycle` Bootstrap Skill

> **Adapted from:** `superpowers/skills/using-superpowers/SKILL.md`
> **Purpose:** Forces the LLM to check the database state and run the workflow before answering any user query.

**Files:**
- Create: `skills/using-exploration-cycle/SKILL.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p skills/using-exploration-cycle
```

- [ ] **Step 2: Write `skills/using-exploration-cycle/SKILL.md`**

Write the following content to `skills/using-exploration-cycle/SKILL.md`:

```markdown
---
name: using-exploration-cycle
description: Use when starting any conversation - establishes how to find and follow the business exploration workflow.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent (via dispatch.py) to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
You are operating with the exploration-cycle-plugin active. 

Before responding to ANY user message (including answering general questions or scoping requests), you MUST verify the state of the active exploration session. If a session is in progress, you DO NOT have a choice: you MUST route execution through the active phase of the exploration-workflow.
</EXTREMELY-IMPORTANT>

## How to Check Session State

Before generating any response:
1. Check if `exploration/exploration-dashboard.md` exists.
2. If it DOES exist:
   - Read the dashboard using the Read tool.
   - Check the `**Status:**` field.
   - If status is `Complete`, the prior session has ended. You may answer normally or offer to start a new exploration.
   - If status is `In Progress` or `TBD`, identify the `**Current Phase:**`.
   - **Immediately yield control to the active phase of the exploration workflow.** Invoke the `exploration-workflow` skill or its child skills. Do NOT answer the user's question directly in freeform prose.
3. If it DOES NOT exist:
   - If the user's message matches any exploration triggers (e.g. "I want to build...", "Let's explore...", "I have an idea...", "start discovery"), you must bootstrap the session.
   - Invoke the `exploration-workflow` skill to initiate Phase 0 intake.

## State Authority

The SQLite state database and programmatic phase artifacts are the absolute state authority. The markdown dashboard is a read-only projection of the database. Do not rely on conversational chat history to assume a phase is complete or that a gate has been passed.
```

---

## Task 2: Refactor `hooks/session_start.py` for Prompt Context Injection

> **Adapted from:** `superpowers/hooks/session-start`
> **SME Translation:** Injects constraints silently without developer jargon.

**Files:**
- Modify: `hooks/session_start.py`
- Modify: `hooks/hooks.json`

- [ ] **Step 1: Rewrite `hooks/session_start.py`**

Refactor `hooks/session_start.py` to write JSON injection output to stdout. The hook must read `skills/using-exploration-cycle/SKILL.md` and inject it wrapped in `<EXTREMELY_IMPORTANT>` tags. Include robust defensive error handling to prevent startup crashes when files are corrupt or missing.

Replace the contents of `hooks/session_start.py` with:

```python
#!/usr/bin/env python3
"""
session_start.py
=====================================
Purpose:
    Hook executed at session start. Injects the bootstrap constraints and 
    active session context directly into the LLM system prompt.
"""
import os
import sys
import json
from pathlib import Path

def main() -> None:
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        plugin_root = Path(__file__).resolve().parents[1]
        
        bootstrap_path = plugin_root / "skills" / "using-exploration-cycle" / "SKILL.md"
        dashboard_path = Path(project_dir) / "exploration" / "exploration-dashboard.md"
        
        bootstrap_content = ""
        if bootstrap_path.exists():
            bootstrap_content = bootstrap_path.read_text(encoding="utf-8")
        else:
            bootstrap_content = "The exploration-cycle-plugin is active. Follow the exploration-workflow."
            
        session_context = f"<EXTREMELY_IMPORTANT>\nYou have the exploration-cycle-plugin installed.\n\n{bootstrap_content}\n"
        
        # Check active dashboard status with defensive parsing
        if dashboard_path.exists():
            try:
                dashboard_content = dashboard_path.read_text(encoding="utf-8")
                lines = dashboard_content.splitlines()
                phase_line = next((line for line in lines if "**Current Phase:**" in line), "**Current Phase:** Phase 1 — Problem Framing")
                status_line = next((line for line in lines if "**Status:**" in line), "**Status:** In Progress")
                
                session_context += "\n## Active Workspace State\n"
                session_context += f"- {phase_line}\n"
                session_context += f"- {status_line}\n"
                session_context += "- An active exploration session is detected on disk. You MUST orient the user around this active session and run the exploration-workflow.\n"
            except Exception:
                session_context += "\n- An active exploration session exists but the dashboard is corrupt or parsing failed.\n"
                
        session_context += "</EXTREMELY_IMPORTANT>"
        
        # Output JSON format consumed by the IDE harnesses
        output_data = {
            "additionalContext": session_context,
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": session_context
            }
        }
        
        # Output as single-line JSON to ensure clean parsing by shell harnesses
        sys.stdout.write(json.dumps(output_data) + "\n")
        sys.stdout.flush()

    except Exception as e:
        # Fallback behavior when injection fails
        sys.stderr.write(f"[exploration-cycle] Warning: SessionStart hook context injection failed: {str(e)}\n")
        sys.exit(0) # Hooks must fail silently to avoid crashing startup

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Update `hooks/hooks.json`**

Ensure `hooks.json` maps `SessionStart` cleanly to the python execution.

Replace the contents of `hooks/hooks.json` with:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py\" || true"
          }
        ]
      }
    ]
  }
}
```

---

## Task 3: Implement Silent Intake Handshake in `exploration-workflow`

> **SME Translation:** No duplicate questioning. Information captured in intake is utilized automatically.

**Files:**
- Modify: `skills/exploration-workflow/SKILL.md`

- [ ] **Step 1: Update Block 1 - Bootstrap logic in `skills/exploration-workflow/SKILL.md`**

Modify `skills/exploration-workflow/SKILL.md` to silently read and parse `exploration/session-brief.md` if `exploration-dashboard.md` does not yet exist.

Replace lines around the bootstrap logic (Block 1) in `skills/exploration-workflow/SKILL.md` with:

```markdown
## Block 1 — Bootstrap (run silently before speaking to the SME)

1. Check for `exploration/exploration-dashboard.md`.
2. **If the file does NOT exist:**
   - Create the `exploration/` directory if it does not already exist.
   - Check if `exploration/session-brief.md` exists.
   - **If session-brief.md EXISTS:**
     - Read the file contents silently.
     - Extract the following fields from the brief (using regex fallback checks for header variations):
       * Project / Session Title (e.g. from Epic/Title lines)
       * Exploration Type (Greenfield / Brownfield / Spike / Analysis)
       * Domain classification
       * Desired output
       * Known constraints and expectations
     - Write the final `exploration/exploration-dashboard.md` using the extracted values. Initialize `**Status:** In Progress` and set `**Current Phase:** Phase 1 — Problem Framing`.
     - Automatically pre-mark non-applicable phases as `- [~] (Skipped)` based on the Session Type.
     - **Skip Beat 1 and Beat 2** entirely since this data is already hydrated. Proceed directly to Block 3 Orientation.
   - **If session-brief.md DOES NOT exist:**
     - **Beat 1 — Name and goal:** Ask:
       > "What are we exploring today? Give it a short name so we can track it — and in a sentence or two, what are you hoping to achieve or solve?"
     - When the SME responds, immediately write a provisional dashboard with `**Session:**` set and `**Session Type:** TBD`.
     - **Beat 2 — Session type:** Suggest a type with a one-sentence rationale:
       > "That sounds like [Type X] — [why]. Does that fit, or would you describe it differently?"
     - Update `**Session Type:**` in the dashboard to the confirmed type.
     - Create an initial task list in the dashboard or session notes.
     - Pre-mark non-applicable phases as `- [~] (Skipped)`.
   - Write the final dashboard, then proceed to Block 3.
3. **If the file EXISTS:** Proceed to Block 2.
```

---

## Task 4: Implement Orchestrator Handoff Authorization

> **Purpose:** Prevents child skills from immediately redirecting back to the orchestrator when legitimately invoked.

**Files:**
- Modify: `skills/exploration-workflow/SKILL.md`
- Modify: `skills/discovery-planning/SKILL.md`
- Modify: `skills/visual-companion/SKILL.md`
- Modify: `skills/subagent-driven-prototyping/SKILL.md`
- Modify: `skills/exploration-handoff/SKILL.md`

- [ ] **Step 1: Update routing dispatch block in `exploration-workflow/SKILL.md`**

Ensure that when routing to child skills, the orchestrator passes a strict `<ORCHESTRATOR_DISPATCH>` context block containing authorization parameters.

Update `exploration-workflow/SKILL.md` Block 4 dispatch block to read:

```markdown
When invoking a child skill, pass this structured context block — do NOT bury it in prose:

```
## Session Context (from orchestrator — read and act on before proceeding)
<ORCHESTRATOR_DISPATCH session_id="[session-id-uuid]" phase_number="[N]" phase_name="[phase-name]" strategy="[dispatch-strategy]" expected_output="[path/to/artifact]" return_required="yes">
- Authorized Skill: [child-skill name, e.g. discovery-planning]
- Session type: [exact value from **Session Type:** in dashboard]
- Active phase: Phase [N] — [phase name]
- Discovery Plan: [path to most recent discovery-plan-*.md, or "not yet written"]
- Current task slice: [the current planned work items for this phase]
- Return signal: When this phase is complete, announce "PHASE [N] COMPLETE" then invoke the exploration-workflow skill to continue.
</ORCHESTRATOR_DISPATCH>
```
```

- [ ] **Step 2: Update Dashboard Intercept in child skills**

Update the dashboard intercept logic in `skills/discovery-planning/SKILL.md`, `skills/visual-companion/SKILL.md`, `skills/subagent-driven-prototyping/SKILL.md`, and `skills/exploration-handoff/SKILL.md` to check for this token.

Replace the Dashboard Intercept section in those files with:

```markdown
## Dashboard Intercept

Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

- **If the file EXISTS:**
  - Read the file and check the status. If status is `Complete`, proceed standalone.
  - If status is `In Progress` or `TBD`:
    - **Check for the presence of the `<ORCHESTRATOR_DISPATCH>` tag in the immediate context.**
    - If the tag is PRESENT:
      - Extract and verify `authorized_skill`, `phase_number`, and `expected_output`.
      - If `authorized_skill` matches [this-skill-name] AND `phase_number` matches the dashboard phase:
        - Proceed with this skill's logic. (You are authorized by the orchestrator).
        - **IMPORTANT:** Clear this dispatch block from memory immediately after completing your initial turn to prevent reuse.
      - If verification fails (mismatched name or stale phase):
        - Stop immediately. Announce: *"Orchestrator dispatch verification failed. Returning to dashboard."*
        - Return control. Invoke skill: `exploration-workflow`. Stop generating output.
    - If the tag is ABSENT or malformed:
      - Stop immediately. Do not continue.
      - Announce: *"It looks like you have an active Exploration Session. Let me take you back to your session dashboard."*
      - Return control to the orchestrator. Invoke skill: `exploration-workflow`. Stop generating output from this skill.
- **If the file DOES NOT exist:** Proceed standalone.
```

---

## Task 5: Implement Inline Agent Prompt Hydration for Direct Strategy

> **Purpose:** Forces the main model to emulate specialized agent instructions in direct mode without context pollution.

**Files:**
- Modify: `skills/exploration-workflow/SKILL.md`

- [ ] **Step 1: Add direct-mode hydration guidelines to `exploration-workflow/SKILL.md`**

Add a section detailing the direct-mode dispatch behavior in Block 4 of `skills/exploration-workflow/SKILL.md`.

Insert in `skills/exploration-workflow/SKILL.md` (after the phase routing table):

```markdown
### Direct Mode Agent Prompt Hydration (Degraded Fallback Mode)

When the dashboard records `**Dispatch Strategy: direct**`, you do not have CLI-level subagent spawning capabilities. To prevent role contamination and context pollution:

1. Identify the sub-agent required for the current phase task (e.g., `requirements-doc-agent.md`).
2. Read the prompt file using the `Read` tool.
3. Explicitly wrap the sub-agent task turn inside execution boundaries:
   ```
   BEGIN AGENT EXECUTION: [Agent Name]
   [Paste Agent Prompt Instructions & Rules Here]
   ---
   Task Context: [Provide current files/artifacts]
   Task Instruction: [Provide specific task slice]
   ```
4. Execute the generation and immediately write the output to `exploration/captures/` or the designated path.
5. Upon writing the output, output the cleanup marker:
   ```
   END AGENT EXECUTION: [Agent Name]
   ```
6. **Persona Purge:** Immediately clear the agent persona from your current reasoning thread. Announce: *"Execution complete. Returning to Exploration Orchestrator role."* Resume the standard orchestrator behavior.
```

---

## Task 6: Create `scripts/validate_phase_gate.py` and Integrate into State Engine

> **Purpose:** Replaces soft prose gates with a semantic-aware programmatic validation check.

**Files:**
- Create: `scripts/validate_phase_gate.py`
- Modify: `skills/exploration-workflow/SKILL.md`

- [ ] **Step 1: Write `scripts/validate_phase_gate.py`**

Write a Python script that programmatically validates the workspace files for each phase. Check minimum sizes and scan for placeholder stubs.

Write to `scripts/validate_phase_gate.py`:

```python
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
from pathlib import Path

MIN_FILE_SIZE_BYTES = 150
PLACEHOLDER_WORDS = ["TODO", "TBD", "fill in later", "insert here", "[NEEDS HUMAN INPUT]"]

def load_session_title(dashboard_path: Path) -> str:
    if not dashboard_path.exists():
        return ""
    try:
        content = dashboard_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            if "**Session:**" in line:
                return line.split(":")[-1].strip()
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
        for word in PLACEHOLDER_WORDS:
            if word in content:
                return False, f"File {path.name} contains unresolved placeholder: '{word}'"
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
            
        return True, "Phase 3 Validated: Prototype artifacts exist and are semantically complete."

    elif phase == 4:
        handoff = handoffs_dir / "handoff-package.md"
        ok, err = check_file_validity(handoff)
        if not ok:
            return False, err
            
        content = handoff.read_text(encoding="utf-8")
        if "## Risk Assessment" not in content or "**Tier:**" not in content:
            return False, "Handoff package is missing the mandatory TierGate Risk Assessment."
            
        # Verify session title alignment to prevent stale files
        if session_title and session_title not in content:
            return False, f"Handoff package session mismatch. Expected title: '{session_title}'."
            
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
```

- [ ] **Step 2: Update `skills/exploration-workflow/SKILL.md` to call validation script**

Integrate the validation script into Block 5 (HARD-GATE) of `skills/exploration-workflow/SKILL.md`.

Replace Block 5 (HARD-GATE) in `skills/exploration-workflow/SKILL.md` with:

```markdown
## Block 5 — HARD-GATE (phase completion approval)

`<HARD-GATE>` — This block runs when the child skill signals its phase is done.

1. **Run Programmatic Validation:** Run the phase gate validator script:
   ```bash
   python3 scripts/validate_phase_gate.py [active_phase_number]
   ```
2. **If validation fails:** Stop. Present the validation failure message to the SME. Re-route control to the child skill to fix the missing outputs. Do NOT prompt for approval.
3. **If validation passes:**
   - Present a plain-language summary of what was produced (1–3 bullets).
   - Show the SME the Outcome file path.
   - Ask for explicit approval:
     > "Does everything look right? If you're happy with it, just say the word and I'll mark Phase [N] complete."
4. **Do NOT update the dashboard until the SME gives a clear affirmation.** Accepted responses: "Yes", "Looks good", "Approved", "Go ahead", "That's right", or any equivalent clear confirmation.
5. If the SME requests changes: return control to the child skill, apply changes, then re-present for approval. Repeat until satisfied.
```

---

## Task 6.5: Continuous Enforcement (Turn-by-Turn Guarding)

> **Purpose:** Prevent writing output files out-of-order or updating dashboard phase stubs directly.

**Files:**
- Create: `hooks/pre_write_guard.py` (Planned for Phase 2)

- [ ] **Step 1: Document the Continuous Pre-Write Guard in the code comments and architecture**

Add `pre_write_guard.py` under the `hooks/` directory as a placeholder configuration, noting that on the next iteration (Phase 2), this will execute before tool usage to block out-of-order file writes if phase gates aren't met in the SQLite state database.

---

## Task 7: Comprehensive Behavioral Verification Matrix

- [ ] **Step 1: Execute verification testing for all 9 core scenarios**

Configure and run manual tests using the active harness, recording outcomes in a test report matrix:

1. **Scenario 1 (No Dashboard + Trigger):** Send "I have an idea I want to explore" to a clean session. Verify the `exploration-workflow` boots.
2. **Scenario 2 (Dashboard active + Normal message):** Send "what is the deadline?" mid-session. Verify the agent resumes workflow routing instead of answering directly.
3. **Scenario 3 (Direct child-skill invocation):** Invoke `visual-companion` directly. Verify it blocks and redirects back to `exploration-workflow`.
4. **Scenario 4 (Authorized child-skill invocation):** Invoke `visual-companion` with a valid `<ORCHESTRATOR_DISPATCH>` tag. Verify it executes successfully.
5. **Scenario 5 (Malformed dispatch token):** Invoke child skill with modified phase numbers. Verify it rejects and redirects.
6. **Scenario 6 (Silent brief hydration):** Pre-populate `exploration/session-brief.md`. Boot the workflow. Verify the dashboard hydrates silently without asking Epic/Domain questions.
7. **Scenario 7 (Validator fail):** Call validation with empty stubs or "TODO" files. Verify validation returns exit code `1` and prevents phase progression.
8. **Scenario 8 (Direct-mode isolation):** Emulate `requirements-doc-agent` in direct mode. Verify the persona is purged and the system switches back to orchestrator upon `END AGENT EXECUTION` write.
9. **Scenario 9 (Stale session artifacts):** Check validator behaves correctly if files mismatch session title references.
