
<!-- plugin: agent-agentic-os / adversarial-reasoning-before-agreement-rule -->
---
description: >
  Prevent sycophantic, agreeable, or premature agent responses by requiring adversarial reasoning,
  assumption checks, counterarguments, and explicit risk evaluation before recommendations are accepted.
globs:
  - "*.md"
  - "docs/**/*.md"
  - "plugins/**/*.md"
  - "plugins/**/*.py"
  - "plugins/**/*.ts"
  - "plugins/**/*.tsx"
  - ".agents/**/*.md"
  - ".agent/rules/**/*.md"
---

# Rule: Adversarial Reasoning Before Agreement

## 1. Why This Rule Exists

AI agents have a known sycophancy bias: they tend to validate the user's framing, agree too quickly, and jump into execution without stress-testing assumptions. This leads to premature migrations, hidden coupling, and costly rework.

**A useful agent does not merely execute a proposal—it stress-tests the plan first to make agreement earned.**

---

## 2. The Iron Law

**NO SIGNIFICANT ARCHITECTURE DECISION, SCHEMA DESIGN, CODE REFACTOR, DELETION PLAN, OR MIGRATION PROPOSAL MAY BE ACCEPTED WITHOUT AN ADVERSARIAL PASS FIRST.**

This applies to:
- Architecture, system design, and dependency changes
- Database/schema changes and data persistence refactors
- Plugin, skill, agent instruction, and workflow modifications
- Security boundaries, governance, and permission updates
- Cleanup, file relocation, and deletion plans

It does not apply to:
- Simple factual lookups or documentation clarifications
- Minor typos, formatting, or localized bug fixes with obvious remedies
- Mechanical tasks explicitly constrained by the user

---

## 3. Core Anti-Sycophancy Principles

1. **Agreement Must Be Earned**: Never offer uncritical validation ("Looks great!", "You're totally right!"). If you agree, state *why* while naming the remaining risks or failure modes.
2. **Challenge the Premise**: When presented with a problem framing or proposed solution, evaluate whether the root problem is being solved, or merely a symptom.
3. **Identify Critical Assumptions**: Explicitly call out assumptions that, if invalid, would change the recommendation. Inspect context, code, and tests to verify assumptions before asking the user.
4. **No Cleanup Without Evidence**: Prohibit destructive actions, deletions, or deprecations based on perceived "absorption" or redundancy without verified inventories and user authorization.
5. **Present Viable Alternatives**: For major technical recommendations, articulate at least one credible alternative and explain the explicit tradeoffs of the chosen path.

---

## 4. Evaluation Checklist

Before confirming significant design changes or plans, verify:
- **Assumptions**: What must hold true for this solution to succeed?
- **Failure Modes**: How could this approach fail in production or under edge cases?
- **Missing Elements**: Are tests, migration paths, rollback strategies, or consumer dependencies unaccounted for?
- **Tradeoffs**: What is made more complex or constrained by choosing this design?


<!-- plugin: agent-agentic-os / destructive-action-guard -->
---
name: destructive-action-guard
description: Pre-verification protocol required before any file or skill deletion, bulk cleanup, or stand-in conversion. Prevents data loss from blind cleanup passes and prohibits autonomous skill deletions based on absorption or redundancy rationalizations.
metadata:
  type: feedback
---

# Destructive Action & Skill Deletion Guard

Before deleting files, removing skill directories, bulk-removing stand-ins, or resolving broken references, run the full verification protocol below. **No exceptions.**

---

## Part 1: The Iron Law of Skill Deletions (No Absorption Deletions)

### The Failure Mode
An agent reviews two skills, concludes that skill A's "functionality is covered by" or "has been absorbed into" skill B, then **deletes skill A's directory**. This is always wrong without explicit user instruction naming the exact skill path.

### The Iron Law
**Never delete a skill directory, its SKILL.md, or its evals because you believe the skill is redundant, absorbed, consolidated, or superseded.**

This is a hard gate. No amount of reasoning makes autonomous deletion acceptable.

### Why "Absorption" Is Always a Rationalization
Even when two skills appear to overlap in body content, they are never interchangeable because each skill has three components that are always unique:
1. **Routing identity** — the `trigger:` field and `description:` in frontmatter. Two skills that do similar things still have different routing signatures. Deleting one breaks all prompts that relied on its specific triggers.
2. **Eval contract** — `evals/evals.json` contains `should_trigger` test cases specific to this skill's domain boundary. These cases define where the skill starts and its neighbors end. No other skill has the same eval contract.
3. **Methodology** — the skill body may encode a distinct protocol, phase sequence, or heuristic that the "absorbing" skill does not replicate verbatim, even if the overall goal is similar.

### Skill Deletion Permission Rules
- Adding content or evals to a skill: **Permitted**
- Renaming or moving a skill directory: **Requires explicit confirmation**
- Deleting a skill directory: **HARD GATED — always requires explicit user instruction naming the exact skill path (e.g., "delete `plugins/agent-agentic-os/skills/my-skill`")**
- Deleting a skill because it "looks absorbed" or the user said "clean up redundant skills": **NEVER. General requests like "clean up", "deduplicate", "merge", or "simplify" describe intent, not deletion authorization.**

### Zombie Directory Protocol
A zombie is a skill directory that exists on disk but has no `SKILL.md`.
**Do not delete zombie directories autonomously.**
1. Check `git log -- plugins/<plugin>/skills/<name>/` to see the last known state.
2. Report to user: *"Found zombie directory at `<path>` — no SKILL.md. Last commit: `<sha>`. Restore or delete?"*
3. Wait for explicit instruction.

---

## Part 2: General File Deletion & Stand-in Verification Protocol

### Scope
This verification applies before:
- Deleting any file anywhere in the repository
- Removing stand-in / text-file pointer files
- Bulk cleanup operations (`rm`, `git rm`, script-driven deletion)
- Converting stand-ins to symlinks (targets may have moved)
- "Dead reference" cleanup from consolidation or migration

### Verification Protocol

#### Step 1 — Extract the target from each file
For a single-line text stand-in at path `P` containing relative path `T`:
```bash
cat P  # confirm single line, relative path
```

#### Step 2 — Repo-wide target search
```bash
git ls-files | grep -i "<filename>"
```
- **Target found in repo** → classify as **MISLOCATED_REFERENCE** — do not delete; propose correct path
- **Target not found** → proceed to Step 3

#### Step 3 — Git history check
```bash
git log --all --oneline --full-history -- "**/filename"
```
- **File existed and was recently deleted** → classify as **POSSIBLE_ACCIDENTAL_DELETION** — add to Map Debt; do not delete
- **File only appears in consolidation/migration commits with no subsequent history** → likely safe, classify as **DEAD_CROSS_REPO_REFERENCE**

#### Step 4 — SKILL_ALIAS check (commands/ and agents/)
If content matches `../skills/<name>/SKILL.md` pattern AND the target SKILL.md exists:
- Classify as **SKILL_ALIAS** → convert to symlink via `symlink_manager create`, do not delete

#### Step 5 — Produce audit table before any change
Output this table and wait for explicit confirmation:

| File | Target | Exists in Repo | Classification | Action |
|------|--------|----------------|----------------|--------|

#### Step 6 — Kill switch
**Stop and output the audit table only (no changes)** if any of the following:
- 5+ files classified `POSSIBLE_ACCIDENTAL_DELETION`
- Any ambiguity in target resolution
- Content is multi-line (not a stand-in)
- Target path resolves outside the repo

### Classification → Action Map

| Classification | Action |
|---|---|
| `DEAD_CROSS_REPO_REFERENCE` | Delete |
| `MISLOCATED_REFERENCE` | Propose corrected path; do not modify |
| `POSSIBLE_ACCIDENTAL_DELETION` | Escalate to Map Debt; do not modify |
| `SKILL_ALIAS` | Convert to symlink via `symlink_manager create` |

---

## Why This Rule Exists

