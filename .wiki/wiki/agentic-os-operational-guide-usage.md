---
concept: agentic-os-operational-guide-usage
source: plugin-code
source_file: agent-agentic-os/USAGE.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.687159+00:00
cluster: evolution
content_hash: 61a467111107a100
---

# Agentic OS — Operational Guide & Usage

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agentic OS — Operational Guide & Usage

> While the architectural blueprints define the *Why* (the control-plane guarantees, state machines, and learning invariants), this document dictates the *How*. It maps out how a human or external caller interacts with the system to start the full improvement lifecycle.

---

## 1. The Human / Caller Entry Point

### Recommended: `/os-architect`

The practical entry point for any evolution activity is:

```
/os-architect
```

Describe what you want in plain language. The os-architect agent classifies your intent into one of 5 categories, audits what capabilities already exist, proposes the right evolution path (orchestrate existing / update existing / create new), and dispatches implementation work via your available CLI tools. You do not need to know which sub-agent to invoke, whether a capability exists, or how to configure a run.

**Intent categories os-architect handles:**
1. Pattern Abstraction — applying a new way of working to existing skills/agents
2. Research Application — incorporating techniques from papers or external research
3. Lab Setup / Improvement Loop — running eval iterations on an existing skill
4. Capability Gap Fill — creating a new skill or agent that doesn't exist yet
5. Multi-Loop Orchestration — coordinating parallel improvement loops

### Advanced: Direct sub-agent invocation

For users who know exactly what they want, sub-agents can be invoked directly:

```bash
# Configure a skill improvement run directly
# → improvement-intake-agent

# Set up a full triple-loop eval lab
# → triple-loop-architect agent

# Run unattended overnight iterations
# → triple-loop-orchestrator agent

# Verify that os-architect actually caused evolution (post-run)
# → os-evolution-verifier skill

# Query or summarize experiment history
# → os-experiment-log skill
```

### Low-level: kernel.py submission

For programmatic or scripted invocation, the kernel accepts direct task submissions:

```bash
python3 plugins/agent-agentic-os/scripts/kernel.py emit_event \
  --agent improvement-intake-agent \
  --type lifecycle \
  --action intake-complete \
  --status success \
  --summary "target_skill — run depth configured"
```

---

## 2. The Experiment Log

Every experiment run — whether from os-evolution-verifier, os-architect-tester,
triple-loop-orchestrator, or os-evolution-planner — is persisted to a durable, folder-based
log. This is the unified cross-cutting record across all evolution activity.

```
context/experiment-log/
  index.md                            ← one row per run (date, source, target, verdict)
  2026-04-25-verifier-round1.md       ← qualitative: PASS/FAIL/PARTIAL per scenario
  2026-04-25-orchestrator-skill.md    ← numeric: best_score, baseline, delta, KEEP/DISCARD
  2026-04-25-tester-os-architect.md   ← qualitative: AC-1–4 per scenario
  2026-04-25-planner-0024.md          ← qualitative: workstream count, gaps identified
  2026-04-25-survey-session.md        ← mixed: friction items + north_star metric
```

**Result types agents must distinguish:**
- `numeric` — carries quantitative scores suitable for charting and trending (orchestrator)
- `qualitative` — carries pass/fail verdicts and gap analysis prose (verifier, tester, planner)
- `mixed` — carries both; check which fields are present before parsing (survey)

**Appending to the log** (run after every experiment):
```bash
python3 plugins/agent-agentic-os/scripts/experiment_log.py append \
  --source-type verifier \          # verifier | tester | orchestrator | planner | survey
  --report temp/os-evolution-verifier/test-report.md \
  --session-id 2026-04-25-round1 \
  --target os-architect \
  --triggered-by os-evolution-verifier

python3 plugins/agent-agentic-os/scripts/experiment_log.py summary
python3 plugins/agent-agentic-os/scripts/experiment_log.py query FAIL
```

---

## 3. The Skill as the Unit of Work (Lifecycle)

The "Skill" is the atomic unit the improvement lifecycle operates on. It is the durable knowl

*(content truncated)*

## See Also

- [[agentic-os-guide]]
- [[agent-agentic-os-hooks]]
- [[after-os-evolution-verifier-run]]
- [[no-direct-usage-shared-module]]
- [[os-architect-test-report-scenario-id]]
- [[os-state-json]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/USAGE.md`
- **Indexed:** 2026-04-27T05:21:03.687159+00:00
