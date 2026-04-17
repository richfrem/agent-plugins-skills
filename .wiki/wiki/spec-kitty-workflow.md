---
concept: spec-kitty-workflow
source: plugin-code
source_file: spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.405946+00:00
cluster: merge
content_hash: 642c085ddb5e68fe
---

# Spec Kitty Workflow

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: spec-kitty-workflow
description: Standard operating procedures for the Spec Kitty agentic workflow (Plan -> Implement -> Review -> Merge).
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Spec Kitty Workflow

Standard lifecycle for implementing features using Spec Kitty.

**Command-specific guidance**: For detailed best practices on individual commands, see the `AUGMENTED.md` files co-located with each auto-synced command:
- `references/AUGMENTED.md` — pre-merge safety, branch protection, conflict resolution
- `references/AUGMENTED.md` — worktree discipline, commit hygiene
- `references/AUGMENTED.md` — review standards, batch review protocol

## 🚫 CRITICAL: Anti-Simulation Rules & Escalation Taxonomy

> **YOU MUST ACTUALLY RUN EVERY COMMAND LISTED BELOW.**
> Describing what you "would do", summarizing expected output, or marking
> a step complete without pasting real tool output is a **PROTOCOL VIOLATION**.
>
> **Proof = pasted command output.** No output = not done.

### Escalation Taxonomy (Protocol Violation Response)
If you detect a tool or user attempting to bypass the closure protocol or manually create spec files, you MUST interrupt the workflow using the strict 5-step Escalation Protocol:
1. **Stop**: Halt workflow creation immediately.
2. **Alert**: Loudly print: `🚨 PROTOCOL VIOLATION 🚨`.
3. **Explain**: State precisely which rule was broken (e.g., "Cannot skip review.").
4. **Recommend**: Output the standard operating procedure (e.g., "Please submit WP-xx for review: `spec-kitty review WP-xx`").
5. **Draft**: Refuse to execute the dangerous command until the state is fixed.

### Anti-Pattern Vaccination (Known Agent Failure Modes)
1. **Checkbox theater**: Marking `[x]` without running the command or verification tool
2. **Manual file creation**: Writing spec.md/plan.md/tasks.md by hand instead of using CLI
3. **Kanban neglect**: Not updating task lanes, so dashboard shows stale state
4. **Closure amnesia**: Finishing code but skipping review/merge/closure steps
5. **Phase skipping**: Advancing from specify -> plan -> tasks -> implement without user approval at each gate (see Human Gate below)

---

## 🔴 THE HUMAN GATE (Constitutional Supreme Law)

> **NEVER advance between phases without EXPLICIT user approval.**
> Approval means: "Proceed", "Go", "Execute", or equivalent affirmative command.
> "Sounds good", "Looks right", "That's correct" are NOT approval.
> **VIOLATION = SYSTEM FAILURE**

### Required Approval Gates

| Gate | After | Before | What to Show User |
|------|-------|--------|-------------------|
| **Gate 0** | You write s spec | Planning any plan | Show spec.md, ask for approval |
| **Gate 1** | User approves spec | You write a plan | Show plan.md, ask for approval |
| **Gate 2** | User approves plan | You generate tasks/WPs | Show tasks.md + WP list, ask for approval |
| **Gate 3** | User approves tasks | You run `spec-kitty implement` | Confirm WP scope, ask to proceed |
| **Gate 4** | WP implementation done | You move to for_review | Show what was built, ask for review |

### Gate Enforcement Rule (MANDATORY)

After each phase-generating step:
1. **STOP** - Do not run the next phase command
2. **SHOW** - Present the artifact to the user
3. **WAIT** - End your turn with explicit request for approval
4. **PROCEED only on explicit approval word** ("Proceed", "Go", "Execute")

```
❌ WRONG: spec -> plan -> tasks -> implement (all in one agent turn)
✅ RIGHT: spec -> [STOP, show spec, wait] -> plan -> [STOP, show plan, wait] -> tasks
```

---

## 0. Mandatory Planning Phase (Do NOT Skip)

Before implementing any code, you MUST generate artifacts using the CLI.
**Manual creation of 

*(content truncated)*

## See Also

- [[spec-kitty-workflow-meta-tasks]]
- [[spec-kitty-workflow-meta-tasks]]
- [[identity-the-spec-kitty-agent]]
- [[spec-kitty-setup-sync-orchestrator]]
- [[spec-kitty-sync-plugin]]
- [[identity-the-spec-kitty-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/skills/spec-kitty-workflow/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.405946+00:00