The consolidation of repository plugins left pre-consolidation stand-ins with cross-repo paths that never existed post-merge. Blind deletion passes treat MISLOCATED and DEAD references identically — but only DEAD ones are safe to remove. The distinction requires git verification. Similarly, agents routinely rationalize deleting functional skills under the guise of "cleanup" or "absorption". This rule unifies both protections under one strict gate.


<!-- plugin: agent-agentic-os / github-issue-logging-policy -->
---
trigger: always_on
description: Policy and decision matrix governing when and how agent friction events, map debt, and bugs are logged as GitHub issues.
globs: ["**/*"]
---

# GitHub Issue Logging Policy (`github-issue-logging-policy`)

## 1. Purpose & Integration with `self-evolution-policy.md`

This policy governs when and how friction events, execution workarounds, tool failures, and map debt identified during agent runs are logged into GitHub Issues.

It directly extends `self-evolution-policy.md` by defining the decision boundary between in-session fixes, local Map Debt entries (`map-debt.md`), and formal GitHub Issue creation.

---

## 2. Friction Tier Decision Alignment Matrix

Every friction event or failure detected during agent execution must be evaluated against the friction tiers defined in `self-evolution-policy.md`:

| Friction Tier | Condition | Primary Action | GitHub Issue Logging Action | Required Labels |
|---|---|---|---|---|
| **Tier 0 (Quickfix)** | Small friction, fixable inline within allowed edit boundaries in < 5 mins. | Patch inline, update rules/docs ("The Map"). | **Optional**. Log issue only if pattern recurs across sessions. | `type:friction`, `tier:0-quickfix`, `source:agent`, `risk:low` |
| **Tier 1 (Friction / Gap)** | Workaround used, capability missing or awkward, but non-blocking. | Patch inline OR record Map Debt in `map-debt.md`. | **Fix inline or log issue**. If deferred as Map Debt, log issue payload. | `type:friction`, `tier:1-friction`, `source:agent`, `risk:low` |
| **Tier 2 (Failure / Structural)** | Script/tool broken, execution error, or recurring friction. | Collect stack trace & empirical logs. Patch code or log debt. | **Mandatory Issue Logging** (or comment on existing root-cause issue). | `type:bug` or `type:friction`, `tier:2-structural`, `source:agent` |
| **Tier 3 (Regression / Architecture)** | External change, breaking API/selector change, core design flaw. | Collect full evidence bundle & present formal Escalation Template. Synthesized by `repository-improvement`. | **Mandatory Issue Logging + Architecture Review**. | `type:architecture` or `type:bug`, `tier:3-architecture` |

---

## 2.1 Hotspot Synthesis Engine (`repository-improvement`)

For Tier 3 architecture friction and recurring friction clusters identified by `friction_cluster_agent`:
- The **`repository-improvement`** skill consumes cluster hotspot reports and synthesizes proposals for human review. It never creates branches, commits, or PRs itself — see the skill's Human Gate section.
- High-density hotspots are consolidated into architectural refactoring initiatives rather than fragmented single-line patches.

---

## 3. The Root-Cause Consolidation Principle

Before creating any new GitHub issue, the agent MUST perform root-cause consolidation:

> **Root-Cause Question:** *"Is this event itself the root issue, or is it merely one instance/symptom of a broader systemic issue?"*

### Operating Rules for Consolidation:
1. **Deduplication Search**: Run `search-related-issues` (via `gh_issue_search.py`) with title keywords and location labels (`area:*` or `plugin:*`).
2. **Existing Root Cause Found**: If an existing issue covers the root cause, do NOT create a new issue. Instead, use `comment-on-existing-issue` (`gh_issue_comment.py`) to append the new empirical evidence and log context to the open issue.
3. **Symptom vs. Cause**: Never open separate issues for "Script A failed line 10" and "Script B failed line 12" if both failed due to the same missing environment variable or missing helper parameter. Open one consolidated issue capturing the root cause.

---

## 4. Human Suppression Override

Humans retain full override control over automated issue logging.

If a prompt, system instruction, configuration, or issue logging context contains:
```yaml
issue_logging: suppressed
```
or if the user explicitly instructs "do not log issues" / "suppress issue creation":
- **Issue creation and commenting MUST be completely bypassed**.
- Friction events MUST still be recorded locally in `map-debt.md` or logged in the execution context, but no calls to `gh` issue creation scripts shall be executed.

---

## 5. Staged Rollout Stages

To ensure repository stability and prevent issue spam, automated issue logging follows a 4-phase rollout protocol:

- **Phase 1: Payload Generation (Current Default)**
  - All script runs operate in dry-run mode (`execute=False`).
  - Output is formatted as structured JSON payload containing issue title, body, taxonomy labels, and validation status.
  - No live network requests are made to GitHub.
- **Phase 2: Comment Operations**
  - Live commenting (`execute=True`) enabled for adding evidence to existing human-verified issues.
  - New issue creation remains dry-run.
- **Phase 3: Issue Creation**
  - Live issue creation (`execute=True`) enabled for Tier 2 and Tier 3 friction events passing all safety gates.
- **Phase 4: Label & Status Sync**
  - Full bidirectional sync of issue state, status labels, and resolution states.

---

## 6. Mandatory Body Evidence Requirements

Every issue body (whether generated as payload or submitted live) MUST strictly include all 5 markdown sections:

1. `## Summary`: Concise explanation of what failed or caused friction.
2. `## Observed Behavior`: Exact error output, stack trace snippet, or observed unexpected behavior.
3. `## Expected Behavior`: What should have happened according to specifications or rules.
4. `## Evidence`: Command executed, reproduction steps, log locations, or environment details.
5. `## Impact`: Impact on execution, developer flow, or system capabilities (e.g., blocked pipeline, workarounds required).

*Note: The `body_validator.py` script automatically verifies the presence of these 5 sections.*

---

## 7. Task Completion Reporting Rules

When completing a task where friction occurred:
- State whether issue logging was executed or produced dry-run payload.
- Include the issue number (if submitted live) or the dry-run payload summary (if in Phase 1).
- Emit the standard `PRE-COMPLETION GATE` block per `self-evolution-policy.md`.


<!-- plugin: agent-agentic-os / self-evolution-policy -->
---
trigger: always_on
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["**/*"]
---

## Self-Evolution & Self-Healing Policy

**Full context and execution protocol -> `.agent/skills/self-evolution/SKILL.md` (if available)**  
**Skill/directory deletion rules -> `.agent/rules/destructive-action-guard.md` (Part 1)**

Governs responses when any tool call, subprocess, automation step, selector query, script, workflow, or sub-agent encounters failure or friction. Agents must treat failures as evolution events governed by graph state machines (via `agent-orchestration:graph-execution` and `agent-orchestration:select-loop-strategy`) and 3-Layer Filesystem Memory.

---

### The 3 Filesystem Memory Layers

1. **Layer 1: Runtime Context (Lean Procedural Core)**
   - Lean `SKILL.md` files (target <= 100 lines). Loaded strictly on-demand.
   - Raw execution traces and multi-page dossiers are barred during active task execution.
2. **Layer 2: Compounding Wiki Layer (Permanent Knowledge)**
   - Permanent Markdown in `wiki/` and plugin `references/`: playbooks, edge cases, negative constraints, `map-debt.md`, and `evolution-log.md`.
   - **Taxonomy & Confidence Decay:** Entries tagged (`OBSERVED`, `HYPOTHESIS`, `CONFIRMED`, `REJECTED`, `OPEN`). Decays from `CONFIRMED` to `OBSERVED` if unverified for 30 days.
   - **Asymmetric Persistence Rule:** On failure, code mutations roll back, but wiki insights, edge-case findings, and failure logs are NEVER rolled back.
3. **Layer 3: Safe Audit Layer (Append-Only Manifests)**
   - Stored in `.agent/learning/traces/cycle_manifests.jsonl`.
   - Tracked audit log capturing event sequences, hashes, exit codes, and affected paths (no raw terminal text/credentials). Audited via `verify_evolution_receipt.py`.

---

### The 4-Box Automation Gate (Pre-Evolution Qualification)

