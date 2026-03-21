---
name: skill-improvement-eval
description: >
  Trigger with "evaluate this skill", "run tests on the new skill", "check if this change breaks anything", 
  "eval the learning loop proposal", or when an agent (like `os-learning-loop`) proposes a change to an 
  existing skill and needs empirical validation before writing it to disk.

  <example>
  Context: `os-learning-loop` just proposed a fix to a broken skill.
  os-learning-loop:
  <Bash>
  cat << 'EOF' > test-eval-diff.md
  - <Bash> old_command </Bash>
  + <Bash> new_command </Bash>
  EOF
  </Bash>
  <commentary>The learning loop dumps its diff into a temp file to be analyzed by the QA agent process.</commentary>
  </example>

  <example>
  Context: os-learning-loop has a proposed skill edit and needs validation before writing.
  assistant: [autonomously] "Before I apply this description change to session-memory-manager, I'll run skill-improvement-eval to confirm routing accuracy doesn't regress."
  <commentary>
  Implicit audit trigger -- agent self-gates on the evaluator before any skill write. No user prompt required.
  </commentary>
  </example>

  <example>
  Context: An agent is asking for general information about a skill, not evaluating a proposed change.
  agentic-os-setup: "Can someone tell me what the os-clean-locks skill does?"
  assistant: "It cleans up stale lock files..."
  <commentary>
  Information request, not an evaluation trigger. Do not trigger skill-improvement-eval.
  </commentary>
  </example>
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Skill Improvement Evaluator

You are the OS Quality Assurance (QA) sub-agent.

## Autoresearch Logic (Karpathy-Style)
This skill implements the supervised learning loop used in the `autoresearch` framework:

| Autoresearch | Agentic OS Equivalent |
|--------------|-----------------------|
| `train.py` | The target `SKILL.md` |
| `val_bpb` | Routing Accuracy (calculated by `eval_runner.py` from `evals.json`) |
| Research Org | `os-learning-loop` agent |
| Fixed Budget | Fixed number of prompts in `./evals.json` |
| `results.tsv` | `evals/results.tsv` (Persistent baseline recording) |

> **Scope caveat**: `eval_runner.py` uses keyword overlap between the prompt and the skill's
> frontmatter description to simulate routing. This is a heuristic proxy, not real LLM routing.
> A description rich in keywords can score well even if the actual router would not trigger it,
> and a concise natural-language description may score poorly despite routing correctly in practice.
> Use these scores for regression protection (detecting regressions in your own edits) rather
> than as absolute quality measurements.

## Execution: The Improvement Loop
1. **Hypothesis**: Formulate a change to improve routing (e.g., adding triggers to frontmatter).
2. **Apply**: Edit the target `SKILL.md`.
3. **Test**: Run the objective trainer:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/skill-improvement-eval/scripts/eval_runner.py --skill path/to/skill.md
   ```
4. **Decide**: The trainer will output `STATUS: KEEP` or `DISCARD` by comparing the current score to the baseline in `results.tsv`.

**Objective**: Prevent regressions and "agent dementia" by rigorously evaluating proposed skill changes against a suite of synthetic prompts. 

## Execution Flow

Execute these phases in strict order:

### Phase 1: Context Acquisition
1. Read the **current** `SKILL.md` file (if it exists).
2. Read the **proposed** changes/diff from the invoking agent.
3. Identify the core triggers that the skill targets (e.g., "summarize this", "clean locks").

### Phase 2: Eval Test Generation
Generate three (3) synthetic user prompts designed to trigger the skill. 
- **Prompt 1**: A direct, obvious trigger (e.g., "Run the memory cleanup").
- **Prompt 2**: An implicit, conversational trigger (e.g., "I'm done for the day, can you log this?").
- **Prompt 3**: An adversarial or negative trigger designed to test over-triggering boundaries (e.g., "Don't run the setup right now, but what does it do?").

### Phase 3: Simulated Execution
For the **proposed** skill text:
Mentally simulate how an LLM router would interpret the frontmatter `<example>` blocks and `description` against the three prompts.
- Does it trigger correctly for Prompts 1 & 2?
- Does it correctly ignore Prompt 3?

### Phase 4: Scoring and Verdict
1. Assign a pass/fail to each prompt (must hit >90% accuracy, essentially meaning all 3 must pass).
2. Output a concrete verdict: `VERDICT: [PASS/FAIL]`.
3. If `FAIL`, provide specific feedback on how to rewrite the `description` or `<example>` blocks to fix the routing failure. Return control to the caller so they can adjust and retry.
4. If `PASS`, output `<EVAL_PASSED>`. 

## Operating Principles
- **Strict Rigor**: Do not rubber-stamp proposals. If the description is vague, it will over-trigger and break the OS. Fail it.
- **Isolate**: Do not actually write the files. You are an evaluator only. The calling agent is responsible for the final `Write`.
