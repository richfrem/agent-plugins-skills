---
concept: agent-loop-patterns
source: plugin-code
source_file: exploration-cycle-plugin/references/agent-loop-patterns.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.582065+00:00
cluster: plugin-code
content_hash: 3fba024b9dd02fe3
---

# Agent Loop Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Loop Patterns

The exploration-cycle and agentic OS systems utilize a progression of loop architectures based on the complexity of the task and the need for autonomy vs. precision.

## Learning Loop (Single-Loop)

**Purpose**: Tactical execution and solo framing/research where no sub-agent delegation is required. The agent reads the brief, explores, and iterates within context.
- **Architecture**: `plugins/agent-loops/references/learning-loop-architecture.md` (or core agent design)
- **Primary Skill**: `plugins/agent-loops/skills/learning-loop/SKILL.md`
- **Use Case**: Solo discovery sessions where the agent just needs to acquire knowledge and maintain continuity.

## Dual Loop (Double-Loop)

**Purpose**: Strategic reframing combined with tactical execution. The outer loop challenges assumptions and mental models, while the inner loop executes the tactics.
- **Architecture**: `plugins/agent-loops/references/dual-loop-architecture.md`
- **Primary Skill**: `plugins/agent-loops/skills/dual-loop/SKILL.md`
- **Use Case**: Often used implicitly by `os-improvement-loop` to evolve agent behaviors and rules. Useful when the problem statement itself needs to be validated before solving.

## Triple Loop (Automated Autoresearch)

**Purpose**: Continuous, self-improving orchestration across multiple isolated evaluation sessions. It utilizes sibling repo labs to experiment autonomously.
- **Architect/Agent**: `plugins/agent-agentic-os/agents/triple-loop-architect.md`
- **Primary Skill**: `plugins/agent-agentic-os/skills/triple-loop-learning/SKILL.md`
- **Use Case**: The standard for robust execution and continuous improvement. In the Exploration Cycle, the triple-loop pattern is invoked when orchestrating multiple detached passes (like dispatching the `requirements-doc-agent` iteratively for complex captures).

---

By referencing this unified structure, skills and sub-agents can dynamically scale from a simple inner `learning-loop` all the way to a robust `triple-loop` evaluation harness.


## See Also

- [[concurrent-agent-loop]]
- [[dual-loop-innerouter-agent-delegation]]
- [[dual-loop-innerouter-agent-delegation]]
- [[dual-loop-innerouter-agent-delegation]]
- [[dual-loop-innerouter-agent-delegation]]
- [[concurrent-agent-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/references/agent-loop-patterns.md`
- **Indexed:** 2026-04-17T06:42:09.582065+00:00