Before triggering an autonomous self-evolution cycle, all 4 criteria must be satisfied:
1. *Recurring or structural failure?* (Ignore single transient flukes; repeatable errors/gaps qualify).
2. *Objective, programmatic verifier?* (Deterministic test/script returning shell exit code executed directly by controller — never self-reported).
3. *Iteration ceiling?* (Hard limit of max 3 attempts; controller strictly enforces rollback on 3rd failure).
4. *Immutable persistence sink?* (Layer 2 `wiki/` / `map-debt.md` and Layer 3 `cycle_manifests.jsonl` retain learnings regardless of code pass/fail).

---

### Proposal Mode & Verifier Sovereignty Invariants

- **Proposal Mode:** During Stage 1 (`PLAN`), workspace files and configs are strictly read-only. No repo files modified or branches/worktrees spawned until explicit human authorization (`evolution_state.py authorize`).
- **Verifier Sovereignty:** Mutation subject cannot modify the acceptance gate. Immutable base protection set (`evaluate.py`, `eval_runner.py`, tests, holdout sets, baselines, policies) and declared verifiers cannot be targeted for mutation. Pre-execution SHA256 hashes are locked; modifications abort cycle with exit code 2. Verifier command must run directly in isolated worktree.

---

### Hard Gates & Non-Negotiables (always active)

1. **Verify Edit Boundaries First**: Check permitted edit boundaries before making autonomous repairs. Escalate immediately if repairs require edits outside allowed boundaries.
2. **Three-Attempt Maximum**: Max 3 repair attempts. If the 3rd fails, hard stop and present Escalation Template with evidence bundle.
3. **Update The Map, Not Just the Diary**: Every fix must update domain playbooks, rules, or references. Log `Status: RESOLVED` in `map-debt.md` for every Tier 0-3 friction event even when patched immediately. When a fix establishes a new invariant, verification contract, or repeatable architectural constraint, synthesize a confirmed Layer 2 playbook (`wiki/playbook-*.md`) and synchronize `wiki/index.md` via `distill_playbook.py`. Dual-log to `references/evolution-log.md` and `cycle_manifests.jsonl`.
4. **Autonomy & Permission Gates**:
   - **Auto-approved**: New functions/exports, fallback routines/selectors, appending diffs for modified functions.
   - **Confirmation Gated**: Renaming or moving files.
   - **Hard Gated (Requires explicit human permission)**: Deletions of any file, function, skill, rule, manifest, eval, or reference.
   - Composes with `graph-planning-superpowers-policy.md`'s Supreme Law Human Gate.
5. **The Absorption Fallacy - always wrong**: Never conclude an asset is "redundant", "consolidated", or "superseded" and delete it autonomously. Flag overlap; never delete.
6. **One Logical Fix at a Time**: Apply one clean fix per execution pass; never bundle independent repairs.
7. **Fix Forward, Never Skip**: Fix failures at source immediately and update rules/playbooks. Never skip, work around, or add blind retries.
8. **Synchronize Templates on Rule/Strategy Changes**: Update matching templates, generator configs, and prompts when core rules or strategies change.
9. **Refine Prompt Templates on Ingesting Outputs**: Evaluate external model outputs and update prompt templates to guard against observed gaps.
10. **Synchronize Manifests & Reinstall Cleanly on Deletion**: Remove deleted assets from `symlinks.json` and reinstall via `plugin_add.py <plugin-path> -y`.
11. **Pre-Deletion Git History Check**: Run `git log --follow -- <file>` before proposing any file deletion.
12. **Hub First, Spoke Second**: New skill assets must land in plugin root (`plugins/<plugin>/scripts/`, etc.) and symlink into skill folders via `symlink_manager.py`. Run `audit_plugin_structure.py`.
13. **Asymmetric Persistence via Worktree Transfer**: On 3rd attempt failure in isolated worktree, roll back code, but export Layer 2 insights, negative constraints, and debt records to main checkout before worktree teardown.
14. **Evolution Integrity Receipts**: Autonomous evolution commits require a programmatic pre-commit receipt (`EVO-INTEGRITY-<cycle_id>-<hash>`) binding staged tree, verifier exit code, and trace manifest.

---

### Friction-Driven Self-Evolution & Tiers

A self-evolution event is required when a script/eval/tool fails, an existing capability is bypassed/manually replaced, workarounds are used, or repeatable process issues arise. Task success does not waive this.

- **Tier 0 (Friction/Workaround)**: Bypassed capability or used workaround. Patch now + update map + log `Status: RESOLVED` in `map-debt.md` if small/safe; record `Status: OPEN` in `map-debt.md` if unsafe/deferred; escalate if repeated/blocking.
- **Tier 1 (Gap)**: Missing capability (build missing piece).
- **Tier 2 (Failure)**: Existing capability broken/errors (patch minimal code, save logs).
- **Tier 3 (Regression)**: External change broke working behavior (collect evidence, patch primary + fallback).

**No Silent Bypass Rule:** Agents must use intended capabilities. Workarounds are permitted only after recording the failure as a self-evolution event.

---

### Pre-Completion Self-Evolution Gate

Before claiming a task is complete, output this block verbatim:

```
PRE-COMPLETION GATE:
  Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]
  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO - 1 line if YES]
  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO - 1 line if YES]
  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO - 1 line if YES]

If any YES: action taken -> FIX / MAP_DEBT / ESCALATE
```

The block must be emitted as literal text. The task is not complete until every YES has a declared action.

---

### Map Debt Management

If friction cannot be fixed immediately, record it as Map Debt in `<project_root>/references/map-debt.md` (mutable queue, separate from append-only evolution log).

Each entry must include: Logged date (`YYYY-MM-DD`), Cycle/Session ID, Artifact affected, Friction observed, Why not fixed now, Recommended fix, Evidence/repro, Severity (`S`/`M`/`L`), Repeat (`YES`/`NO`), Status (`OPEN`/`RESOLVED`/`ESCALATED`).

- **Aging rule:** If `OPEN` entry is older than 3 execution cycles or 14 days, auto-escalate before starting new work.
- **Repeat = YES:** Must escalate on next encounter — no further deferral permitted.


<!-- plugin: agent-agentic-os / test-driven-development -->
---
description: >
  Enforce Test-Driven Work (TDW) for all new code development (TDD) and orchestration flows (TDO).
  No implementation code is written or orchestration executed before a success contract or failing test exists.
globs:
  - "src/**/*"
  - "tests/**/*"
  - "plugins/**/*"
  - "backend/**/*"
  - "frontend/**/*"
---

# Rule: Test-Driven Work (TDW) — Tests & Contracts Before Execution

## Why This Rule Exists

A silent logic, path resolution, or orchestration contract bug is easily introduced during development or refactoring. Verification contracts written before execution force clarity of intent, define clear success boundaries, and catch bugs before any work is committed.

**Verification contracts written after the work only verify what you remember to check.  
Verification contracts written before the work verify what you actually require.**

---

## The Iron Law

```
NO CODE DEVELOPMENT OR ORCHESTRATION EXECUTION WITHOUT A FAILING TEST OR SUCCESS CONTRACT FIRST.
```

This applies to:
- **Code Development (TDD)**: New service modules, functions, API routes, automation scripts, and bug fixes to any of these.
- **Orchestration & Workflows (TDW/TDO)**: New prompt templates, agent tool execution paths, coordinator scripts, workflow engines, and task runners.

It does NOT apply to:
- Throwaway exploration or prototyping (which must be discarded before the actual implementation begins)
- Static, non-executable configuration files and JSON/YAML data files
- Automatically generated code (migration files, boilerplate, etc.)
- Declarative task checklists or static documents (unless executable)

---

## Mandatory Pre-Execution Step

**Before writing any implementation code or executing any new orchestration flow**, establish the verification contract:

1. **For Code**: Write a failing unit or integration test first.
2. **For Orchestration**: Write a mock evaluation scenario, an assertions list, or an expected output schema validator first.
3. **Skill / Test Tooling**: If the workspace contains a test runner or TDD skill, invoke it before touching code.

This enforces the Red-Green-Refactor cycle and blocks the rationalization patterns ("too simple to test", "I'll do it after") that lead to broken systems. If you start the work before writing the contract, it is invalid. Delete it and start over.

