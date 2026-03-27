# Capabilities Matrix: Plugin Comparison

Columns: **agent-agentic-os** | **exploration-cycle-plugin** | **superpowers**
Rating scale: Full / Partial / Missing / Not Applicable

---

## 1. Session Memory and Persistence

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Session-to-session memory persistence | **Full** - Three-tier model: MEMORY.md (auto), context/memory.md (curated L3), context/memory/YYYY-MM-DD.md (L2 session logs). Deduplication and conflict detection built in. | **Partial** - Relies on agentic-os kernel.py for event emission; exploration/session-brief.md persists session intent. No independent memory stack. | **Missing** - No persistent memory layer. Session context is injected via the SessionStart hook (using-superpowers SKILL.md content only). No cross-session learning or retention. |
| Memory promotion and garbage collection | **Full** - session-memory-manager skill drives deliberate promotion from L2 to L3. Includes conflict resolution guard ("dementia guard"). | **Missing** - No promotion logic. Hook only suggests starting intake if brief is absent. | **Missing** - Not a concern in the design. Skills are stateless. |
| Memory deduplication and dedup IDs | **Full** - Conflict detection and dedup IDs explicitly specified in session-memory-manager and memory-hygiene reference. | **Missing** | **Missing** |
| Structured event log (audit trail) | **Full** - context/events.jsonl as the system event bus. kernel.py emits structured events with agent, type, action, status fields. | **Partial** - Uses kernel.py emit_event if present; exploration events emitted to the same log. Dependent on agentic-os being initialized. | **Missing** - No event log. No audit trail. |

---

## 2. Learning Loops and Retrospectives

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Post-session retrospective mechanism | **Full** - os-learning-loop agent mines events.jsonl, proposes SKILL.md and CLAUDE.md patches. Fast Path and Full Loop modes. | **Full** - exploration-optimizer skill runs autoresearch-style iteration loops on exploration artifacts. results.tsv records keep/discard decisions. | **Missing** - No retrospective. No session closure workflow. Skills are authored once and updated manually. |
| Objective eval gate before applying changes | **Full** - skill-improvement-eval runs eval_runner.py against evals.json. KEEP/DISCARD verdict gates any write. | **Full** - exploration-optimizer enforces baseline-first, one-variable iteration with results.tsv ledger. Demonstrated in 12+ real iterations in evals/results.tsv. | **Missing** - No eval gate. writing-skills uses TDD-for-documentation approach (run agent without skill, observe failure, write skill, verify compliance), but this is a manual one-time authoring process, not a continuous loop. |
| Friction event capture and threshold triggering | **Full** - post_run_metrics.py counts friction events and emits metric. If friction_events_total >= 3, os-learning-loop auto-triggers on next session start. | **Partial** - No friction event infrastructure. exploration-optimizer runs on-demand. | **Missing** |
| Self-improvement ledger (longitudinal tracking) | **Full** - improvement-ledger.md records eval score progression, survey-to-action trace, and Autonomous Workflow Completion Rate across cycles. Specified in improvement-ledger-spec.md. | **Partial** - evals/results.tsv provides longitudinal keep/discard history. Less structured than improvement-ledger.md. | **Missing** |
| Post-run self-assessment survey | **Full** - post_run_survey.md is mandatory after every eval run. Agents save surveys to context/memory/retrospectives/. Friction counts feed the improvement loop. | **Partial** - Referenced in architecture docs. exploration-optimizer specifies survey data as a quality signal. Not as rigidly enforced as in agentic-os. | **Missing** |

---

## 3. Multi-Agent Orchestration

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Sequential agent handoff via shared state | **Full** - Agents A/B coordinate through events.jsonl event bus. Strategy packets (handoffs/packet-*.md) formalize handoff. kernel.py handles turn signaling. | **Full** - exploration-cycle-orchestrator dispatches agents sequentially. Requirements-doc-agent invoked once per focused capture pass. Handoff preparer synthesizes all captures. | **Partial** - executing-plans and subagent-driven-development implement task-by-task sequential dispatch. No shared event log; coordination is implicit via TodoWrite state. |
| Parallel agent dispatch | **Full** - concurrent-agent-loop documents fan-out, request-reply, and turn-signal coordination topologies using kernel event bus. | **Partial** - Dual-loop pattern supports parallel dispatch. exploration-cycle-orchestrator can dispatch multiple CLI agents. No explicit fan-out topology documented. | **Full** - dispatching-parallel-agents skill provides a complete parallel agent dispatch pattern with explicit domain isolation and integration review step. |
| Inner/outer loop (supervisor + worker) | **Full** - dual-loop.md defines ORCHESTRATOR (strategy, git, human interaction) vs INNER_AGENT (code, tests) with correction packets and KEEP/DISCARD. PEER_AGENT provides independent eval. | **Full** - Dual-Loop pattern explicitly referenced and implemented. exploration-cycle-orchestrator is outer; requirements-doc-agent is inner. Correction loops possible. | **Partial** - subagent-driven-development dispatches implementer, spec-reviewer, and quality-reviewer subagents per task. Two-stage review with loops, but no formal outer/inner designation or correction packets. |
| Agent lock and collision prevention | **Full** - context/.locks/ with kernel.py acquire_lock/release_lock. Stale lock timeout. Explicit abort if lock fails. | **Partial** - Uses agentic-os kernel.py locks if available. No independent locking. | **Missing** - No multi-agent collision prevention. Skills assume one agent at a time. |
| Background + foreground agent separation | **Full** - os-learning-loop and os-health-check run asynchronously. Lock mechanism prevents foreground collision. | **Missing** | **Missing** |

