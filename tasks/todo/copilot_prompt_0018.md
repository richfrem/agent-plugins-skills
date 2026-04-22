# Copilot Delegation — Exploration Cycle Plugin Self-Healing Upgrades
# Task: 0018 | Model: claude-sonnet-4.6 | Date: 2026-04-22

You are making targeted improvements to `plugins/exploration-cycle-plugin/` in the
`agent-plugins-skills` monorepo. All paths below are relative to that plugin root unless
stated otherwise. Use the Write tool to write files directly — do not output delimiters.

---

## Workstream A — Fix Model Identifiers (dashes → dots)

All occurrences of `claude-sonnet-4-6` and `claude-opus-4-6` in this plugin must become
`claude-sonnet-4.6` and `claude-opus-4.6` respectively (dot separates major.minor).
This is the correct GitHub Copilot CLI model identifier — dashes cause "model not available".

Files to fix:
- `skills/exploration-workflow/SKILL.md`: lines containing `claude-sonnet-4-6` and `claude-opus-4-6`
- `references/dispatch-strategies.md`: model names in the Strategy Selection table and examples

In `skills/exploration-workflow/SKILL.md`, find and replace:
  `claude-sonnet-4-6` → `claude-sonnet-4.6`
  `claude-opus-4-6` → `claude-opus-4.6`

In `references/dispatch-strategies.md`, find and replace:
  `claude-sonnet-4-6` → `claude-sonnet-4.6`
  `claude-opus-4-6` → `claude-opus-4.6`

---

## Workstream B — Add ## Gotchas Sections to Key Skills/Agents

Per the browser-harness self-healing pattern: field-tested failures belong in the artifact
itself, not in external logs. Add a `## Gotchas` section near the end of each file below,
BEFORE the final "Completion" or "Return to Orchestrator" section.

Each Gotchas section should contain 3–5 concrete, field-derived failure patterns specific
to what that skill/agent does. Use this format:

```
## Gotchas

- **[Short title]**: [One sentence describing the failure and how to avoid it.]
```

### B1 — `skills/exploration-workflow/SKILL.md`
Add before the "Completion Block":
```
## Gotchas

- **Malformed checkbox silently mis-routes**: A `- [x]` with no leading space or an asterisk instead of dash will match the wrong phase. Block 2 now explicitly stops on malformed checkboxes — don't skip that check.
- **Skipping dispatch strategy question for Analysis/Docs sessions**: Block 0 correctly skips the dispatch question for Analysis/Docs, but if the session type pivots mid-session (Q4 Intervention Check reveals a software problem was actually a process problem), the dispatch strategy default (`direct`) may not be what the SME wants. Re-ask if the session type changes.
- **Phase routing after kill-session**: Early-exit writes `[~]` to remaining phases but if the write is incomplete (crash, context loss), Block 2 may re-route to a killed phase. Always confirm `**Status:** Complete` is written before announcing completion.
- **Mid-session revision back-pointer**: When a phase is reopened with `- [↩]`, the Outcome file path is cleared to TBD. If the SME later asks "where are my files", they may not find them. Always log the prior file path in the Session Log revision note even when clearing the Outcome field.
- **Tier message mismatch**: If Phase 4 is skipped but a prototype exists, the Completion Block may default to "Tier 3" message. Read the dashboard `**Session Type:**` field first — brownfield self-build completions use the brownfield message, not the tier message.
```