---

## Test Tier Locations

Place tests in the correct tier directory designated for the project. Always locate the project's existing test structure (e.g. `tests/`, `test/`, `spec/`) first and follow its naming patterns. Typical default locations:

| What you're building | Test location | Test file naming |
|---|---|---|
| Pure business logic / services | `/tests/unit/` or `/test/` | `test_<module_name>.py` / `<ModuleName>.spec.ts` |
| API routes / Controllers | `/tests/integration/` or `/tests/api/` | `test_<route_name>_routes.py` / `<RouteName>.spec.ts` |
| UI components | `/tests/ui/` or `/tests/frontend/` | `<ComponentName>.spec.ts` |
| Script automation / CLI tools | `/tests/cli/` or `/tests/` | `test_<script_name>.py` |

---

## What a Passing Test Looks Like

### 1. Pure Function (Deterministic Unit Test)
```python
# WRITE THIS FIRST — watch it fail
def test_calculate_total_with_override():
    result = calculate_total(base_amount=100.0, tax_rate=0.05, discount=10.0)
    assert result == 95.0  # discount applied before tax

# THEN write the implementation in calculations.py
```

### 2. CLI Argument Validation (Integration Test)
```python
# WRITE THIS FIRST
def test_tool_requires_target_argument():
    result = subprocess.run(
        ["python3", "cli_tool.py", "--action", "sync"],
        capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "--target is required" in result.stderr
```

### 3. API Route Test (Backend Server)
```javascript
// WRITE THIS FIRST
describe('POST /api/payment/preflight', () => {
  it('should block transaction when balance is insufficient', async () => {
    const res = await request(app)
      .post('/api/payment/preflight')
      .send({ accountId: '123', amount: 1000.0 });
    expect(res.status).toBe(422);
    expect(res.body.state).toBe('INSUFFICIENT_FUNDS');
  });
});
```

---

## What Counts as a Valid Failing Test

A test only satisfies the TDD requirement if — **before** any implementation is written:
1. The test executes without syntax/runtime compilation errors.
2. The test **fails** for the expected reason (e.g., assertion error, missing function).
3. The failure **proves** the feature or bugfix does not yet exist.

**Invalid examples — these do NOT satisfy TDD:**
```python
assert True  # Trivial — proves nothing
```
```python
with pytest.raises(Exception): ...  # Too broad — does not verify the specific failure cause
```
```python
mock_fn.return_value = expected_value
assert mock_fn() == expected_value  # Tests the mock, not the actual code path
```
```python
@pytest.mark.skip  # Skipped test — does not prove a failure
pass
```

**For bug fixes:** The failing test must reproduce the original bug before the fix is applied. If the test passes before you change anything, it is not a valid TDD cycle.

---

## Critical Runtime Paths — No Mocking Allowed

Certain critical paths must be tested with **real subprocess execution, real file system resolution, and actual I/O** rather than synthetic mocks:

- Script execution wrappers and bridges (e.g., spawning helper scripts or subprocesses)
- File system path resolution logic and directory setup
- File readers and parsers handling external formats
- External API client boundaries

**Do NOT mock these in the primary integration test:**
```python
# FORBIDDEN for critical integration paths:
mock_subprocess_run.return_value = ...
mock_os_path_exists.return_value = True
mock_file_read.return_value = "fake file content"
```

**Reason:** Production bugs are frequently caused by runtime path resolution and formatting anomalies. Mocking these layers hides the bug entirely.

---

## Anti-Patterns — Stop and Start Over

| Pattern | What it produces |
|---|---|
| Writing the function first, then writing a test | Tests that only verify what you built, not what was required |
| Modifying paths or imports without verifying via an import test | Silent import and runtime load failures |
| Refactoring a bridge/helper without an end-to-end integration test | Invisible path or argument mismatch bugs |
| Testing only the happy path | Missed edge cases, poor error handling, and silent crashes |
| Testing via a heavy API when a unit test is more appropriate | Slow test suites that hide where the actual failure lies |
| Testing internal private methods instead of observable behavior | Brittle tests that break during refactoring without protecting against regression |

**Observable behavior is the contract.** Test exit codes, API response structures, JSON schemas, and state transitions—not internal flags, private variables, or cache internals.

---

## Mutation Safety Rule

Any change touching core business logic or security boundaries **must** include a regression test that reproduces the pre-change behavior AND an assertion for the new expected behavior. No existing critical-path test coverage may be reduced. If you refactor a test, the new version must cover at least the same cases.

---

## Prefer Replay Fixtures Over Synthetic Mocks

When capturing external behavior for tests, prefer **recorded real output** over fabricated mocks:
- Captured stdout/stderr logs from tools
- Raw API response payloads (saved as local JSON/YAML fixtures)
- Sample static files and databases

Real captures preserve formatting quirks, character encodings, and edge cases that synthetic mocks routinely miss.

---

## Red Flags — Stop Immediately

If you think any of the following, you are rationalizing. Stop and write the test first:
- *"This is just a quick script, tests would be overkill"*
- *"I'll add tests after I see if this approach works"*
- *"I manually ran it in my terminal and it worked"*
- *"It's just a path change, nothing could break"*
- *"The test is too hard to write before I know the interface"*

The last one especially: if you don't know the interface, write the test that describes **the interface you want**. That IS the design.

---

## Test-Driven Orchestration (TDO) & Prompt-Driven Work — Success Contracts First

For coordinator scripts, workflow engines, master orchestrators, agent prompts, and tool execution flows:
- **Define the Orchestration Contract First**: Before writing any coordination logic or sequencing scripts, write an integration test or schema assertion that verifies parameter propagation between sub-components, execution orders, and error bubbling.
- **Prompt & Output Schema Assertions**: When developing LLM prompts or templates, first define the exact output structure (e.g., JSON schema, markdown headings, or exact tone boundaries). Write validation checks (e.g., matching keys, non-empty outputs, schema compliance) before finalizing the prompt instruction.
- **Safety and Boundary Invariance**: Assert that critical safety boundaries (e.g., user confirmations, budget caps, authorization gates, and data privacy limits) cannot be bypassed by any code path, flag override, or exception handler in the orchestrator.
- **Runnable Integration Scenarios**: Every orchestrated workflow or skill must have a matching runnable evaluation scenario. Mock input fixtures must trigger the flow and verify that the output payload matches expectations in an offline or sandboxed environment.

---

## Related Rules and References

- `.agent/rules/coding-conventions.md` — coding conventions and documentation standards
- `superpowers:test-driven-development` skill (if available) — invoke BEFORE writing any implementation
- `graph-planning-superpowers-policy.md` — test-driven execution and verification discipline

<!-- plugin: agent-agentic-os / worktree-lifecycle-management -->
---
description: Mandatory protocol for creating, reporting on, and closing out git worktrees -- prevents the "where is it" confusion loop caused by collapsing five distinct states into one vague "done".
globs: ["**/*"]
---

# Worktree Lifecycle Management

## The Problem This Rule Solves

Worktree-related changes frequently suffer from ambiguity when multiple git states (uncommitted local work, committed on a branch, pushed to remote, merged to main, local ref updated, and checked out on disk) are collapsed into the vague word "done". This leads to confusion about where files actually reside and whether PRs or branches are safely integrated.

## The Law

> **A worktree-related change is not "done" until you state which of the six states below
> it is actually in, using the exact vocabulary below.** Never use the bare words "done",
> "merged", "pushed", or "saved" without one of these qualifiers attached. When the user
> asks "where is X" or "is it gone", answer with the state name and the exact path/branch,
> not a general reassurance.

## The Six States (use this exact vocabulary)

1. **Written in the worktree** -- exists only as an uncommitted file inside the worktree's
   working directory. Invisible to git log, invisible to any other checkout, lost if the
   worktree is deleted.
2. **Committed in the worktree** -- has a commit hash, but only reachable from the
   worktree's local branch. Invisible outside this machine.
