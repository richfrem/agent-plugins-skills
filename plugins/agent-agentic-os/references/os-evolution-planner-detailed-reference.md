# os-evolution-planner — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Phase 1 — Brainstorm prompt and presentation templates

**Brainstorm prompt template:**
```
Evolution goal: <goal>
Target: <target skill/agent>
Current gaps detected: <gap list>

Generate exactly 3 distinct approaches to this evolution goal. For each:
- Approach name (2-4 words)
- What it does (2-3 sentences)
- What it trades off (1 sentence)
- Estimated effort: [Small / Medium / Large]
```

**Present options to user:**
```
Here are 3 approaches to <goal>:

**Option A — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

**Option B — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

**Option C — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

My recommendation: **Option <X>** — <one-line reason>.
Which would you like to proceed with? (A / B / C / modify)
```

Wait for the user to select before proceeding to Phase 2.

## Phase 3 — Output Format (full templates)

**Task plan** written to `tasks/todo/<YYYY-MM-DD>-<slug>-plan.md`:

```markdown
# <task-number> — <title>

## Context
[What triggered this evolution, what was found]

## Approach Selected
Option <X> — <name>: <one-line description of chosen approach and why>
(Options considered: <A>, <B>, <C> — see brainstorm output for tradeoffs)

## Gaps Identified
[One bullet per gap found by the detection lens]

## Workstreams
| WS | Scope | Delegate to |
...

**WS ordering rule**: Structural fixes (model identifiers, path bugs, security flags) MUST
be listed as the first workstreams. Additive content (Gotchas, HANDOFF_BLOCK, domain
patterns, smoke tests) comes after. The delegated agent executes workstreams in listed order.

## Delegation Plan
1. Delegation prompt at tasks/todo/copilot_prompt_<slug>.md
2. Dispatch via run_agent.py with claude-sonnet-4.6
3. Review output (diff, symlink audit)
4. Commit and PR: If modifying code/logic in `plugins/`, `src/`, or `py_services/`, ensure `references/map-debt.md` or `references/evolution-log.md` is updated and staged in the commit, or include `Evolution-Check: none` in the commit message to satisfy the pre-commit and CI evolution integrity gate.

## Status
- [ ] WS-A ...
```

**Delegation prompt** written to `tasks/todo/copilot_prompt_<slug>.md`:
- One section per workstream with exact file paths and content specifications — listed in order: structural fixes first, then additive content
- Global instruction: "Use the Write tool to write files directly — do not output delimiters"
- Completion checklist section at the end with COMPLETION_REPORT format (including Map Debt / Evolution Log verification)

## Step 4 — Dispatch via copilot-cli-agent skill (full detail)

If the `--dispatch` flag is set (or the user confirms dispatch), run the heartbeat then dispatch:

Invoke the `copilot-cli-agent` skill with the following parameters:

1. **Heartbeat check** (always first):
   - **prompt_file**: `/dev/null`
   - **context**: `/dev/null`
   - **output**: `temp/heartbeat_<slug>.md`
   - **instruction**: "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."
   - **model**: `gpt-5-mini`

   Verify heartbeat before premium dispatch:
   ```bash
   grep -q "HEARTBEAT_OK" temp/heartbeat_<slug>.md || (echo "HEARTBEAT FAIL — aborting dispatch" && exit 1)
   ```

2. **Main Dispatch**:
   - **prompt_file**: `tasks/todo/copilot_prompt_<slug>.md`
   - **context**: `/dev/null`
   - **output**: `temp/copilot_output_<slug>.md`
   - **instruction**: "Generate all files exactly as specified. Use the Write tool to write files directly."
   - **model**: `claude-sonnet-4.6`
   - **mode**: `non-interactive`

   After dispatch, verify output before claiming complete:
   ```bash
   wc -l temp/copilot_output_<slug>.md  # expect 100+ lines for multi-workstream output
   test -s temp/copilot_output_<slug>.md || echo "ERROR: empty output — copilot-cli-agent dispatch failed"
   ```

After dispatch completes (or after plan is written if dispatch is off), log to experiment log:
```bash
python3 plugins/agent-agentic-os/scripts/experiment_log.py append \
  --source-type planner \
  --report tasks/todo/<slug>-plan.md \
  --session-id "<slug>" \
  --target "<target-skill-or-agent>" \
  --triggered-by os-evolution-planner
```
This records the workstream count and gaps identified as a qualitative entry in
`context/experiment-log/` — traceable alongside any subsequent verifier or tester runs.

If dispatch flag is NOT set, present the plan and prompt paths and ask:
> "Plan written to `tasks/todo/<slug>-plan.md` and delegation prompt to
> `tasks/todo/copilot_prompt_<slug>.md`. Dispatch to Copilot CLI now? (yes / review first)"

## Gotchas

- **Always brainstorm before planning**: Even if the "right" approach seems obvious, running Phase 1 costs near-zero tokens and frequently surfaces a simpler or more composable alternative the first instinct missed.
- **Brainstorm prompt must include current gaps**: Without gap context, the cheap model produces generic approaches. Pass the full gap list from Phase 2 detection into the brainstorm prompt.
- **Gap detection reads source files, not installed `.agents/` files**: Always read from `plugins/<plugin>/skills/<skill>/SKILL.md` — the installed `.agents/` copy may be stale.
- **Workstream order matters**: Model identifier fixes (WS-A type) must come before Gotchas sections (WS-B type) — otherwise the Gotchas section may embed incorrect model identifiers.
- **Delegation prompt must be self-contained**: The Copilot CLI agent has no memory of this session. Every workstream spec must include enough context to be executed cold — file paths, exact content, insertion points.
- **Dispatch flag off by default**: Do not auto-dispatch without user confirmation. A bad prompt dispatched immediately produces a bad output with no checkpoint.

## Smoke Test

1. Given target = `os-eval-runner` skill, Phase 1 produces 3 named approaches with effort estimates before any plan file is written.
2. After user selects an option, the plan file includes an "Approach Selected" section naming the chosen option and noting alternatives considered.
3. Given `--dispatch` flag set and heartbeat passes, the skill calls `run_agent.py` with `claude-sonnet-4.6` and verifies output line count before reporting complete.