### B2 — `skills/discovery-planning/SKILL.md`
Add before "Completion — Return to Orchestrator":
```
## Gotchas

- **Dashboard intercept ordering**: The dashboard intercept runs before the HARD-GATE check. If the dashboard status field is missing (file corrupted), the intercept will not fire and this skill will run standalone instead of redirecting. Always write `**Status:**` as the first field in a new dashboard.
- **Assumptions Check is not a gate**: The two assumptions questions must not block progress — but agents sometimes treat "I'm not sure" as a blocker. If the SME is unsure, note it as an open question and continue.
- **Legacy/Brownfield track skips Intervention Check**: The Intervention Check is implicit in LQ5. Do NOT re-run Q4 from the Standard Track for brownfield sessions — it will confuse the SME with redundant questions.
- **Discovery Plan date in filename vs content**: The plan file uses `YYYY-MM-DD` in both the filename and the `# Discovery Plan — [Date]` header. If the session spans midnight, these may differ. Use the date when the plan was approved, not when the session started.
- **Spike re-entry loses plan context**: When archiving a prior spike discovery plan (iteration N), ensure the new Phase 1 starts with a brief showing the prior plan path. The SME should not have to re-describe their idea from scratch.
```

### B3 — `skills/exploration-handoff/SKILL.md`
Add before "Anti-Hallucination Rules":
```
## Gotchas

- **TierGate Q5 (bias/people decisions) does not trigger Tier 3 alone**: Q5 "yes" → Tier 2 minimum, plus ethics review. Only combined with Q3 or Q4 "yes" does it escalate to Tier 3. Agents sometimes over-escalate Q5-only cases.
- **Stage 0 runs twice if child skills also run it**: `business-requirements-capture` and `user-story-capture` are invoked in Stage 0 but they also have their own session-type detection. Pass the session type explicitly in the invocation instruction to avoid double-questioning.
- **Reader Testing question 3 is often skipped**: Stage 3 says predict 3 questions — in practice agents predict 1–2 and move on. Enforce all 3 before asking the SME if they're answered.
- **Throwaway path skips Anti-Hallucination Rules**: When the SME selects Throwaway in Stage 1.5, the skill jumps to write a brief handoff. This brief still must not invent content — apply Anti-Hallucination Rules even for the throwaway path.
- **Return to orchestrator after standalone use**: If the dashboard does NOT exist (standalone use), the skill must not attempt to invoke `exploration-workflow`. Check for the dashboard before emitting the return signal.
```

### B4 — `skills/subagent-driven-prototyping/SKILL.md`
Add before "Persona Enforcement":
```
## Gotchas

- **Worktree setup not idempotent**: If `superpowers:using-git-worktrees` was already called by the orchestrator, calling it again creates a nested worktree. Check if a worktree branch already exists before invoking the setup skill.
- **Brownfield build leaves orphaned prototype/ directory**: For brownfield sessions, the actual code changes go into the real codebase but `.md` tracking files go to `exploration/prototype/components/`. If the session is later revisited, these stale `.md` files may describe code that has since been refactored. Mark tracking files with the build date.
- **Agent Plugin Mode detection is order-sensitive**: The Discovery Plan Intervention Type check happens BEFORE Component Decomposition. If the model reads "plugin" in a different context (e.g., "we'll use the WordPress plugin ecosystem"), it may incorrectly trigger Agent Plugin Mode. The trigger condition is "Agent Plugin" or "agentic plugin" as the PRIMARY output type, not any mention of "plugin".
- **plugin.json Binding Check must run before completion, not after**: The check is listed in the Assembly section but agents sometimes defer it to "after the build loop". Run the binding check as part of Agent Plugin Mode assembly, not as a post-completion step.
- **Two-stage review skipped for direct mode**: In `direct` mode the self-review is supposed to run twice (plan alignment + quality). In practice only one pass is done. Explicitly label and separate the two review purposes when self-reviewing.
```

### B5 — `agents/business-rule-audit-agent.md`
Add before the first `<example>` block:
```
## Gotchas

