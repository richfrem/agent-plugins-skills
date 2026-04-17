---
concept: implementation-plan-superpowers-hybrid-integration
source: research-docs
source_file: superpowers/implementation-plan.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.463796+00:00
cluster: done
content_hash: 099bbd283c355167
---

# Implementation Plan: Superpowers Hybrid Integration

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
- [ ] Test live: verify memory injection

*(content truncated)*

## See Also

- [[decision-brief-superpowers-hybrid-integration]]
- [[azure-ai-foundry-open-agent-skill-integration-plan]]
- [[azure-foundry-integration-plan]]
- [[azure-foundry-integration-plan]]
- [[sme-orchestrator-option-15-detailed-implementation-plan]]
- [[dashboard-pattern-refactor-option-15-implementation-plan]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/implementation-plan.md`
- **Indexed:** 2026-04-17T06:42:10.463796+00:00
