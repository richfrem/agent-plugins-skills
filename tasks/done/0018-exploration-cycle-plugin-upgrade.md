# 0018 — Exploration Cycle Plugin: Self-Healing & Quality Upgrades

## Context

Applying the same lessons learned from the agentic-os plugin (0017) to the exploration-cycle-plugin.
Full source review completed 2026-04-22. Gaps identified by applying browser-harness self-healing
patterns: contribute-back reflex, gotchas embedded in artifacts, thin-core/domain-layer separation,
and structured agent handoff signaling.

---

## Gaps Identified (Source Review)

### Critical Bugs
1. **Model identifier (dashes vs dots):** `claude-sonnet-4-6` and `claude-opus-4-6` appear in
   `skills/exploration-workflow/SKILL.md` and `references/dispatch-strategies.md`. Correct form is
   `claude-sonnet-4.6` / `claude-opus-4.6` (dot). Will cause "model not available" errors at runtime.

2. **Intake agent template path bug:** `intake-agent.md` Phase 4 reads
   `architecture/templates/exploration-session-brief-template.md` — this path does not exist.
   Templates are in `assets/templates/`. Fix: point to `assets/templates/` or create the missing file.

3. **TierGate Q5 inconsistency:** `exploration-handoff/SKILL.md` Stage 1.5 has 5 questions (Q5 added
   for people-decisions/bias risk). `references/hard-gate-enforcement.md` Tier 3 Hard Stop section
   still references only 4-question logic. Inconsistency creates wrong tier determinations.

4. **Plugin-level evals.json is a stub:** `evals/evals.json` has only 4 REPLACE placeholder prompts.
   No real routing eval cases — breaks any autoresearch loop on this plugin.

### Missing Browser-Harness Patterns

5. **No `## Gotchas` sections:** None of the SKILL.md files document field-tested failure patterns.
   Per browser-harness pattern: gotchas belong in the artifact, not an external log.
   Skills to add `## Gotchas` to: `exploration-workflow`, `discovery-planning`, `subagent-driven-prototyping`,
   `exploration-handoff`, `business-rule-audit-agent`.

6. **No structured HANDOFF_BLOCK:** Child skills signal completion via prose ("PHASE N COMPLETE" text).
   The orchestrator re-reads disk state rather than consuming a machine-readable handoff signal.
   Add machine-readable `## HANDOFF_BLOCK` code fences to child skill completion sections:
   `discovery-planning`, `exploration-handoff`, `subagent-driven-prototyping`.

7. **No domain-patterns reference layer:** Agentic-OS has `references/domain-patterns/routing-skill.md`
   for known failure escape patterns. Exploration-cycle has no equivalent for exploration workflow
   failure types (false starts, wrong session type classification, premature handoff, etc.).

### Python Script Improvements

8. **dispatch.py: no model flag for Copilot backend:** When `--cli copilot`, no `--model` arg is
   passed — the model is selected by the Copilot CLI default. Should support `--model` flag so callers
   can explicitly request `claude-sonnet-4.6` for premium tasks.

9. **dispatch.py: security TODO unresolved:** `--dangerously-skip-permissions` is applied
   unconditionally for Claude CLI backend regardless of Tier. The comment says "Tier 2/3 workloads
   require explicit human gate before any bash-capable dispatch." Add `--tier` flag; only apply
   `--dangerously-skip-permissions` when `--tier 1` (or unset, defaulting to Tier 1 for backward compat).

10. **No session-end friction hook:** Plugin only has `hooks/session_start.py`. There is no end-of-session
    friction capture. The `exploration-optimizer` skill has no automated input source. Add
    `hooks/session_end.py` that writes a summary event to `context/events.jsonl` when a session completes
    (dashboard status = Complete), giving the optimizer a friction signal.

---

## Workstreams (for Copilot Delegation)

| WS | Scope | What changes |
|----|-------|--------------|
| A | Model identifiers | `exploration-workflow/SKILL.md`, `dispatch-strategies.md` — dashes→dots |
| B | Gotchas sections | Add `## Gotchas` to 5 SKILL.md / agent files |
| C | Consistency fixes | `hard-gate-enforcement.md` Q5 update; intake-agent template path |
| D | HANDOFF_BLOCK | Structured completion signals in 3 child skills |
| E | Domain patterns | Create `references/domain-patterns/exploration-session.md` + README |
| F | Evals fill-in | Replace stub prompts in `evals/evals.json` with real routing cases |
| G | dispatch.py | `--model` flag + `--tier` flag for tier-aware sandboxing |
| H | session_end hook | New `hooks/session_end.py` + update `hooks/hooks.json` |

Workstreams A–F and H: agent/skill/reference/json file changes → delegate to Copilot Sonnet 4.6.
Workstream G: Python script changes → delegate to Copilot Sonnet 4.6.

---

## Delegation Plan

1. Create dense prompt at `tasks/todo/copilot_prompt_0018.md`
2. Dispatch to `claude-sonnet-4.6` via `run_agent.py`
3. Review output (diff all changed files)
4. Audit symlinks after any skill edits
5. Commit to feature branch, PR, merge

---

## Status

- [x] A — Model identifier fixes
- [x] B — Gotchas sections
- [x] C — Consistency fixes
- [x] D — HANDOFF_BLOCK signals
- [x] E — Domain patterns layer
- [x] F — Evals fill-in
- [x] G — dispatch.py improvements
- [x] H — session_end hook
- [x] Symlink audit
- [x] Commit and PR (merged in PR #317 and #318)