- **Missing `prototype-notes.md` is not an error**: If the optional context is absent, mark ALL rules UNVERIFIED and note the absence. Do not exit, do not hallucinate evidence, do not ask for the file interactively — you are a non-interactive CLI agent.
- **`[NEEDS HUMAN INPUT]` marker format is case- and format-sensitive**: The gap checker counts this exact string. Never write `[needs human input]`, `[NEEDS HUMAN INPUT.]` (with period), or `**[NEEDS HUMAN INPUT]**` (with asterisks). Always use the exact form.
- **Consolidation rule must be enforced even for small audits**: Even if there are only 2 CONTRADICTED rules, they must appear in `## Unresolved Drifts`. Agents sometimes omit the section when the count is low.
- **BR-xxx ID derivation from headings**: When no BR-xxx IDs exist, derive them from section headings (e.g., `BR-AUTH-1`). Use a consistent prefix — do not mix `BR-` and `BRD-` within one audit report.
- **Audit scope is textual only**: Never attempt to grep code, follow file paths, or infer behavior from imports. If the prototype notes reference a file, quote the reference text — do not try to read the actual file.
```

---

## Workstream C — Consistency Fixes

### C1 — Fix TierGate Q5 in `references/hard-gate-enforcement.md`

The Tier 3 Hard Stop section references the old 4-question TierGate. Q5 (people decisions/bias)
was added to the TierGate in `skills/exploration-handoff/SKILL.md`. Update the hard-gate reference.

In the `## Tier 3 Hard Stop — Canonical Redirect` section, find:
```
> "yes" on Q3 (high-privilege access) or Q4 (financial/compliance)
```
Replace with:
```
> "yes" on Q3 (high-privilege access) or Q4 (financial/compliance), or when Q5 (people decisions / bias risk) is "yes" AND combined with any "yes" on Q3 or Q4
```

Also add to the Rules list in that section (after rule 4):
```
5. If Q5 is "yes" but Q3 and Q4 are both "no" — this is Tier 2 minimum (ethics review required), NOT Tier 3. Do not invoke the Tier 3 hard stop for Q5-alone cases.
```

### C2 — Fix intake agent template path in `agents/intake-agent.md`

In Phase 4, find:
```
Read `architecture/templates/exploration-session-brief-template.md`.
```
Replace with:
```
Read `assets/templates/exploration-dashboard.md` for the dashboard structure, then pre-fill
`exploration/session-brief.md` using the intake interview results. (The session-brief template
is not a separate file — derive the brief structure from the intake classification fields
documented in this agent's Output section below.)
```

---

## Workstream D — Add HANDOFF_BLOCK Structured Completion Signals

Child skills signal completion with prose only. Add a machine-readable `## HANDOFF_BLOCK`
code fence to each child skill's completion section, so the orchestrator can parse phase
completion reliably without depending on prose phrasing.

### D1 — `skills/discovery-planning/SKILL.md`
In the "Completion — Return to Orchestrator" section, after the announcement "Your plan is saved — Phase 1 is complete.", add:

```
Output this machine-readable block so the orchestrator can parse phase completion:

~~~
## HANDOFF_BLOCK
PHASE: 1
STATUS: COMPLETE
OUTPUT: exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md
SESSION_TYPE: [value from dashboard or classification]
INTERVENTION_TYPE: [software / process / strategic / legacy-analysis / risk-compliance / spike]
OPEN_QUESTIONS: [count of items in ## Open Questions section]
~~~
```

### D2 — `skills/exploration-handoff/SKILL.md`
In the "Completion — Return to Orchestrator" section, after "Your handoff package is complete — Phase 4 is done.", add:

```
Output this machine-readable block so the orchestrator can parse phase completion:

~~~
## HANDOFF_BLOCK
PHASE: 4
STATUS: COMPLETE
OUTPUT: exploration/handoffs/handoff-package.md
RISK_TIER: [1 / 2 / 3 / Throwaway]
DELIVERY_PATH: [Direct deployment / Security review before deployment / Ethics + security review before deployment / Formal engineering cycle (Opportunity 4) / Session closed — learning preserved]
CONSOLIDATED_GAPS: [count of [NEEDS HUMAN INPUT] markers in handoff]
~~~
```

### D3 — `skills/subagent-driven-prototyping/SKILL.md`
In the "Completion — Return to Orchestrator" section, after "Your prototype is ready — Phase 3 is complete.", change the user-facing instructions and add the block. After the existing instruction for the user to type the confirmation phrase, add:

