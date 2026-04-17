---
concept: agent-harness-learning-layer-formerly-agentic-os
source: plugin-code
source_file: agent-agentic-os/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.122161+00:00
cluster: memory
content_hash: 4d59c3ec8c1eade8
---

# Agent Harness & Learning Layer (formerly Agentic OS)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Harness & Learning Layer (formerly Agentic OS)

A developer **meta-harness** that gives your AI agent **persistent memory**, a **self-improving feedback loop**, and **cross-IDE orchestration** — helping solo developers coordinate workflows and continuously improve skills with every execution across multiple environments (VS Code, Cursor, Windsurf, Copilot).

A *harness* controls what information a model sees at each step: prompting, context management, memory retrieval, and tool orchestration. A *meta-harness* adds an outer loop that searches over and improves the harness itself. This plugin is both: the memory and coordination layer is the harness; the `os-eval-runner` + `triple-loop-architect` orchestration is the meta-layer that evolves the harness's own skills and protocols continuously.

This architecture is independently validated by Meta-Harness (Lee et al., arXiv:2603.28052, 2026), which demonstrates that code-space search over harness definitions — using an LLM proposer with access to prior candidates and evaluation traces — outperforms hand-designed harnesses by significant margins across benchmarks. See [`plugin-research/meta-harness/`](../../plugin-research/meta-harness/) for the full analysis.

> **Positioning:** Anthropic now ships auto-memory, native hooks, and subagent coordination natively. This plugin is not an operating system, but rather an **opinionated discipline layer** on top of those primitives — a structured meta-harness for solo developer workflows. See [`SUMMARY.md`](./SUMMARY.md) for full context and known limitations.

---

## The Problem

Claude Code ships persistent memory. What it gives you is a 200-line `MEMORY.md` with no structured deduplication, no promotion logic, and no eval gate. That works for a few sessions. It breaks down when you have multiple agents, background loops, and workflows that span days or weeks where the quality of what gets remembered directly affects the quality of every future session.

The harder problem: coordination. How does the background improvement agent share what it learned with the foreground session? How does an outer-loop supervisor pass context to an inner-loop worker? How do two agents write to shared memory without corrupting it?

This plugin provides a system for that.

---

## What It Does

### Structured Memory Hierarchy

Every session writes structured logs to `context/events.jsonl` and `context/memory/`. At end-of-session, the `os-memory-manager` deduplicates and promotes important facts to `context/memory.md` - a curated long-term store that bootstraps every future session. Dedup IDs, conflict detection, and size limits prevent the memory from drifting into contradiction over hundreds of sessions.

### Continuous Improvement Loop (The Meta-Harness Layer)

### Continuous Improvement Loop (The Meta-Harness Layer)

This is the system's core differentiator: a unified **Triple-Loop Learning System** that continuously improves the instructions the model receives based on objective evaluation.

```text
TRIPLE-LOOP (Outer Meta-Learning Orchestrator via os-improvement-loop/nightly-evolver):
  Runs automated loops unattended
    -> oversees all experiments and delegates strategic targets
    -> reviews cross-loop patterns to improve OS-level protocols 

DOUBLE-LOOP (Strategic Planner via os-skill-improvement):
  Session runs
    -> errors and friction logged to events.jsonl
    -> formulates hypotheses and generates strategy packets 

SINGLE-LOOP (Tactical Executor via os-eval-runner):
    -> executes the patch against a SKILL.md (The Target)
    -> scores it against locked evals/evals.json fixtures (Headless Evaluation)
    -> if DISCARD: auto-reverted via git checkout; if KEEP: retained for next session
```

The loop relies strictly on headless evaluation — no subjective LLM "mental" testing — defeating Goodhart's Law. A test registry prevents re-testing falsified hypotheses. The plugin applies this loop to its own skills: it is a live lab as much 

*(content truncated)*

## See Also

- [[agent-harness-summary]]
- [[agentic-os-setup-orchestrator]]
- [[os-health-check-sub-agent]]
- [[agentic-os-architecture]]
- [[canonical-agentic-os-file-structure]]
- [[agentic-os---future-vision]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/README.md`
- **Indexed:** 2026-04-17T06:42:09.122161+00:00
