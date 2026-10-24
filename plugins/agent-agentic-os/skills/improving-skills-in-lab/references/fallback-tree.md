# Fallback Tree: improving-skills-in-lab

Merged verbatim from the retired skills; one section per mode. Headings inside a section are one level deeper than in the original.

## Contents

- [Mode: planner](#mode-planner)
- [Mode: setup](#mode-setup)
- [Mode: loop](#mode-loop)
- [Mode: scorer](#mode-scorer)
- [Mode: log](#mode-log)
- [Mode: backport](#mode-backport)
- [Mode: memory](#mode-memory)

## Mode: planner

### From os-architect (merged into the `plan` mode)

1. Classify intent via interview + ecosystem audit -> 2. If classification is ambiguous, ask clarifying question with recommended default -> 3. If no CLI dispatch tool is available, hand off plan as a manual delegation prompt.

### From os-evolution-planner (merged into the `plan` mode)

1. Brainstorm options via cheapest available model, then write task plan + delegation prompt -> 2. If no CLI model is available, write the plan directly for manual execution.

## Mode: setup

1. Bootstrap dedicated lab repo via scripted scaffold -> 2. If scaffold script fails, fall back to manual directory + git init walkthrough.

## Mode: loop

1. Full concurrent event-driven multi-agent loop cycle -> 2. If event bus unavailable, fall back to single-agent sequential execute-eval-log cycle.

## Mode: scorer

### From os-eval-runner (renamed to the `score` mode)

1. Run headless Python eval scripts -> 2. If eval script missing or fails to import, report FAIL with the import error rather than a false PASS.

### From os-skill-improvement (merged into the `score` mode)

1. RED-GREEN-REFACTOR cycle gated by the `score` mode's evaluate.py -> 2. If the scorer is unavailable, fall back to manual before/after routing comparison.

## Mode: log

### From os-experiment-log (renamed to the `log` mode)

1. Write dated run file + update index.md -> 2. If source type unrecognized, log as "unclassified" with raw payload preserved for manual triage.

### From os-improvement-report (merged into the `log` mode)

1. Read the cycle data and render trend chart/text -> 2. If cycle data is missing or empty, report 'no cycles recorded yet'.

## Mode: backport

1. Review completed lab run diff and backport approved changes to master -> 2. If the lab agent's rationale is unclear, interrogate it before capturing learnings rather than backporting blind.

## Mode: memory

1. Read/write via kernel.py memory API -> 2. If kernel.py unavailable, fall back to direct file read/append on the target memory markdown file.
