---
concept: changelog
source: plugin-code
source_file: agent-agentic-os/CHANGELOG.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.685977+00:00
cluster: skill
content_hash: 1d8bea0d1c22f622
---

# Changelog

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Changelog

All notable changes to `agent-agentic-os` are documented here.

## v1.6.0

### Removed
- `agents/triple-loop-architect.md` — merged into os-improvement-loop as `--lab` invocation mode
- `agents/triple-loop-orchestrator.md` — same; os-improvement-loop handles multi-iteration runs natively
- `skills/os-skill-improvement/` — function absorbed by os-improvement-loop; not a distinct capability
- `references/sample-prompts/triple-loop-architect-prompt.md`

### Changed
- `agents/os-architect-agent.md`: Category 3 routing now delegates to os-improvement-loop directly;
  Routing Decision Audit block added to all HANDOFF_BLOCK outputs; skill creation threshold added
- `skills/os-improvement-loop/SKILL.md`: os-skill-improvement references removed; eval budget guard added
- `plugin.json`: deprecated entries removed from agents, skills, keywords, capabilities
- `README.md`: triple-loop rows removed; Utilities section added; How It Works reframed

## [1.5.0] - 2026-04-25

### os-architect — Front-Door Evolution Intake
- **New agent**: `agents/os-architect-agent.md` — interactive conductor that classifies user intent into 5 categories (Pattern Abstraction, Research Application, Lab Setup, Gap Fill, Multi-Loop Orchestration), audits the ecosystem, proposes Path A/B/C, and dispatches via `run_agent.py`. Replaces the "where do I start" problem in agent-agentic-os.
- **New skill**: `skills/os-architect/SKILL.md` — slash command entry point (`/os-architect`)
- **New evals**: `skills/os-architect/evals/evals.json` — 19 routing cases with `expected_category` field (1–5) on all TP cases and 4 misrouting-risk boundary cases
- **Confidence-aware classification**: Phase 1 classification block includes `Confidence: High | Medium | Low`; Low confidence triggers a clarifying question before proceeding to audit
- **Path A+ (no-op path)**: When audit shows Full match + current + all self-healing patterns present, agent tells user "no action needed" rather than forcing a path
- **Category 5 dispatch spec**: Multi-Loop Orchestration now has a concrete per-target sequential dispatch protocol in Phase 3

### os-evolution-verifier — Evolution Artifact Verification Skill
- **New skill**: `skills/os-evolution-verifier/SKILL.md` — dispatches os-architect in single-shot simulation mode for a given test scenario, checks artifact presence via grep/file-exists (not transcript review), and reports PASS/FAIL with evidence. Uses structured EVOLUTION_VERIFICATION output block with VERDICT: PASS | PARTIAL | FAIL. Accumulates results into `temp/os-evolution-verifier/test-report.md`.
- **New evals**: `skills/os-evolution-verifier/evals/evals.json` — 10 routing cases covering explicit verifier invocations vs. general architect queries
- **PARTIAL verdict**: More precise than binary pass/fail — pinpoints which specific workstream failed

### os-experiment-log — Persistent Experiment Log Skill
- **New skill**: `skills/os-experiment-log/SKILL.md` — append-only log of evolution verification runs at `context/experiment-log.md`. Three modes: `append` (post-run), `query <term>` (search by scenario ID/verdict), `summary` (aggregate stats). Closes the loop on learnings — every test run leaves a durable record with actions taken.
- **New evals**: `skills/os-experiment-log/evals/evals.json` — 8 routing cases
- **Initialized**: `context/experiment-log.md` — empty log ready to receive first run

### os-evolution-planner — Repeatable Plan-and-Delegate Skill
- **New skill**: `skills/os-evolution-planner/SKILL.md` — given a target and evolution goal, applies the self-healing diagnostic lens, writes a structured task plan (`tasks/todo/<slug>-plan.md`), and writes a dense Copilot CLI delegation prompt. Called by os-architect for Path B/C executions.

### os-architect-tester — Scenario-Based Validation Agent
- **New agent**: `agents/os-architect-tester-agent.md` — runs pre-scripted scenario transcripts through os-architect via Copilot CLI and evaluates against 4 acceptance criteria 

*(content truncated)*

## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/CHANGELOG.md`
- **Indexed:** 2026-04-27T05:21:03.685977+00:00