```
After the user provides the confirmation phrase, output this machine-readable block:

~~~
## HANDOFF_BLOCK
PHASE: 3
STATUS: COMPLETE
OUTPUT: exploration/prototype/index.html
SESSION_TYPE: [Greenfield / Brownfield / Agent Plugin]
COMPONENTS_BUILT: [count]
WORKTREE: [branch name if worktree was created, or "none"]
~~~
```

---

## Workstream E — Domain Patterns Reference Layer

Create a new directory `references/domain-patterns/` with two files.

### E1 — `references/domain-patterns/README.md`

```markdown
# Domain Patterns — Exploration Cycle

Curated library of known failure types and escape strategies for the exploration workflow.
Each file covers one workflow stage and documents mutations that have produced confirmed improvements.

## What domain patterns are

When the exploration-optimizer encounters a failure type it has seen before, it can apply
a proven escape strategy instead of generating a fresh hypothesis from scratch.

## When to read them

Check this directory during any exploration-optimizer run before formulating a hypothesis.
If the current failure type matches a known pattern, apply that pattern's escape first.

## How to contribute a new pattern

1. A novel friction point occurs and resolves in a confirmed improvement.
2. After a **2nd confirmation** on the same failure type, promote to `## Known Patterns`.
3. Include: failure type, root cause, escape steps, and confirmation count.

## File naming convention

`<stage>.md` — named by the exploration stage where the failure occurs:

| File | Covers |
|:-----|:-------|
| `exploration-session.md` | Session type misclassification, HARD-GATE bypasses, premature handoffs |
| `requirements-capture.md` | BRD quality issues, gap marker inconsistencies, coverage failures |
| `prototype-build.md` | Component decomposition failures, brownfield conflicts, plugin-mode detection |
```

### E2 — `references/domain-patterns/exploration-session.md`

```markdown
# Domain Patterns: Exploration Session Failures

Failures observed at the session orchestration level — classification, gate enforcement, and
state management. Use when the exploration-optimizer target is `exploration-workflow` or
`discovery-planning`.

## When to use this file

Check before formulating an improvement hypothesis. Apply the matching escape first.

---

## Known Patterns

### Pattern 1: Session Type Misclassification → Wrong Phase Set

**Failure type:** SME describes a process problem but gets classified as Greenfield, enabling
Phase 3 (prototype build) when the real deliverable is a process change recommendation.

**Root cause:** The scenario routing guide matches on keywords ("workflow", "approval") that
appear in both software and process-change contexts. The Intervention Check (Q4) catches this
but only if it fires correctly.

**Escape:**
- Strengthen the routing guide to check for the explicit signal "existing manual process" vs
  "no process exists yet" — the latter is Greenfield, the former often isn't.
- Add a negative example to `discovery-planning/SKILL.md` showing a process-change scenario
  that LOOKS like Greenfield but routes to Analysis/Docs.
- Ensure the Intervention Check Q4 always fires, even when the routing seems confident.

**Confirmed improvements:** 2+

---

### Pattern 2: HARD-GATE Bypass via "Quick Question" Framing

**Failure type:** SME frames the start of a session as "just a quick question" and the agent
starts capturing requirements without a Discovery Plan in place.

**Root cause:** The HARD-GATE check is a prose instruction. When the user trigger is low-stakes
("quick question", "just wondering"), agents sometimes treat it as a clarification request
rather than a session start and skip the gate.

**Escape:**
- Add trigger phrases "quick question about" and "wondering if" to the negative-example block
  in `exploration-workflow/SKILL.md` — these should route to the gate check, not bypass it.
- Add an explicit check in Block 0: before any capture begins, verify that a Discovery Plan
  exists or that the session is in Bootstrap phase.

**Confirmed improvements:** 3+

---

### Pattern 3: Premature Handoff — Phase 4 Before Phase 3 Artifacts Exist

**Failure type:** Orchestrator routes to Phase 4 (Handoff) before prototype artifacts are
confirmed present, producing a handoff with empty "Prototype Notes" section.