---

## 4. Exploration and Discovery Workflows

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Problem framing and requirements capture | **Missing** - Not in scope. | **Full** - intake-agent, problem-framing-agent, requirements-doc-agent (5 capture modes), user-story-capture, business-requirements-capture, business-workflow-doc (Mermaid). | **Partial** - brainstorming skill covers problem framing through Socratic dialogue and 2-3 approach proposals. No structured requirements capture or BRD generation. |
| Prototype-led discovery | **Missing** | **Full** - prototype-companion-agent captures observations. prototype-builder skill (deferred). | **Missing** |
| Business rule capture and audit | **Missing** | **Full** - business-rule-audit-agent.md verifies prototype logic against captured rules. | **Missing** |
| Handoff to downstream workflow | **Missing** | **Full** - exploration-handoff skill synthesizes captures into audience-targeted handoff package with Reader Testing stage and gap prediction. Optional planning-doc-agent bridges to spec-kitty. | **Partial** - brainstorming writes design doc and transitions to writing-plans. Single-step handoff, no audience routing or gap validation. |
| Greenfield / brownfield / re-entry classification | **Missing** | **Full** - intake-agent classifies session type explicitly. Re-entry spike mode supported. | **Missing** - brainstorming does not distinguish. |

---

## 5. Spec-Driven Development Lifecycle

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Spec / design document creation | **Missing** | **Partial** - planning-doc-agent creates spec.md drafts (optional). No native spec authoring. | **Full** - brainstorming produces design doc in docs/superpowers/specs/YYYY-MM-DD-topic-design.md with self-review and user approval gate. |
| Implementation plan creation | **Missing** | **Missing** (handoff targets spec-kitty plan.md, not a superpowers-style step-by-step plan) | **Full** - writing-plans produces bite-sized task plans with exact file paths, complete code, TDD steps, and verification commands per task. "No Placeholders" enforcement, self-review checklist. |
| Phase gate enforcement (design then plan then build) | **Missing** | **Partial** - Human gate concept present in spec-kitty integration path. Not enforced within exploration-cycle-plugin itself. | **Full** - brainstorming HARD-GATE blocks any implementation skill until design is approved. writing-plans must precede executing-plans. Workflow sequencing is enforced via skill checklists and process flow diagrams. |
| Task-level implementation tracking | **Missing** | **Missing** | **Full** - TodoWrite used per task in subagent-driven-development and executing-plans. Each task marked in_progress then completed. |

---

## 6. Code Review Workflows

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Pre-merge code review | **Missing** | **Missing** | **Full** - requesting-code-review dispatches code-reviewer subagent with git SHA range and context isolation. Mandatory after each task in subagent-driven-development. |
| Review feedback reception and pushback | **Missing** | **Missing** | **Full** - receiving-code-review skill provides complete response pattern including forbidden performative phrases, YAGNI check, technical pushback protocol, and GitHub thread reply guidance. |
| Two-stage review (spec compliance + quality) | **Missing** | **Missing** | **Full** - subagent-driven-development dispatches spec-reviewer-prompt.md then code-quality-reviewer-prompt.md as separate subagents per task. Each has its own review loop. |
| Final whole-implementation review | **Missing** | **Missing** | **Full** - subagent-driven-development dispatches final code reviewer after all tasks complete, before finishing-a-development-branch. |

---

