# 0020 — os-architect: Round-2 Red-Team Fixes

## Context

Round-2 red-team review (Claude, GPT, Gemini) of the os-architect bundle (PRs #319/#320).
Three reviewers identified concrete bugs and missing specs. Claude's review is the
highest-signal source; GPT adds two high-value enhancements. Gemini's kernel suggestions
are filtered — kernel.py exists but integration is a separate workstream.

Red-team reviews at: `temp/red-team-reviews/agentic-os-architect-agent/round2/`

---

## Gaps Identified

1. **evals.json classification-only** — 15 cases test trigger/no-trigger but not which
   intent category was selected. A prompt routed to Cat 3 instead of Cat 1 passes evals.
   No `expected_category` field; no misrouting-risk boundary cases (Cat 1 vs 2 confusion).

2. **Path bug in os-architect-agent.md** — Delegation Patterns section uses
   `.agents/skills/copilot-cli-agent/scripts/run_agent.py` (installed path, WS-F not done).
   Correct source path confirmed working: `plugins/copilot-cli/scripts/run_agent.py`.
   Tester agent already uses the correct path; architect agent does not.

3. **Category 5 has no Phase 3 dispatch spec** — taxonomy says "spawn multiple loops"
   but Phase 3 only covers Path A/B/C. Category 5 requests will produce hallucinated behavior.

4. **os-evolution-planner WS ordering rule is Gotchas-only** — ordering constraint
   ("structural fixes before additive content") exists in Gotchas but not in the delegation
   prompt template. Delegated agent won't see it.

5. **No confidence model** — classification confirmation block has no CONFIDENCE field.
   Ambiguous multi-intent prompts get forced into a single category, causing misroutes.

6. **No no-op path** — when a capability audit returns Full match + current + no gaps,
   the agent has no protocol for "nothing to do." Without it, it will force a path even
   when none is warranted, wasting improvement loop compute.

7. **improvement-intake-agent patch unapplied** — WS-E from task 0019.
   `agents/improvement-intake-phase4c-5-patch.md` adds Phase 4c (kernel event emission)
   and HANDOFF_BLOCK to the intake agent. os-architect depends on clean HANDOFF_BLOCK
   output from it for Category 3 requests. Manual apply required.

---

## Workstreams

| WS | Scope | File(s) | Delegate to |
|----|-------|---------|-------------|
| A | evals.json: add `expected_category` + misrouting cases | `skills/os-architect/evals/evals.json` | Copilot claude-sonnet-4.6 |
| B | Path bug: fix run_agent.py path in architect agent | `agents/os-architect-agent.md` | Copilot claude-sonnet-4.6 |
| C | Category 5 Phase 3 spec | `agents/os-architect-agent.md` | Copilot claude-sonnet-4.6 |
| D | os-evolution-planner: add WS ordering to template | `skills/os-evolution-planner/SKILL.md` | Copilot claude-sonnet-4.6 |
| E | Confidence-aware classification | `agents/os-architect-agent.md`, `skills/os-architect/SKILL.md` | Copilot claude-sonnet-4.6 |
| F | No-op path (Path A+) | `agents/os-architect-agent.md`, `skills/os-architect/SKILL.md` | Copilot claude-sonnet-4.6 |
| G | Apply improvement-intake patch | `agents/improvement-intake-agent.md` | **Manual — diff review required** |

All WS paths are relative to `plugins/agent-agentic-os/`.

---

## Delegation Plan

1. Delegation prompt at `tasks/todo/copilot_prompt_0020.md`
2. Dispatch WS-A through F via `run_agent.py` with `claude-sonnet-4.6` (batch all into one request)
3. Review output diff for all changed files
4. Apply WS-G manually by diffing patch file against agent file
5. Symlink audit after edits
6. Commit and PR

---

## Status

- [x] A — evals.json classification upgrade
- [x] B — Path bug fix
- [x] C — Category 5 Phase 3 spec
- [x] D — os-evolution-planner WS ordering enforcement
- [x] E — Confidence-aware classification
- [x] F — No-op path
- [ ] G — improvement-intake patch (manual)
- [ ] Symlink audit + plugin_add.py install
- [x] Commit (dispatch agent committed: 9714cd92)