**Root cause:** Block 2 checks for Outcome files for complete phases, but the outcome file
for Phase 3 is `exploration/prototype/index.html` — agents sometimes write only
`exploration/prototype/README.md` and mark Phase 3 complete without `index.html`.

**Escape:**
- Add a Phase 3 completion gate: before marking `[x]`, verify that BOTH `index.html` AND
  `README.md` exist under `exploration/prototype/` for Greenfield sessions.
- For Analysis/Docs and Brownfield-legacy sessions (Phase 3 disabled), this check should be
  skipped — the dashboard `[~]` marker is the authority.

**Confirmed improvements:** 2+

---

## Novel Candidates (awaiting 2nd confirmation)

[Empty — append here when a novel failure is confirmed once]
```

---

## Workstream F — Fill Plugin-Level evals.json With Real Routing Cases

Overwrite `evals/evals.json` with real routing eval cases for this plugin.
The plugin's canonical entry point is `exploration-workflow`. Evals should test whether the
agent correctly invokes it (or a child skill) vs not invoking it at all.

```json
[
  {
    "prompt": "Let's explore this idea I have for a staff scheduling tool.",
    "should_trigger": true
  },
  {
    "prompt": "I have an idea I want to explore — can we start a discovery session?",
    "should_trigger": true
  },
  {
    "prompt": "Where did we leave off with the customer portal exploration?",
    "should_trigger": true
  },
  {
    "prompt": "Let's start an exploration session for a new HR onboarding system.",
    "should_trigger": true
  },
  {
    "prompt": "Resume my exploration from yesterday.",
    "should_trigger": true
  },
  {
    "prompt": "Start a discovery planning session for my onboarding redesign.",
    "should_trigger": true
  },
  {
    "prompt": "I need to explore whether we should build or buy this reporting tool.",
    "should_trigger": true
  },
  {
    "prompt": "Help me think through this business problem — I'm not sure if we need software.",
    "should_trigger": true
  },
  {
    "prompt": "Fix the bug in the authentication service on line 42.",
    "should_trigger": false
  },
  {
    "prompt": "Run the test suite and report the results.",
    "should_trigger": false
  },
  {
    "prompt": "Review my pull request and suggest improvements.",
    "should_trigger": false
  },
  {
    "prompt": "How do I configure the GitHub Actions workflow?",
    "should_trigger": false
  },
  {
    "prompt": "Generate a BRD from the session captures we already have.",
    "should_trigger": false
  },
  {
    "prompt": "Optimise the database query on line 87 in users.py.",
    "should_trigger": false
  }
]
```

---

## Workstream G — dispatch.py: Model Flag + Tier-Aware Sandboxing

Read `scripts/dispatch.py`. Make the following two improvements:

### G1 — Add `--model` flag for Copilot backend

Add a `--model` CLI argument (optional, default None). When `--cli copilot` and `--model` is provided,
append `--model <model>` to the Copilot command.

In the argparse section, add:
```python
parser.add_argument("--model", default=None,
                    help="Model to use (optional). When --cli copilot, appended as '--model <model>'. "
                         "Example: claude-sonnet-4.6")
```

In the command construction for copilot:
```python
else:  # copilot (GitHub Copilot standalone CLI)
    cmd = ["copilot", "-p", full_prompt, args.instruction]
    if args.model:
        cmd = ["copilot", "--model", args.model, "-p", full_prompt, args.instruction]
```

### G2 — Add `--tier` flag for tier-aware sandboxing

Add a `--tier` CLI argument (optional, default `1`, choices `["1", "2", "3"]`).
Only apply `--dangerously-skip-permissions` when tier is `"1"`.

In the argparse section, add:
```python
parser.add_argument("--tier", default="1", choices=["1", "2", "3"],
                    help="Risk tier (1=low, 2=moderate, 3=high). Tier 2/3 require human gate "
                         "before bash-capable dispatch. Only Tier 1 uses --dangerously-skip-permissions. "
                         "Default: 1 (backward compatible).")
