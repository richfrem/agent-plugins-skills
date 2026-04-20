# Ecosystem Bake-Off: Spec-Kitty vs. Organic Stack

**Goal:** Stop architecting in the abstract. Test both workflows side-by-side using a dead-simple, real-world task. Let empirical data (metrics) dictate which stack we keep or deprecate.

---

## The Core Thesis: Transitional Architectures
As we evaluate these ecosystems, we must explicitly acknowledge the reality of the current AI landscape:
1. **We cannot change the underlying Frontier Models.**
2. **We cannot change what the SDKs natively support.**
3. **The landscape changes weekly.** Workflows that were revolutionary six months ago are obsolete today.

Because of these immutable facts, frameworks like `spec-kit`, `spec-kitty`, `superpowers`, and `germes-agent` are fundamentally **Transitional Architectures**. We operate under the working hypothesis that large portions of their core mechanics (like prompt-driven worktree management or manual memory files) will be temporary and eventually replaced by native features.

Therefore, the purpose of this repository is to **strictly decouple business logic (Skills) from the underlying agent usage.** We must not lock our workflows into the proprietary quirks of any single transitional framework. The absolute most critical feature we are testing across any stack is the **Continuous Improvement Loop**—ensuring that decoupling allows our skills, workflows, and agents to organically improve themselves after every run, regardless of what SDK executes them. 

---

## The Challenge: A Trivial Task
**Build a simple Python utility (`parser.py`) that parses a CSV file and calculates the average value of a specific column, handling common errors (missing files, malformed rows).**

*Why so trivial?* We are trying to measure the friction of the **frameworks**, not the intelligence of the model. By keeping the coding task dead simple, any errors, amnesia, or token bloat can be 100% attributed to the overhead of Spec-Kitty or the Organic Stack failing to manage the flow.

## Hypotheses & Predictions
Before running the experiment, here is the architectural prognosis of how these two stacks will behave under stress:

* **Prediction 1 (Overhead):** Spec-Kitty will consume 3x to 5x more tokens and take significantly longer just to start writing code, because its SDD lifecycle forces the generation of `spec.md`, `plan.md`, and `tasks.md` before it touches Python.
* **Prediction 2 (State Breakage):** Spec-Kitty will struggle with Git branching and kanban lane transitions, repeatedly requiring human intervention ("Please merge this"). The Organic Stack will proceed fluidly because it relies on standard TDD loops rather than proprietary CLI commands and file moves.
* **Prediction 3 (Amnesia):** The Organic Stack may lose sight of the "big picture" requirements because it lacks a formal `spec.md`, but it will produce working, tested code faster due to the Superpowers TDD execution rules. Spec-Kitty will produce a beautiful checklist, but the agent will forget to follow it when it actually starts writing `parser.py`.

---

## The Testing Grounds

### Run A: The Rigid Framework (`run-A-spec-kitty/`)
1. CD into `run-A-spec-kitty/`.
2. Initialize `spec-kitty init .`
3. Tell the agent: "Use spec-kitty to build a CSV parsing utility that calculates the average of a column."
4. **Constraint:** The agent *must* follow the rigid Spec-Driven Development lifecycle (specify -> plan -> tasks -> implement -> review -> merge).

### Run B: The Organic Stack (`run-B-organic-stack/`)
1. CD into `run-B-organic-stack/`.
2. Initialize the agentic OS (`python kernel.py init` or similar). Ensure the `superpowers` execution skills are loaded.
3. Tell the agent: "Build a CSV parsing utility that calculates the average of a column using strict TDD."
4. **Constraint:** Let the agent govern itself organically with the event bus and execution rules (TDD, verification-before-completion) without a formal Spec-Kitty Kanban board.

---

## Evaluation Rubric (To Record After Runs)

### 1. Efficiency & Overhead
* **Total Token Usage:** (Estimate or log tokens burned from start to finish).
  * *Run A (Spec-Kitty):* ___
  * *Run B (Organic Stack):* ___
* **Administrative Complexity/Tax:** (How many files/folders were mandated just to start coding?)
  * *Run A:* ___ files/folders
  * *Run B:* ___ files/folders