## 7. Git Worktree Management

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Worktree creation and isolation | **Missing** (referenced in references only) | **Missing** (spec-kitty handles worktrees externally) | **Full** - using-git-worktrees provides complete workflow: directory priority (.worktrees > worktrees), .gitignore verification, safety verification, creation steps, and integration with finishing-a-development-branch. |
| Worktree cleanup at branch completion | **Missing** | **Missing** | **Full** - finishing-a-development-branch handles worktree removal for options 1 and 4 (merge/discard). Skips cleanup for option 2 (PR) and option 3 (keep). |
| Branch completion workflow (merge/PR/discard) | **Missing** | **Missing** | **Full** - finishing-a-development-branch presents exactly 4 options with typed "discard" confirmation, test verification gate, and git commands for each path. |

---

## 8. Sub-Agent Dispatching

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Context isolation for subagents | **Partial** - Strategy packets enforce minimal context ("only what INNER_AGENT needs"). | **Full** - dispatch.py wrapper handles file IO with explicit separations. "Cheap model, many invocations, no context inheritance" is the explicit design intent. | **Full** - "Subagents receive only the context they need, preventing context window pollution." Implementer, spec-reviewer, quality-reviewer each get purpose-built prompts. |
| Model selection strategy | **Missing** | **Partial** - "cheap model / free tier" for requirements-doc-agent. No per-task model selection guidance. | **Full** - subagent-driven-development documents model selection: mechanical tasks (fast/cheap), integration tasks (standard), architecture/review (most capable). |
| Named agent types with roles | **Partial** - ORCHESTRATOR, INNER_AGENT, PEER_AGENT roles defined in concurrent-agent-loop. | **Partial** - orchestrator, requirements-doc-agent, prototype-companion, business-rule-audit, handoff-preparer roles defined. | **Full** - implementer, spec-reviewer, code-quality-reviewer, code-reviewer subagent types with separate prompt files. Cross-platform mapping (Codex, Gemini) documented. |
| Dispatch wrapper / tooling | **Partial** - kernel.py provides event bus infrastructure. No dispatch wrapper equivalent. | **Full** - dispatch.py provides safe file IO, explicit separations, and subprocess execution. | **Not Applicable** - Task tool (Claude Code native) / spawn_agent (Codex) used directly. No wrapper needed. |

---

## 9. Hook Lifecycle

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| SessionStart hook | **Full** - update_memory.py fires on session start. | **Partial** - session_start.py fires; checks for exploration brief; emits event if missing. | **Full** - session-start bash script injects using-superpowers SKILL.md content as additionalContext. Platform detection (Cursor vs Claude Code vs other). |
| PostToolUse hook | **Full** - update_memory.py fires on every tool call. | **Missing** | **Missing** |
| Stop / SessionEnd hook | **Full** - post_run_metrics.py fires on Stop; counts friction events. | **Missing** | **Missing** |
| PreToolUse hook | **Missing** (referenced in sub-agents-and-hooks.md as a pattern) | **Missing** | **Missing** |
| Multi-platform hook support (Cursor, Codex, Gemini) | **Missing** | **Missing** | **Full** - hooks-cursor.json with camelCase format for Cursor. Platform detection in session-start. Gemini CLI extension. run-hook.cmd for Windows. --resume guard prevents re-injection. |
| Hook prevents double injection on resume | **Missing** | **Missing** | **Full** - SessionStart hook fires only on startup/clear/compact, not --resume. |

---

## 10. Slash Command Coverage

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Commands defined | **Full** - /os-init, /os-loop, /os-memory. Each has approval gate before running agents. | **Missing** - No commands directory in exploration-cycle-plugin. | **Partial** - /brainstorm, /write-plan, /execute-plan all deprecated in favor of skill invocation. Skills are the primary interface. |
| Skill-first vs command-first design | Commands supplement skills | No commands | Intentionally migrated away from commands to skills |

---

## 11. Plan-Execute-Verify Cycles

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Explicit plan before execution | **Missing** | **Partial** - session brief gates requirements capture. Intake precedes orchestration. | **Full** - HARD-GATE in brainstorming, then writing-plans, then execution. Cannot skip steps. |
| Verification before completion claim | **Missing** | **Missing** | **Full** - verification-before-completion skill enforces "no completion claim without fresh verification evidence." Iron Law with rationalization prevention table. |
| Pre-execution workflow commitment diagrams | **Full** - Strategy packets require Pre-Execution Workflow Commitment Diagram (ASCII box). | **Partial** - exploration-cycle-workflow.mmd exists as visual reference. | **Full** - Graphviz dot diagrams embedded in brainstorming, subagent-driven-development, writing-plans, and dispatching-parallel-agents SKILL.md files. |
| Checkpoint-based batch execution | **Missing** | **Missing** | **Full** - executing-plans uses human checkpoints between batches. subagent-driven-development reviews after each task. |

---