3. **Pushed to origin** -- the branch exists on GitHub. A PR *can* be opened. **Not yet
   merged.** State the exact `git push` result and the PR URL, and say explicitly "not
   merged yet" in the same sentence.
4. **Merged into `origin/main`** -- verify this yourself via `git fetch origin main &&
   git log --oneline origin/main -3` and quote the actual merge commit hash back. Never
   infer this from "I pushed it" or from the user saying "ok" -- confirm the merge commit
   exists on `origin/main` before calling anything merged.
5. **Local branch ref updated** -- `git fetch origin main:main` (or equivalent) updates
   what your local `main` branch *points to*. **This does not change any file on disk if
   the current checkout has a different branch checked out.** Always state explicitly
   which branch is currently checked out (`git branch --show-current`) in the same breath
   as reporting this.
6. **Checked out on disk** -- the actual working directory files match the target branch.
   Verify with `ls`/`git status` on the real path, not by inference. Only at this state can
   you tell the user "you can see it now" -- and even then, name the exact path.

## Non-Negotiables

1. **State the state.** Every progress report on worktree-related work names which of the
   six states applies, e.g. "pushed to origin, PR link below, not yet merged" or "merged
   into origin/main (commit `988b77a`), but your checkout is still on
   `feature/x` -- run `git checkout main` to see it."
2. **Never say "merged" without verifying `origin/main` yourself.** A user saying "I
   merged" is a trigger to `git fetch` and quote the resulting commit hash, not license to
   parrot "merged" back without checking.
3. **Never claim a file is visible "now" without checking the actual checked-out branch.**
   Updating a local branch ref is not the same as changing the working directory. If the
   current checkout is on a different branch than the one just updated, say so before the
   user has to ask why they can't see anything.
4. **State exact full paths for every file/plugin/worktree you reference.** "It's in
   the new plugin" is not an answer; state the exact path (e.g. `/full/path/to/plugins/<plugin>/scripts/script.py`).
5. **Before deleting any worktree, verify state 4 (merged into origin/main) first**, via
   `git fetch` + `git log origin/main`, not by assuming a prior push means the PR was
   merged. Only after that verification, delete via the native worktree-removal tool (or
   `git worktree remove` + `git worktree prune` if the native tool reports no active
   session), and confirm via `git worktree list` that it's gone.
6. **All symlink creation/removal inside a worktree goes through
   `.agents/skills/symlink-manager/scripts/symlink_manager.py`**, per
   `.agent/rules/plugin-architecture-policy.md` Section 5 -- this applies inside worktrees exactly as
   much as the main checkout. If the tool isn't present in the worktree, restore it from
   the marketplace-cached copy or the sibling monorepo before touching any symlink, never
   fall back to raw `ln -s`.
7. **When multiple worktrees exist, or worktree work spans several turns, restate the
   current state of every open worktree at the start of any status report** -- don't make
   the user re-derive it from scattered messages.
8. **Mandatory Post-Implementation Review Stage Gate (`WORKTREE_REVIEW`)**: Once code development
   and automated tests pass inside a worktree, AI agents MUST NEVER autonomously push to origin
   or open a PR. The agent MUST transition the task in `context/control_plane.db` to `WORKTREE_REVIEW`,
   present the diff and summary to the human user, and provide the user the explicit choice between:
   - (A) Running multi-agent adversarial code review (`MULTI_AGENT_CODE_REVIEW`) across independent model perspectives, or
   - (B) Authorizing direct `git push` and PR creation for human review.
9. **Zero Autonomous Push Invariant**: Pushing code to origin without passing through the post-implementation
   review gate and receiving user authorization is an operational violation. Pre-push hooks and
   `agent_control.py update-worktree` will reject any attempt to mark a worktree as `pushed_to_origin`
   unless the task has transitioned through `WORKTREE_REVIEW`.

## Where This Applies

- Every worktree session in the repository.
- Every report to the user about progress on worktree-based work, from creation through final deletion.
- Applies in addition to, not instead of, `worktree-subagent-leak-detection.md` (which covers subagents writing outside assigned worktrees). Both apply simultaneously in any subagent session run inside a worktree.


<!-- plugin: agent-agentic-os / worktree-subagent-leak-detection -->
---
description: A subagent's pwd/git-branch confirmation does not guarantee its Edit/Write calls stay inside the assigned worktree — a mandatory post-task check does. Companion to worktree-lifecycle-management.md, which covers the full worktree lifecycle (create/commit/push/merge/cleanup) this file does not.
globs: ["**/*"]
---

# Worktree/Subagent Isolation (Leak Detection)

**Scope:** This rule covers subagents writing outside their assigned worktree. For the broader lifecycle (creating, verifying, pushing, merging, and cleaning up worktrees), see `worktree-lifecycle-management.md`. Both rules apply simultaneously when subagents execute inside a worktree.

## The Problem This Rule Solves

A subagent's `cd` and `pwd` confirmation at task start only changes its shell state—file editing tools (Edit/Write) resolve absolute file paths independently and can mistakenly write to the main checkout. Treat task-start confirmation as a preliminary check, not a guarantee.

## The Law

> **A `cd`-and-confirm step at task start is not evidence that every subsequent
> Edit/Write call in that session targets the confirmed directory.** `cd` only changes
> the *Bash tool's* persisted shell state — the Edit/Write/Read tools resolve on the
> exact absolute path parameter they're given, independent of any prior `cd`. Treat the
> confirmation step as a cheap first-line check, not a guarantee, and verify the
> **controller's own main checkout** after every task, not just the worktree.

## Non-Negotiables

1. **Every subagent-driven-development dispatch still gets the standard confirmation
   step.** Instruct the subagent to `cd` into the exact worktree path as its first
   action and confirm via `pwd` and `git branch --show-current` before editing anything.
   This remains necessary — it just isn't sufficient on its own.

2. **After every implementer or fix subagent reports back, the controller runs
   `git status --short` in the main checkout (not the worktree) before generating the
   review package.** This is the mandatory second check. It catches a leak within one
   task cycle — while it's still uncommitted and trivially discardable — instead of
   only surfacing at final-merge time, when it's had 5+ more tasks to compound or get
   tangled into review history.

   ```bash
   # From the main repo root, not the worktree:
   git status --short
   ```

   Any unexpected `M` entry that wasn't present before the task's dispatch is a leak.
   Diff it before touching anything (`git diff <path>`) — don't assume.