### 2. Reliability & Execution Mistakes
* **Workflow Amnesia:**
  * *Run A:* Did it forget steps? Did it write code before the task was reviewed? Did it skip its markdown checklist?
  * *Run B:* Did it successfully follow TDD rules natively? Did it break any OS locks?
* **Git Tree & Worktree Management Errors:**
  * *Run A:* Number of detached HEAD states, wrong branches, or `/spec-kitty.implement` parsing failures.
  * *Run B:* Number of branch/commit tracking errors without the heavy CLI.
* **Execution Mistakes:**
  * Total number of times the agent wrote code that strictly threw a traceback error.
  * *Run A:* ___ mistakes
  * *Run B:* ___ mistakes

### 3. Autonomy & Context Preservation
* **Loss of Context / "Getting Stuck":**
  * Number of times the agent threw its hands up, asked for clarification, entered an infinite error loop, or hallucinated an objective because it forgot what to do.
  * *Run A:* ___ instances
  * *Run B:* ___ instances
* **Quality of Completion:**
  * Which agent actually built a functioning CSV parser *first* without needing human rescue?
  * *Run A:* [Pass/Fail]
  * *Run B:* [Pass/Fail]

## Broader Architectural Question: Soft Plugins vs. Native SDKs
You have rightly noted a deep architectural worry: **Why build fragile Markdown plugins when the Claude Agent SDK could theoretically handle this natively?**

This is fundamentally a "point in time" problem in agentic engineering. There is a profound redundancy in the current ecosystem because we are forced to build plugins for things that should be **Core SDK** features. Functions like **Memory Management, Git Worktree isolation, and Execution State serialization** belong natively inside the Agent SDK.

Building custom markdown `skills` to force an agent to read/write a `memory.md` file or switch git branches is a brittle, temporary workaround for features the native SDKs have not yet shipped.

* **What belongs in Core:** Memory Management, Worktrees, Event Buses, and **Agent Orchestration** (swarms, delegation, state handoffs).
  * *Note:* It is objectively absurd that developers currently have to write 300-line "Git Worktree" plugins just to teach an agent how to branch safely, or massive prompt-chaining skills just to route a task to a specialized sub-agent. Fundamental state isolation and workflow orchestration belong strictly inside the agent's native runtime environment.
* **What belongs in Plugins (Extensions):** True domain-specific workflows (e.g., `excel-to-csv`, `obsidian-bases-manager`, or custom enterprise `exploration-cycles`).

Furthermore, **not all frontier models do what Claude does.** The capability gaps between `claude-cli`, Copilot, Codex, and `gemini-cli` mean that relying on "native SDK features" is a moving target. The frameworks we build must act as an agnostic bridge across this fragmented topography.

**The Ultimate Prediction: The Death of Custom Plumbing**
We anticipate that the frontier models (Anthropic, OpenAI, Google) will inevitably take the lead in providing the "low-level plumbing"—native memory persistence, multi-agent orchestration, environment loops, and secure worktrees. When this happens, large swaths of architectures like `spec-kit` and `agent-agentic-os` will be happily discarded. 

However, **Skills and Plugins (domain-specific business logic) will endure.** By building our skills independently of the plumbing today, we ensure that when the frontier models finally release their native orchestration engines, our skills will drop into them seamlessly without needing a rewrite. 

Therefore, this bake-off is not about blaming Spec-Kitty or Superpowers for being "duct-tape." It is an empirical test to discover **which duct-tape framework is currently the least painful and most aggressively agnostic to maintain:** 
* Do we survive the SDK gaps better by forcing the agent to read rigid English Kanban checklists (Spec-Kitty / Run A)?
* Or do we survive better by building a custom Python Event Bus and enforcing strict local TDD rules (Organic OS / Run B)?

This experiment will tell us which gap-filling strategy to double down on until the industry native SDKs finally catch up.

---

## The Verdict

*Once both runs are complete, write your conclusion here. Did the rigid planning of Spec-Kitty prevent bugs, or did it just waste tokens and break? Did the Organic Stack execute faster, or did it lose context without a written plan?*

* **Decision:** [Keep Spec-Kitty / Deprecate Spec-Kitty / Merge Best Concepts]
