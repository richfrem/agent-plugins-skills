---
concept: post-run-survey-exploration-workflow
source: plugin-code
source_file: exploration-cycle-plugin/references/post-run-survey.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.585114+00:00
cluster: orchestrator
content_hash: 1c59f1d44a132c87
---

# Post-Run Survey: exploration-workflow

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Post-Run Survey: exploration-workflow

Use this survey after each exploration cycle, targeted sub-loop, or major re-entry from engineering.

## Run Metadata

- Run ID:
- Date:
- Scenario:
- Loop path: broad exploration, narrowing, targeted sub-loop, handoff, re-entry

## Ratings

Rate each from 1 to 5.

- The orchestrator chose the right next action.
- The orchestrator invoked the right specialized agents.
- The loop stayed broad when it needed exploration.
- The loop narrowed when it was actually ready.
- The produced artifacts were useful.
- The handoff timing was appropriate.
- Any re-entry into exploration was justified.
- The overall coordination reduced confusion rather than adding it.

## Count-Based Signals

- How many times did the orchestrator choose a clearly wrong next step?
- How many times did humans need to redirect the orchestrator?
- How many unnecessary agent invocations occurred?
- How many useful artifacts were produced?
- How many artifacts were created but not actually useful?
- How many times did the loop reopen after an apparently premature handoff?

## Qualitative Questions

1. Where did the orchestrator help the most?
2. Where did the orchestrator create friction or confusion?
3. Which agent routing decision was best?
4. Which routing decision was worst?
5. Did the orchestrator narrow too early, too late, or about right?
6. Did the re-entry behavior feel useful or chaotic?
7. What single change should be tested next?
8. Are there elements of the parent `agentic-os` plugin that should also be improved based on this exploration?

## Keep / Discard Recommendation

- Suggested decision for this orchestrator version: keep, discard, investigate
- Reason:

## See Also

- [[post-run-survey-exploration-orchestrator]]
- [[template-post-run-agent-self-assessment]]
- [[exploration-workflow-sme-orchestrator]]
- [[exploration-cycle-workflow]]
- [[template-post-run-agent-self-assessment]]
- [[template-post-run-agent-self-assessment]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/references/post-run-survey.md`
- **Indexed:** 2026-04-17T06:42:09.585114+00:00
