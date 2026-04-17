---
concept: strengths-and-gaps-analysis
source: research-docs
source_file: superpowers/strengths-and-gaps.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.465878+00:00
cluster: agent
content_hash: 015d13edfe2db12d
---

# Strengths and Gaps Analysis

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Strengths and Gaps Analysis

---

## Section 1: What agent-agentic-os Does Well

### 1.1 Structured Memory with Conflict Detection

The three-tier memory hierarchy (MEMORY.md auto / context/memory.md curated L3 / context/memory/YYYY-MM-DD.md session logs L2) is the most sophisticated memory design in the three plugins. The "dementia guard" in `skills/session-memory-manager/SKILL.md` - requiring a Read scan of L3 before any append to detect contradictions - is a genuine engineering discipline absent from both comparators. The deduplication IDs and the explicit conflict-pause-for-human-intervention protocol prevent the silent corruption that afflicts naive append-only memory.

### 1.2 Eval-Gated Self-Improvement

The feedback control loop is the system's core architectural differentiator. `skills/skill-improvement-eval/SKILL.md` implements a Karpathy autoresearch-style evaluation cycle: propose a patch, run `eval_runner.py` against `evals.json`, compare to baseline in `results.tsv`, KEEP only if score improves. `agents/os-learning-loop.md` mines `context/events.jsonl` for friction events and proposes patches without requiring manual inspection. The `skills/concurrent-agent-loop/SKILL.md` improvement ledger (`improvement-ledger-spec.md`) tracks longitudinal score progression, survey-to-action traces, and Autonomous Workflow Completion Rate across cycles - a genuine learning flywheel, not a one-shot tuning exercise.

### 1.3 OS Mental Model and Lazy Loading Architecture

The OS metaphor in `SUMMARY.md` and `references/architecture.md` is not decorative. The three-tier lazy loading design - always-loaded skill metadata, loaded-on-trigger full SKILL.md body, loaded-on-demand references/ documents - reflects a real constraint (context window as finite RAM) and a real discipline (never auto-load events.jsonl or session logs). The `references/canonical-file-structure.md` and `references/context-folder-patterns.md` give the system a consistent physical structure that agents can navigate without instruction.

### 1.4 Agent Coordination Primitives

`skills/concurrent-agent-loop/SKILL.md` formalizes four coordination topologies (turn-signal, fan-out, request-reply, dual-loop). The dual-loop pattern with strategy packets, correction packets, PEER_AGENT independent eval, and ORCHESTRATOR decision emission is the most complete multi-agent coordination protocol in the three plugins. `context/kernel.py` with `acquire_lock`, `release_lock`, and stale-lock timeout prevents agent collisions on shared state.

### 1.5 Honest Self-Documentation

`README.md` and `SUMMARY.md` explicitly name the known vulnerabilities: keyword heuristic is a Goodhart's Law risk, no shadow mode validation, missing baseline floor requirement. The research references (`references/research/`) acknowledge academic grounding and competitive landscape. This transparency is rare and valuable.

---

## Section 2: What exploration-cycle-plugin Does Well

### 2.1 Real Evals with Actual Run Data

`evals/results.tsv` contains 12+ real iterations on a canonical waitlist scenario, including baseline runs, keep/discard decisions, confound analysis, and lessons from infrastructure failures (AWS Copilot CLI path collision, YAML frontmatter parse failure). This is not synthetic data - it is empirical evidence from actual agent execution. The baseline-first discipline and one-variable-per-iteration rule are correctly applied throughout. No other plugin in the set has this much real execution evidence in its repository.

### 2.2 Cheap-Model Sub-Agent Dispatch Architecture

The `dispatch.py` wrapper for Copilot CLI sub-agents solves a genuine problem: context truncation from pipe-based prompt injection. The explicit dispatch pattern in the README (showing the INVALID bash pipe approach vs the STANDARD dispatch.py approach) reflects hard-won operational experience. Dispatching the requirements-doc-agent "many times per session, cheap model, no context inheritance" is the correct architectur

*(content truncated)*

## See Also

- [[claudemd-hierarchy-and-scope-rules]]
- [[sub-agents-hooks-and-commands]]
- [[memory-hygiene-when-to-write-promote-and-archive]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[sub-agents-and-hooks]]
- [[sub-agents-and-hooks]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/strengths-and-gaps.md`
- **Indexed:** 2026-04-17T06:42:10.465878+00:00
