<!-- PATCH: Replacement for Phase 4c, Phase 5, and Routing After Handoff in improvement-intake-agent.md -->
<!-- Insert Phase 4c after existing Phase 4b. Replace Phase 5 and Routing After Handoff entirely. -->

### 4c — Emit Kernel Event

After both files are written, register this agent (if needed) and emit the intake-complete event:

```bash
# Ensure improvement-intake-agent is in context/agents.json
if [ -f context/agents.json ]; then
  python -c "
import json, sys
d = json.load(open('context/agents.json'))
if 'improvement-intake-agent' not in d.get('permitted_agents', []):
    d.setdefault('permitted_agents', []).append('improvement-intake-agent')
    json.dump(d, open('context/agents.json', 'w'), indent=2)
    print('[Intake] Registered agent in context/agents.json')
"
fi

python scripts/kernel.py emit_event \
  --agent improvement-intake-agent \
  --type lifecycle \
  --action intake-complete \
  --status success \
  --summary "Intake complete for $(jq -r .target_skill improvement/run-config.json) — $(jq -r .run_depth.label improvement/run-config.json) run configured"
```

---

## Phase 5 — Handoff

Tell the user:

> "All set. Your run is configured at `improvement/run-config.json` and the session brief
> is at `improvement/session-brief.md`.
>
> When you're ready, say **'start the run'** and the improvement lifecycle will begin.
> It will keep you updated as it goes — you don't need to watch it closely."

If baseline was requested, add:

> "We'll run a quick baseline first so we have something to measure improvement against.
> That should only take a few minutes before the main run begins."

Then output the machine-readable handoff block for downstream agent consumption:

```
## HANDOFF_BLOCK
CONFIG: improvement/run-config.json
BRIEF: improvement/session-brief.md
ENTRY_STATE: IDLE
FIRST_ACTION: [baseline | hypothesis_0]
CROSS_PERSONA: [true | false — from run-config.json]
SEED_GOTCHAS: [N — count from seed_gotchas array]
DISPATCH: [copilot-cli | gemini-cli | claude-subagents — from run-config.json]
```

---

## Routing After Handoff

Once the user says "start the run", hand off to `improvement-lifecycle-orchestrator`.
The orchestrator reads the `HANDOFF_BLOCK` above and the files it references.

The orchestrator owns everything from IDLE → RUNNING onward.
The intake agent does not re-enter once the run has started, unless the user explicitly
restarts intake (e.g. to change the target skill or reset the run depth).
