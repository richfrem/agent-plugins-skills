# Implementation Plan: Superpowers Hybrid Integration

**Branch:** feat/superpowers-hybrid-integration
**Decision:** Option C - Hybrid (see `decision.md`)
**Execution guide:** `quick-wins.md`

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

- [ ] Create `plugins/agent-execution-disciplines/plugin.json`
- [ ] Create `plugins/agent-execution-disciplines/README.md`
- [ ] Create `plugins/agent-execution-disciplines/skills/` directory structure
- [ ] Create `plugins/agent-execution-disciplines/agents/` directory
- [ ] Create `plugins/agent-execution-disciplines/references/` (for shared refs)
- [ ] Create `plugins/agent-execution-disciplines/scripts/` (for shared scripts)
- [ ] Port `superpowers/skills/verification-before-completion/SKILL.md`
  - [ ] SKILL.md in `skills/verification-before-completion/`
  - [ ] Add friction event type `false_completion_claim` note in agent-agentic-os `agents/os-learning-loop.md`
- [ ] Register plugin in `plugins/tool_inventory.json`
- [ ] Run `bridge_installer.py --dry-run` to verify structure is clean

---

## Phase 2: Port Execution Discipline Skills (QW3, QW4, QW5, QW6)

All skills land in `plugins/agent-execution-disciplines/`.

### QW3: Systematic Debugging
- [ ] Port `superpowers/skills/systematic-debugging/SKILL.md`
- [ ] Copy reference files to plugin root: `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`
- [ ] Copy script to plugin root: `find-polluter.sh`
- [ ] Create file-level symlinks in skill dir -> plugin root (ADR-003)
- [ ] Add `debugging_without_root_cause` friction event note in agent-agentic-os

### QW4: Test-Driven Development
- [ ] Port `superpowers/skills/test-driven-development/SKILL.md`
- [ ] Copy `testing-anti-patterns.md` to plugin root
- [ ] Create file-level symlink in skill dir -> plugin root (ADR-003)
- [ ] Register evals in `skills/test-driven-development/evals/evals.json`

### QW5: Git Worktree Management
- [ ] Port `superpowers/skills/using-git-worktrees/SKILL.md`
  - [ ] Adapt: respect spec-kitty's `.worktrees/` convention
- [ ] Port `superpowers/skills/finishing-a-development-branch/SKILL.md`
- [ ] Add prose cross-reference in `agent-agentic-os/skills/agentic-os-guide/SKILL.md`

### QW6: Code Review
- [ ] Port `superpowers/skills/requesting-code-review/SKILL.md`
- [ ] Port `superpowers/agents/code-reviewer.md` to `agents/`
- [ ] Note: deep kernel event bus integration deferred (see decision.md Out of Scope)

---

## Phase 3: Harden SessionStart Hook (QW2)

**Goal:** POSIX-safe bash wrapper around Python kernel, no replacement of Python logic.

- [ ] Read current `plugins/agent-agentic-os/hooks/` structure
- [ ] Identify the current session-start / update_memory trigger mechanism
- [ ] Write new bash wrapper with:
  - [ ] Platform detection (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback)
  - [ ] Trigger guard: fire only on `startup|clear|compact`, skip `--resume`
  - [ ] `printf` instead of heredoc (avoids bash 5.3+ hang)
  - [ ] Platform-conditional `hookSpecificOutput` key
  - [ ] Passes resolved `PLUGIN_ROOT` to existing Python orchestrator as arg
- [ ] Test dry-run: verify no double-injection on `--resume`
- [ ] Test live: verify memory injection fires correctly on fresh session

---

## Phase 4: Embed Diagrams in Existing Skills (QW7)

**Goal:** Inline Graphviz dot diagrams in the three most complex richfrem skills.

- [ ] Add digraph block to `agent-agentic-os/skills/concurrent-agent-loop/SKILL.md`
  (Fast Cycle and Standard Cycle workflows)
- [ ] Embed Phase A workflow diagram in `exploration-cycle-plugin/skills/exploration-workflow/SKILL.md`
- [ ] Add routing decision tree diagram to `agent-agentic-os/agents/exploration-cycle-orchestrator-agent.md`

---

## Phase 5: Port Writing-Skills TDD Methodology (QW8)

**Goal:** RED-scenario verification gate for skill authoring in agent-agentic-os.

- [ ] Port `superpowers/skills/writing-skills/SKILL.md` into `plugins/agent-agentic-os/skills/`
  - [ ] Adapt: use `skill-improvement-eval` infrastructure as the GREEN verification step
  - [ ] Adapt: use autoresearch eval format already established in agent-agentic-os
- [ ] Add RED-scenario gate requirement to `agents/os-learning-loop.md`:
  before proposing any skill patch, generate one RED scenario and verify GREEN behavior

---

## Phase 6: Final Verification and Commit

- [ ] Run `bridge_installer.py --dry-run --plugin plugins/agent-execution-disciplines`
- [ ] Run `bridge_installer.py --plugin plugins/agent-execution-disciplines`
- [ ] Verify all 6+ new skills appear in `.agents/skills/`
- [ ] Run `plugins/agent-plugin-analyzer/scripts/audit_plugin_structure.py plugins/agent-execution-disciplines`
  and confirm exit code 0 (no ADR violations)
- [ ] Commit all changes on `feat/superpowers-hybrid-integration`
- [ ] Ready to push (user approval required before push)

---

## Summary

| Phase | What | Quick Win | Effort |
|---|---|---|---|
| 0 | Decision + planning | - | Done |
| 1 | Scaffold plugin + verification | QW1 | Small |
| 2a | Systematic debugging | QW3 | Small |
| 2b | TDD enforcement | QW4 | Small |
| 2c | Git worktree management | QW5 | Small |
| 2d | Code review | QW6 | Medium |
| 3 | Harden SessionStart hook | QW2 | Small |
| 4 | Embed diagrams | QW7 | Small |
| 5 | Writing-skills TDD methodology | QW8 | Medium |
| 6 | Audit + commit | - | Small |