## 12. Test-Driven Development Support

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| TDD workflow enforcement | **Missing** | **Missing** | **Full** - test-driven-development skill enforces RED-GREEN-REFACTOR with Iron Law ("delete code written before tests, start over"). No exceptions for simple tasks. |
| Testing anti-patterns reference | **Missing** | **Missing** | **Full** - testing-anti-patterns.md documents common TDD violations and how to recognize rationalization. |
| TDD applied to skill authoring | **Partial** - skill-improvement-eval adapts Karpathy autoresearch pattern for skill patches. | **Partial** - exploration-optimizer adapts autoresearch for workflow iteration. | **Full** - writing-skills explicitly maps TDD to documentation: test case = pressure scenario, RED = agent violates rule without skill, GREEN = agent complies with skill present. Run baseline subagent before writing skill. |
| Integration tests for skills | **Missing** | **Missing** | **Full** - tests/claude-code/ contains integration test scripts that run real Claude Code sessions in headless mode and parse .jsonl transcripts to verify skill behavior. |

---

## 13. Debugging Support

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| Systematic debugging workflow | **Missing** | **Missing** | **Full** - systematic-debugging enforces 4-phase root cause investigation: read error messages, reproduce consistently, check recent changes, gather evidence at component boundaries. Iron Law: no fixes without root cause. |
| Debugging reference techniques | **Missing** | **Missing** | **Full** - root-cause-tracing.md, defense-in-depth.md, condition-based-waiting.md, find-polluter.sh all included as supporting references in systematic-debugging/. |
| System health check | **Full** - os-health-check agent inspects event log, memory state, and lock status. | **Missing** | **Missing** |

---

## 14. Cross-Agent Portability (npx skills / multi-IDE)

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| npx skills install | **Full** - `npx skills add richfrem/agent-plugins-skills --path plugins/agent-agentic-os` | **Full** - `npx skills add richfrem/agent-plugins-skills --path plugins/exploration-cycle-plugin` | **Not Applicable** - Uses plugin marketplace directly; npm package (package.json) for OpenCode. |
| Claude Code native | **Full** | **Full** | **Full** |
| Cursor support | **Missing** | **Missing** | **Full** - hooks-cursor.json, CURSOR_PLUGIN_ROOT detection. |
| Gemini CLI support | **Missing** | **Missing** | **Full** - gemini-extension.json, GEMINI.md, gemini-tools.md tool mapping. |
| Codex / OpenCode support | **Missing** | **Missing** | **Full** - docs/README.codex.md, docs/README.opencode.md, codex-tools.md tool mapping, spawn_agent translation guide. |
| Windows support | **Missing** | **Missing** | **Full** - run-hook.cmd, Windows-specific bash bug fixes, MSYS2 detection, foreground mode fallback. |
| Tool name translation layer | **Missing** | **Missing** | **Full** - codex-tools.md and gemini-tools.md map Claude Code tool names to platform equivalents. |

---

## 15. Documentation and Onboarding Quality

| Dimension | agent-agentic-os | exploration-cycle-plugin | superpowers |
|---|---|---|---|
| README clarity and completeness | **Full** - README.md + SUMMARY.md provide OS analogy, three-tier table, signaling patterns, scope limits, honest limitations. | **Partial** - README covers purpose, optional integrations, CLI invocation anti-patterns, and phased build plan. Less architectural depth. | **Full** - README covers complete workflow, philosophy, all skills, multi-platform install. Blog post linked. |
| Architecture diagrams | **Full** - PNG diagrams in assets/diagrams/: overview, structure, loop-lifecycle, memory-subsystem. Mermaid source in assets/. | **Partial** - .mmd diagrams referenced in skills but not all are built. | **Full** - Graphviz dot diagrams embedded directly in SKILL.md files (inline, not external assets). Renders in supported environments. |
| Self-documented limitations | **Full** - README explicitly lists keyword heuristic vulnerability, missing shadow mode, Goodhart's Law risk in SUMMARY.md. | **Partial** - README notes scaffold-not-finished status and phased build order. | **Partial** - RELEASE-NOTES.md documents regression findings (subagent review loop removed after benchmarking). No single limitations document. |
| Release notes / changelog | **Partial** - CHANGELOG.md present. | **Missing** | **Full** - RELEASE-NOTES.md documents every version with specific bug IDs, regression data, and community contributor attribution. |
| Skill creation guide | **Partial** - references/skill_optimization_guide.md. skill-improvement-eval covers evaluation discipline. | **Missing** | **Full** - writing-skills is a complete guide with TDD mapping, skill types, directory structure, testing methodology, anthropic-best-practices.md. |

---

*Matrix based on direct file analysis of all SKILL.md, agent .md, hooks, references, and README files in each plugin as of 2026-03-27.*
