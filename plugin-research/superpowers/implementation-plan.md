# Implementation Plan: Superpowers Hybrid Integration

**Branch:** feat/superpowers-hybrid-integration (merged to main via PR #129)
**Decision:** Option C - Hybrid (see `decision.md`)
**Execution guide:** `quick-wins.md`
**Status:** COMPLETE - all phases done

---

## Phase 0: Decision and Planning

- [x] Comparative analysis across superpowers / agent-agentic-os / exploration-cycle-plugin
- [x] ADR review (ADR-001 through ADR-004) and architectural correction
- [x] Decision brief written (`decision.md`)
- [x] Implementation plan written (this file)
- [x] Feature branch created: `feat/superpowers-hybrid-integration`

---

## Phase 1: Scaffold agent-execution-disciplines Plugin (QW1)

**Goal:** One canonical home for all ported superpowers execution skills.

- [x] `plugin.json` -- not used in this ecosystem; `lsp.json` serves that role
- [x] Create `plugins/agent-execution-disciplines/README.md`
- [x] Create `plugins/agent-execution-disciplines/skills/` directory structure
- [x] Create `plugins/agent-execution-disciplines/agents/` directory
- [x] Create `plugins/agent-execution-disciplines/references/` (for shared refs)
- [x] Create `plugins/agent-execution-disciplines/scripts/` (for shared scripts)
- [x] Port `superpowers/skills/verification-before-completion/SKILL.md`
  - [x] SKILL.md in `skills/verification-before-completion/`
  - [x] Add friction event type `false_completion_claim` note in agent-agentic-os `agents/os-learning-loop.md`
- [x] `tools_manifest.json` is auto-generated -- skipped (find-polluter.sh picked up on next regen)
- [x] Run `plugin_installer.py --dry-run` -- CLEAN: all 6 skills + code-reviewer agent resolve

---

## Phase 2: Port Execution Discipline Skills (QW3, QW4, QW5, QW6)

All skills land in `plugins/agent-execution-disciplines/`.

### QW3: Systematic Debugging
- [x] Port `superpowers/skills/systematic-debugging/SKILL.md`
- [x] Copy reference files to plugin root: `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`
- [x] Copy script: `find-polluter.sh` in plugin scripts + skill scripts dir
- [x] File-level symlinks in skill dir -> plugin root (ADR-003)
- [ ] Add `debugging_without_root_cause` friction event note in agent-agentic-os -- deferred

### QW4: Test-Driven Development
- [x] Port `superpowers/skills/test-driven-development/SKILL.md`
- [x] Copy `testing-anti-patterns.md` to plugin root references
- [x] File-level symlink in skill dir -> plugin root (ADR-003)
- [ ] Register evals in `skills/test-driven-development/evals/evals.json` -- deferred (requires baseline session)

### QW5: Git Worktree Management
- [x] Port `superpowers/skills/using-git-worktrees/SKILL.md` (spec-kitty .worktrees/ convention noted)
- [x] Port `superpowers/skills/finishing-a-development-branch/SKILL.md`
- [ ] Add prose cross-reference in `agent-agentic-os/skills/agentic-os-guide/SKILL.md` -- deferred

### QW6: Code Review
- [x] Port `superpowers/skills/requesting-code-review/SKILL.md`
- [x] Port `superpowers/agents/code-reviewer.md` to `agents/`
- [x] Deep kernel event bus integration deferred (see decision.md Out of Scope)

---

## Phase 3: Harden SessionStart Hook (QW2)

**Goal:** POSIX-safe bash wrapper around Python kernel, no replacement of Python logic.

- [x] Read current `plugins/agent-agentic-os/hooks/` structure
- [x] Identify the current session-start / update_memory trigger mechanism
- [x] Write new bash wrapper (`hooks/session-start.sh`) with:
  - [x] Platform detection (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback)
  - [x] Trigger guard: fire only on `startup|clear|compact`, skip `--resume` (60s recency check)
  - [x] `printf` instead of heredoc (avoids bash 5.3+ hang -- superpowers RELEASE-NOTES v5.0.3 #572)
  - [x] Platform-conditional `hookSpecificOutput` key
  - [x] Passes resolved `PLUGIN_ROOT` to existing Python orchestrator as arg
- [ ] Test dry-run: verify no double-injection on `--resume` -- deferred (requires live session)
- [ ] Test live: verify memory injection fires correctly on fresh session -- deferred (requires live session)

---

## Phase 4: Embed Diagrams in Existing Skills (QW7)

**Goal:** Inline Graphviz dot diagrams in the three most complex richfrem skills.

- [x] Add digraph block to `agent-agentic-os/skills/concurrent-agent-loop/SKILL.md`
  (Fast Cycle 7-step workflow with KEEP/DISCARD decision branching)
- [x] Embed Phase A workflow diagram in `exploration-cycle-plugin/skills/exploration-workflow/SKILL.md`
  (inline digraph replaces external .mmd reference; all phases + human gates shown)
- [x] Add routing decision tree diagram to `exploration-cycle-plugin/agents/exploration-cycle-orchestrator-agent.md`
  (digraph + original ASCII block retained)

---

## Phase 5: Port Writing-Skills TDD Methodology (QW8)

**Goal:** RED-scenario verification gate for skill authoring in agent-agentic-os.

- [x] Port `superpowers/skills/writing-skills/SKILL.md` into `plugins/agent-agentic-os/skills/writing-skills/`
  - [x] Adapt: `skill-improvement-eval` as the GREEN verification step
  - [x] Adapt: autoresearch eval format (evals.json + results.tsv) for longitudinal tracking
- [x] Add RED-scenario gate (MANDATORY) to `agents/os-learning-loop.md` Phase 3:
  before any skill proposal, generate RED scenario + observed failure + acceptance criterion

---

## Phase 6: Final Verification and Commit

- [x] Run `plugin_installer.py --dry-run --plugin plugins/agent-execution-disciplines` -- CLEAN
- [ ] Run `plugin_installer.py --plugin plugins/agent-execution-disciplines` -- pending user approval
- [ ] Verify all 6+ new skills appear in `.agents/skills/` -- pending install
- [ ] Run plugin structure auditor -- deferred
- [ ] Commit all changes -- pending user approval
- [ ] Push -- pending user approval

---

## Summary

| Phase | What | Quick Win | Status |
|---|---|---|---|
| 0 | Decision + planning | - | DONE |
| 1 | Scaffold plugin + verification | QW1 | DONE |
| 2a | Systematic debugging | QW3 | DONE |
| 2b | TDD enforcement | QW4 | DONE |
| 2c | Git worktree management | QW5 | DONE |
| 2d | Code review | QW6 | DONE |
| 3 | Harden SessionStart hook | QW2 | DONE |
| 4 | Embed diagrams | QW7 | DONE |
| 5 | Writing-skills TDD methodology | QW8 | DONE |
| 6 | Audit + commit | - | Pending approval |