```

In the Claude command construction:
```python
if args.cli == "claude":
    cmd = ["claude", "-p", combined_prompt]
    if args.tier == "1":
        cmd.append("--dangerously-skip-permissions")
    else:
        # Tier 2/3: no auto permission bypass — agent runs with standard permissions
        print(f"Info: Tier {args.tier} dispatch — not applying --dangerously-skip-permissions. "
              f"Ensure required tool permissions are granted interactively.", file=sys.stderr)
```

Also update the TODO comment in the code to reflect the fix:
Replace the existing TODO block comment with:
```python
# Security: --dangerously-skip-permissions is only applied for Tier 1 (low risk) dispatches.
# Tier 2/3 workloads run with standard permissions — the caller must ensure required tool
# access is granted before dispatch. See references/architecture.md Rigor Tier table.
```

---

## Workstream H — session_end.py Hook

Create `hooks/session_end.py` and update `hooks/hooks.json`.

### H1 — `hooks/session_end.py`

```python
#!/usr/bin/env python
"""
session_end.py
=====================================

Purpose:
    Detects when an exploration session completes (dashboard Status: Complete)
    and emits a session-complete event to context/events.jsonl for the
    exploration-optimizer to consume as friction signal input.

Layer: Hooks / Triggering

Usage Examples:
    python session_end.py

Script Dependencies:
    - context/kernel.py (for emitting events, optional)

Consumed by:
    - Exploration cycle hooks
"""
import os
import sys
from pathlib import Path


def main() -> None:
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        dashboard_path = Path(project_dir) / "exploration" / "exploration-dashboard.md"
        marker_path = Path(project_dir) / "context" / ".exploration_session_end_marker"

        if not dashboard_path.exists():
            return

        content = dashboard_path.read_text(encoding="utf-8")
        if "**Status:** Complete" not in content:
            return

        # Check if we already emitted for this completion (avoid duplicate events)
        dashboard_mtime = str(int(dashboard_path.stat().st_mtime))
        if marker_path.exists() and marker_path.read_text().strip() == dashboard_mtime:
            return

        # Extract session name from dashboard for the summary
        session_name = "unknown"
        for line in content.splitlines():
            if line.startswith("**Session:**"):
                session_name = line.replace("**Session:**", "").strip()
                break

        summary = f"Exploration session complete: {session_name}"
        kernel_script = Path(project_dir) / "context" / "kernel.py"

        if kernel_script.exists():
            import subprocess
            cmd = [
                sys.executable, str(kernel_script), "emit_event",
                "--agent", "exploration-plugin-hook",
                "--type", "lifecycle",
                "--action", "session-complete",
                "--status", "success",
                "--summary", summary,
            ]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Write marker so we don't re-emit on next hook invocation
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text(dashboard_mtime)

        print(
            f"\n[exploration-cycle] Session complete: {session_name}\n"
            "Friction signal emitted. Run /exploration-optimizer to improve the workflow.\n"
        )

    except Exception:
        pass  # Hooks must fail silently


if __name__ == "__main__":
    main()
```

### H2 — Update `hooks/hooks.json`

Replace the entire file with:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py"
          }
        ]
      }
    ],
    "SessionStop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/session_end.py"
          }
        ]
      }
    ]
  }
}
```

---

## Completion Checklist

After all workstreams are complete, output a summary in this format:

```
## COMPLETION_REPORT
WS-A: [done / partial / skipped] — [one sentence]
WS-B: [done / partial / skipped] — [one sentence]
WS-C: [done / partial / skipped] — [one sentence]
WS-D: [done / partial / skipped] — [one sentence]
WS-E: [done / partial / skipped] — [one sentence]
WS-F: [done / partial / skipped] — [one sentence]
WS-G: [done / partial / skipped] — [one sentence]
WS-H: [done / partial / skipped] — [one sentence]
FILES_CHANGED: [list of all files written]
DEVIATIONS: [any spec deviations — weights changed, definitions shifted, sections renamed, etc.]
```