3. **A leak found this way is virtually always safe to discard, but verify first.**
   The signature of this exact failure mode is: the main checkout's stray diff is an
   *incomplete* or *superseded* subset of work that's already properly committed in the
   worktree branch (e.g. missing a later fix-round commit's changes). If the diff
   content matches that pattern, discard it via `git checkout -- <path>` in the main
   checkout before merging. If the diff contains anything that doesn't look like a
   partial duplicate of the worktree's own committed work — stop and investigate before
   discarding; it may be unrelated, real, uncommitted user work that predates the
   session (check the pre-session `git status` baseline first).

4. **Log a repeat occurrence, don't just re-fix it silently.** Per
   `.agent/rules/self-evolution-policy.md`'s Map Debt register: a `Repeat: YES` entry
   requires action on next encounter, not further deferral. A third occurrence of this
   exact failure mode should prompt investigating the harness-level root cause directly
   (e.g. checking whether a specific tool or dispatch pattern is the common thread)
   rather than only reapplying this same procedural mitigation a third time.

## Where This Applies

- Any `superpowers:subagent-driven-development` or `superpowers:executing-plans`
  session that dispatches implementer/fix subagents into an isolated worktree.
- Applies to every task in a plan, not just the first or last — the leak in the C2
  incident happened during a mid-plan fix round (Task 7's second fix dispatch), not at
  the boundaries.


<!-- plugin: dev-utils / coding-conventions -->
---
trigger: always_on
description: Universal coding conventions for Python, TypeScript, and C#.
globs: ["*.py", "*.ts", "*.js", "*.cs"]
---

## 🎯 PURPOSE: Enable Agents to Understand Code at a Glance

Every script must document **what it does, what it needs, and how to use it** in the first 20 lines.

**Why:** In fresh agent sessions, agents cannot afford to spend 5-10 minutes reading implementations or running exploratory commands. By reading a 20-line header, agents must be able to:
- Understand the script's purpose in 30 seconds
- Know what files/APIs/dependencies it requires
- See usage examples without trial-and-error
- Identify key functions without code diving

This transforms agent onboarding from minutes to seconds.

---

## 📝 Coding Conventions (Summary)

**Full standards → `.agents/skills/coding-conventions-agent/SKILL.md`**

### Non-Negotiables
1. **Dual-layer docs** — external comment above + internal docstring inside every non-trivial function/class.
2. **File headers** — every source file starts with a purpose header (Python, TS/JS, C#).
   - **Crucial**: The header must explicitly list **Key Input Dependencies** (e.g. required configuration files, environment variables, or databases like `config.json` or `schema.sql`).
   - **Index & Preservation Directive**: File headers must contain a complete index list of all functions, methods, and procedures present in the file. Never remove or reduce existing utility documentation (like usage examples, DOM structures, or technical flags lists) during updates—always preserve and enrich.
   - **Purpose**: This enables clean, token-efficient discovery in new agent sessions. Incoming agents can scan the top of a file to instantly map its capabilities and required state files without reading the full implementation.
3. **Type hints** — all Python function signatures use type annotations.
4. **Naming** — `snake_case` (Python), `camelCase` (JS/TS), `PascalCase` (C# public).
5. **Refactor threshold** — split a function when it exceeds **both** a length and a complexity signal, not either alone (revised 2026-09-05, see `references/map-debt.md` DEBT-20260905-08):
   - **Length**: soft warning at 50 lines, hard ceiling at 100 lines (physical line count), regardless of complexity — an overly long function is a readability problem even when flat.
   - **Complexity**: soft warning at McCabe 10, hard ceiling at McCabe 15 (count of `if`/`for`/`while`/`except`/`and`/`or`/`match`-`case` branches + 1).
   - **Structural exemptions from the length ceiling only** (the complexity ceiling still applies): declarative dict/mapping literals, `match`/`case` dispatch blocks, `argparse` `add_argument`/`add_parser` sequences, and large string-template construction (f-strings/`.format()` building multi-section output) — these inflate line count without adding branching logic.
   - **No exemption by subject matter** — a function touching SQLite, state transitions, or any other "transactional" logic is exempt only if its actual branch count clears the complexity ceiling, same as anything else.
6. **Manifest schema** — use simple `{title, description, files}` JSON/YAML format.

### 🔍 Automated Compliance Checks
To audit workspace source code compliance against these rules, run the developer conventions auditor script:
```bash
python3 .agents/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py
```
This utility outputs a detailed audit breakdown under `temp/workspace_conventions_report.md`.

<!-- plugin: dev-utils / git-operations -->
---
description: Rules for safe git operations — what requires explicit approval, what is forbidden, and how to handle push & lockfile conflicts.
globs: ["**/*"]
---

# Git Operations Policy

## Hard Rules (never violate)

### 1. No git stash without explicit instruction
Never run `git stash`, `git stash pop`, or `git stash apply` unless the user explicitly says to.
**Reason:** Stashing risks applying stale edits onto new branches and causing silent regressions.

### 2. Lockfile Conflict Protocol (`skills-lock.json`)
`skills-lock.json` contains machine-generated timestamps. When a branch or PR has conflicts in `skills-lock.json`:
- **NEVER** edit conflict markers by hand (`<<<<<<<`, `=======`, `>>>>>>>`).
- **NEVER** leave a PR in conflict state after pushing.
- **ALWAYS** resolve immediately via:
  ```bash
  git checkout --ours skills-lock.json
  python3 plugins/plugin-manager/scripts/plugin_add.py plugins/ -y
  git add skills-lock.json
  ```

### 3. Pre-Push Freshness & Quality Gate
Before **explicitly pushing** changes to GitHub (i.e., only when the user has issued a direct push command):
1. **Upstream Freshness Check**: Verify the branch is up to date with `origin/main`:
   ```bash
   git fetch origin main
   git merge origin/main
   ```
   If `skills-lock.json` conflicts occur, apply Rule 2 immediately.

2. **Pre-Push Quality Audits (Mandatory)**:
   Run standard compliance, coding conventions, and structural audits on all modified plugins and skills from the repository root:
   - **Workspace Coding Conventions Audit**:
     ```bash
     python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py
     ```
   - **Compliance Audit**:
     ```bash
     python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/<plugin-name>
     ```
   - **Structural Audit**:
     ```bash
     python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/<plugin-name>
     ```
   - **Cross-Platform Symlink Check**:
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
     ```
   *Resolution Action:* If errors, missing references, or broken symlinks are reported, resolve them before committing or pushing. Never push with broken symlinks or failing convention audits.

3. **Verify Clean Working Tree**: Verify working directory is clean (`git status`) and push with `-u origin <branch>`.

### 4. When a push is rejected
If `git push` is rejected because the remote is ahead:
1. Run `git fetch origin` and `git merge origin/<branch>` or `git pull --rebase` (no stash).
2. If conflicts occur in `skills-lock.json`, resolve via Rule 2.
3. Push once clean. Never force-push around a rejected push.

### 5. No force push to main/master
Never `git push --force` to main or master under any circumstances.

### 6. No --no-verify
Never skip hooks with `--no-verify` unless the user explicitly requests it.

### 7. No autonomous PR or remote operations
- **Never run `gh pr create`**, `gh pr merge`, or any GitHub CLI command that creates or merges a pull request without an explicit, isolated user directive (e.g., "open a PR", "create a pull request now").
- Discussing, reviewing, or mentioning a PR in conversation does NOT constitute permission to open one.
- Applies equally to `hub`, `gh`, and any git alias that results in a remote-side PR or branch creation.

### 8. No branch switching during active unreviewed work
- Do not `git checkout`, `git switch`, or `git checkout -b` away from a feature branch that contains local commits not yet approved by the user.
- If a new branch is needed while work-in-progress commits exist on the current branch, stop and confirm with the user what to do with those commits before switching.

### 9. Commit only what is asked & required
- Commit only files within the task scope.
- Auto-modified files like `.DS_Store` or `uv.lock` should not be committed unless relevant.
- When `skills-lock.json` or `symlinks.json` changes as a direct result of adding/modifying skills or plugins, commit them together with the changes.

### 10. Evolution Integrity Gate — update map-debt BEFORE committing core logic
Any commit that touches files under `plugins/`, `src/`, or `py_services/` **must** do one of the following before `git commit`:
- Stage an update to `references/map-debt.md` recording the debt entry (RESOLVED or OPEN) for the change, **OR**
- Stage an update to `references/evolution-log.md` if one exists, **OR**
- Include `Evolution-Check: none` in the commit message body with a one-line justification.

**Failure mode this prevents:** committing core logic changes and only discovering the missing map-debt entry when CI fails on the PR — forcing a follow-up commit and a broken CI run.

**Correct sequence:**
1. Make code changes
2. Update `references/map-debt.md` (add or resolve the relevant DEBT entry)
3. `git add <code files> references/map-debt.md`
4. `git commit`

The CI gate (`Verify Evolution & Map Debt Compliance`) enforces this post-hoc. The rule enforces it pre-emptively. Both must be respected.

## Approval Required

- Any `git reset` (hard or soft)
- Any `git rebase -i`
- Any branch deletion (`git branch -d` / `-D`)
- Any `git push --force-with-lease` or force variant
- Any `git clean`

## Safe Without Asking

- `git status`, `git diff`, `git log` — read-only, always safe
- `git add <specific files>` + `git commit` when the user asked to commit
- `git push` (non-force) **only** when the user issued an explicit, isolated push directive (e.g., "push this branch", "push now") — conversational mentions of PRs or branches do NOT qualify
- Fetching and merging `origin/main` into the current working feature branch to keep it current — **but only while on that feature branch, and only if no local unreviewed commits would be lost or detached**
- `git checkout -b <branch>` when the user asks for a new branch **and no unreviewed local commits are present on the current branch**



<!-- plugin: dev-utils / graph-planning-superpowers-policy -->
---
trigger: always_on
description: Universal Execution Policy — Pre-Planning Intake Bookend, Native Plan Sandboxing, Worktree Isolation (.worktrees/task-<id>), Superpowers TDD, and Deterministic Exit Gates.
globs: ["**/*"]
---

# Graph Planning, Superpowers, and Execution Discipline Policy

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation (code writes, commits, external commands) without EXPLICIT user approval.
> "Sounds good" or "Looks right" is NOT approval.
> Only **"Proceed"**, **"Go"**, or **"Execute"** constitutes authorization.
> Explicit approval transitions task state to `APPROVED` in `context/control_plane.db`.
> **VIOLATION = SYSTEM FAILURE**

---

## 1. Overview & 4-Phase Lifecycle

All STANDARD-classified engineering tasks MUST progress through the 4-phase lifecycle below. This replaces legacy waterfall approaches and couples upstream discovery to deterministic execution.

```
Phase 0: Intake & Socratic Gate (exploration-cycle-plugin + work-intake)
   │
   ├─ TRIVIAL classification (single-file/few-line, no architectural impact):
   │    fast-track directly to INTAKE -> DONE, skipping Phases 1-3 entirely.
   │    No spec/plan compilation, no worktree isolation, no multi-agent review —
   │    the triage answer itself is the sole recorded audit artifact. Work still
   │    happens on a feature branch followed by a normal PR; only ceremony is
   │    skipped, never branch discipline or the push-to-origin gate.
   │    See work-intake/SKILL.md and GitHub Issue #534 for the full design.
   │
   └─ STANDARD classification: continue below.
   │
Phase 1: Native Plan Mode & Adversarial Review (critical-auditor + Human Gate)
   │
Phase 2: Worktree Isolation & Superpowers TDD (.worktrees/task-<id> + Red-Green-Refactor)
   │
Phase 3: Deterministic Exit Gates & Asymmetric Persistence (6-State Vocabulary + Wiki)
```

**Scope note:** this policy governs tasks tracked in `agent_control.py`'s SQLite control
plane. The `self-evolution` skill runs a separate, independent lifecycle
(`evolution_state.py`, TRIAGE→...→COMPLETED/ROLLBACK/ESCALATED) with its own worktree
convention and approval flow — see `self-evolution-policy.md` and Section 4's note below.
Whether these two systems should eventually be reconciled into one is an open architectural
question tracked in [GitHub Issue #537](https://github.com/richfrem/agent-plugins-skills/issues/537); until that's decided, treat them as two separately-governed systems, not one universal mechanism.

---

## 2. Phase 0: Pre-Planning Intake Bookend & Socratic Gate

Before Plan Mode can ever be entered, the task must be bounded. Immediately after task
registration and before any Socratic question, `work-intake` asks one direct triage
question — TRIVIAL or STANDARD — with a heuristic-derived recommended default (see the
TRIVIAL fast-track branch in Section 1). Only STANDARD-classified tasks proceed through the
rest of this phase and into Phase 1:

1. **Read-Only Exploration Cycle:**
   - Execute read-only codebase discovery via `exploration-cycle-plugin` (`technical_diagnostic_engine.py`).
   - Inspect coupling surfaces (touched files, SQLite schemas, cross-plugin symlinks), surface hidden assumptions, and evaluate candidate architectural forks.
   - Emit `exploration/DIAGNOSTIC_BRIEF.md`.
2. **Interview Gate (`work-intake`):**
   - **Native-First Deferral:** Inspect session environment markers first (`CLAUDE_CODE_ENTRY`, `ANTIGRAVITY_IDE`). Defer to native interactive intake if present. Fall back to Socratic Defaulting loop for headless/Copilot sessions.
   - Socratic Defaulting: 1–3 questions max, structured options with explicit recommended default (`Option A [Recommended]` vs. `Option B`).
   - Compiles the immutable **4-Pillar Spec** (`TASK_SPEC.md`):
     - **1. The Job:** System objective and target subsystem paths.
     - **2. The Why:** Architectural rationale and user/system impact.
     - **3. Semantic Guardrails & Operational Reasons:** Non-negotiables paired with operational justifications.
     - **4. Definition of Done (DoD):** Programmatic verification commands.
   - Atomically records task and transitions state in `context/control_plane.db` (`INTAKE` -> `INTERVIEW`).

---

## 3. Phase 1: Native Plan Mode & Adversarial Review

1. **Native Plan Sandboxing:**
   - Enforce host-native Plan Mode (Claude `/plan`, Copilot `@plan`, Antigravity plan mode) where available. Defer to Superpowers graph planning *only* when native host planning is absent or when executing complex multi-agent DAGs.
   - While in Plan Mode, filesystem mutations outside plan artifacts are strictly prohibited.
2. **Pre-Execution Critic Review:**
   - Run clean-context adversarial review via `critical-auditor` (max 2–3 rounds) probing failure domains and cross-plugin boundaries before human presentation.
3. **The Supreme Law Human Gate:**
   - Present plan and require explicit user approval ("Proceed", "Go", "Execute").
   - On approval, transition task to `APPROVED` in `context/control_plane.db`.

---

## 4. Phase 2: Worktree Isolation & Superpowers TDD

1. **Standard Worktree Topology:**
   - Implementation MUST execute in dedicated isolated worktrees at `.worktrees/task-<task_id>/` (governed by `issue_worktree_manage.py`). Never use sibling directories (`../worktree-...`).
   - Update `worktree_state` in `context/control_plane.db` to `written_in_worktree`.
   - **This convention applies to `agent_control.py`-tracked tasks only.** `self-evolution`
     cycles use their own separate, documented convention — sibling directories under
     `../worktree-evolution-<cycle_id>/` — per `self-evolution/SKILL.md` and
     `self-evolution-policy.md`. This is not a violation of the rule above; it's a
     different, independently-governed system (see Section 1's scope note and
     [#537](https://github.com/richfrem/agent-plugins-skills/issues/537)).
2. **Superpowers TDD Deferral Rule:**
   - Invoke Superpowers execution loops only where native execution lacks automated TDD or DAG management.
   - Enforce strict Red-Green-Refactor:
     - **Red:** Author concrete unit/integration tests matching the contract. Verify they FAIL.
     - **Green:** Implement minimum functional code to make tests pass.
     - **Refactor:** Clean up while maintaining 100% green test status.
3. **Mandatory Post-Task Leak Detection:**
   - Immediately after any subagent reports back, the controller MUST run `git status --short` in the main checkout (not the worktree) before packaging reviews. Discard stray uncommitted diffs matching superseded work.

---

## 5. Phase 3: Deterministic Exit Gates & Asymmetric Persistence

1. **Deterministic Local Exit:**
   - 100% green pass (`exit 0`) on tests (`pytest`), linters, and structural audits (`audit_plugin_structure.py`).
2. **Clean-Context Holistic Diff Review:**
   - Perform full-diff review to verify zero unintended mutations.
3. **Exact 6-State Worktree Status Vocabulary:**
   - Status reports must use the exact vocabulary from `worktree-lifecycle-management.md`:
     `written_in_worktree` | `committed_in_worktree` | `pushed_to_origin` | `merged_into_origin_main` | `local_branch_ref_updated` | `checked_out_on_disk`.
4. **Asymmetric Knowledge Persistence:**
   - Code mutations roll back on failure, but architectural insights, negative constraints, and discovered edge cases are permanently preserved in `wiki/decisions/` and `references/map-debt.md`.

---

## 6. Git & Environment Invariants

- **NEVER** commit directly to `main`. Always use isolated branches.
- **NEVER** run `git push` without explicit approval.
- **NEVER** commit transient agent directories (`.agents/`, `.claude/`, `.gemini/`, `.codex/`).
- UTF-8 encoding only. No smart quotes or non-ASCII characters in manifests and rules.


<!-- plugin: agent-scaffolders / plugin-architecture-policy -->
---
description: Universal rules for plugin file duplication, symlinks, cross-plugin resource bounds, Python script organization, and relative execution paths.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/**/*.py", "plugins/**/*.md"]
---

# Plugin Architecture & Coupling Policy

## 1. Hub-and-Spoke Resource Model & Installer Dereferencing

1. **Authoring Model vs. Runtime Model**:
   ```text
   one canonical editable source
   → managed file-level symlinks in skill source folders
   → plugin installer dereferences symlinks into hard copies
   → installed skills are fully self-contained
   ```
   Symlinks are used exclusively as a repository authoring and maintenance mechanism. The plugin installer dereferences all symlinks into physical hard copies during deployment into `.agents/`.

2. **Self-Contained Installed Skills**:
   An installed skill must be fully portable and independent. It must **NEVER** depend at runtime on:
   - The source repository or source symlink
   - The source plugin directory
   - The repository root or monorepo environment
   - Another installed plugin
   - A sibling Python distribution or external runtime package

3. **Canonical Ownership**:
   Every shared resource has exactly one editable canonical source owner in the repository. Consumers receive installer-materialized hard copies, which are deployed artifacts—not editable authorities. Do not create competing canonical source copies.

---

## 2. Separation of Concerns & Loose Coupling

1. **Pluggable Independence**: If a user installs a skill via `plugin_add.py` or `uvx`, that skill MUST function completely in isolation. It cannot crash or halt because another plugin is uninstalled or missing.
2. **Agent Delegation over Code Interfaces**: If a plugin requires coordination with another plugin, it must do so via Natural Language agent instructions (e.g., *"Please invoke the `<plugin>-agent` to..."*) rather than hardcoded Python imports, hidden filesystem state manipulations, or rigid cross-plugin bindings.
3. **Cross-Plugin Wire Contracts**: Sharing schemas, references, assets, or executable contract helpers through installer-materialized hard copies is permitted. Cross-plugin Python runtime imports or cross-plugin directory symlinks are strictly forbidden.

---

## 3. Plugin-Level Resource & Python Organization

1. **One Canonical Plugin-Level `scripts/` Directory**:
   Canonical Python code shared by skills belongs at the plugin root under `plugins/<plugin>/scripts/`.
2. **Logical Subfolders Approved**:
   Related Python scripts may be logically grouped into cohesive subfolders beneath `scripts/`.
   Approved examples:
   - `scripts/contracts/` (plugin-owned contracts and validation)
   - `scripts/pandoc_fixes/` (cohesive implementation modules)
   - `scripts/validation/` (input/output validation scripts)
   - `scripts/media/` (media conversion and handling)
3. **No Redundant Package-Name Directory**:
   Do **NOT** add a redundant package-name directory inside `scripts/` (e.g. `scripts/<plugin_name>/...`). The enclosing plugin directory already establishes the domain context.
4. **No Top-Level Sibling Runtime Packages**:
   Top-level external runtime packages (e.g. `contracts/python/` or `runtime/python/`) must not exist as required external dependencies. All shared code must belong to an owning plugin.

---

## 4. Resource Placement by Purpose

Resource placement is determined strictly by **purpose**, not file extension:

| Directory | Purpose |
|---|---|
| `references/` | Schemas, contracts, and documentation the agent reads |
| `scripts/` | Executable Python, validation, transformation, and helper scripts |
| `assets/` | Templates and static resources copied, embedded, transformed, or emitted |
| `tests/fixtures/` | Plugin test evidence and test fixtures |
| `evals/fixtures/` | Skill evaluation evidence and test cases |

---

## 5. Mandatory Symlink Workflow & Cross-Platform Protocol

**NEVER create symlinks with `ln -s` directly.**  
**NEVER create real file copies where a symlink should exist.**

All symlink creation, repair, and auditing must go through `.agents/skills/symlink-manager/scripts/symlink_manager.py` and be recorded in `symlinks.json`.

1. **File-Level Symlinks ONLY**:
   All shared resources within or across plugins must use **file-level symlinks ONLY**. Directory-level symlinks are strictly forbidden because installation bridges drop them or fail on cross-platform checkouts.
2. **Zero Manual `ln -s`**:
   Never invoke `ln -s` directly in the shell. Direct calls bypass the manifest, causing links to fail or disappear on fresh checkouts.
3. **Canonical Source Locations**:
   | Resource Type | Canonical Master Copy | Installed / Spoke Location |
   |---|---|---|
   | Python scripts | `plugins/<plugin-name>/scripts/` | `plugins/<plugin-name>/skills/<skill>/scripts/` |
   | References / docs | `plugins/<plugin-name>/references/` | `plugins/<plugin-name>/skills/<skill>/references/` |
   | Assets / templates | `plugins/<plugin-name>/assets/` | `plugins/<plugin-name>/skills/<skill>/assets/` |
4. **Required 5-Step Symlink Workflow**:
   - **Step 1: Diagnose first**
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
     ```
     Identify every `? regular file (not a link)` and `✗ broken symlink` before touching anything.
   - **Step 2: Remove real-file imposters**
     If a file that should be a symlink is a regular file copy, delete the imposter first:
     ```bash
     rm -f path/to/real-file-that-should-be-symlink
     ```
   - **Step 3: Register link in manifest (`symlinks.json`)**
     Record the canonical source and skill target via `symlink_manager.py` or formatted entry:
     `{ "src": "canonical/source.py", "dst": "skill/scripts/source.py", "strategy": "symlink", "description": "..." }`
   - **Step 4: Restore all from manifest**
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py restore
     ```
   - **Step 5: Verify clean status**
     ```bash
     python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose
     ```
     Ensure zero `? regular file` or `✗ broken symlink` entries remain before committing.

---

## 6. Strict Relative Path Execution

1. **Relative to Skill Root**: Inside `SKILL.md` workflows, path references must always be **relative to the skill root** (e.g., `../scripts/script.py` or `python3 scripts/script.py`). **Never use absolute paths or paths relative to the repository root.**
2. **Self-Contained Content**: Every file a skill references must be present inside the skill's directory — either as a hard copy or a symlink.
3. **Execution Context**:
   Installed skills execute from dynamic target locations:
   - `.agents/skills/<skill-name>/` (canonical)
   - `.claude/skills/<skill-name>/`
   Relative paths inside commands resolve from the skill root at the installed location. Verify paths against the installed structure, not the source tree.


<!-- plugin: dependency-management / dependency-management -->
---
description: Universal dependency management rules for Python and agent services.
globs: ["requirements*.txt", "requirements*.in", "Dockerfile", "pyproject.toml"]
---

## 🐍 Python Dependency Rules (Summary)

**Full workflow details → `.agents/skills/dependency-management/SKILL.md`**

### Non-Negotiables
1. **No manual `pip install`** — all changes go through `.in` → `pip-compile` → `.txt`.
2. **Commit `.in` + `.txt` together** — the `.in` is intent, the `.txt` is the lockfile.
3. **Service sovereignty** — every agent service owns its own `requirements.txt`.
4. **Tiered hierarchy** — Core (`requirements-core.in`) → Service-specific → Dev-only.
5. **Declarative Dockerfiles** — only `COPY requirements.txt` + `RUN pip install -r`. No ad-hoc installs.
6. **Hub-and-Spoke DRY** — canonical scripts at plugin/project root; file-level symlinks in `skills/` subfolders (no duplicate files).
7. **Symlink Resolution** — installers resolve symlinks to physical copies in `.agents/`; installed skills must be fully self-contained.
8. **Agent Orchestration** — cross-plugin coordination uses skill delegation via the prompt loop, not direct script execution.


---

## Background Document Priority (added 2026-09-13)

If the user's opening message references, pastes, or points to a local file (a prompt,
issue body, prior spec, handoff doc), read that file FIRST, before asking any
Socratic/interview question. Check every open question against it. For any question the
document already answers, use the document's answer directly — via
`record_source_assisted_answer_candidate(source_path=..., source_authorized=True, ...)`
where `work-intake`'s control plane is active, or by simply citing the source inline
otherwise. Never make the human re-answer, live, something they already wrote down for you.
Only ask a live question for what the document genuinely leaves open or ambiguous.
