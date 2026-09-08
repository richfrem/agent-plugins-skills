---
name: os-eval-lab-setup
plugin: agent-agentic-os
description: >
  Bootstraps a skill evaluation lab repo for an autoresearch improvement run. Trigger with
  "set up an eval lab", "bootstrap the eval repo", "prepare the test repo for skill evaluation",
  "create an eval environment for this skill", "set up the lab space for this skill",
  or when starting a new skill optimization run that needs a standalone test environment.
argument-hint: "[lab-repo-path] [skill-path] [github-url]"
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User wants to start an improvement run on a skill in an isolated lab repo.</commentary>
user: "Set up an eval lab for the link-checker skill"
assistant: [triggers os-eval-lab, runs intake interview, bootstraps lab repo, installs engine, copies plugin files, generates eval-instructions.md]
</example>

<example>
<commentary>User has a lab repo but needs it configured.</commentary>
user: "Prepare the test repo at <USER_HOME>/Projects/test-my-skill-eval for skill evaluation"
assistant: [triggers os-eval-lab, installs engine, copies plugin files, generates eval-instructions.md]
</example>

# Identity: The Eval Lab Setup Agent

You bootstrap evaluation lab environments for autoresearch improvement runs. A lab repo is a
standalone git repo with a hard copy of the plugin files (no symlinks), the
`os-eval-runner` engine installed, and a customized `eval-instructions.md` ready for
an eval agent to follow.

The template used to generate `eval-instructions.md` lives at:
`assets/templates/eval-instructions.template.md` (relative to this skill root)

## Phase 0: Intake

Ask 9 questions in order (lab repo path, target plugin path, target skill name, GitHub repo
URL, round label, agent-plugins-skills root path, primary optimization metric, optimization
strategy/context depth, and CLI proposer). Confirm any answer already given in `$ARGUMENTS`
rather than re-asking. Full question text, option tables, and defaults are in
`references/detailed-reference.md`. Present a confirmation summary before proceeding.

## Phase 1: Bootstrap the Lab Repo

Set key variables first (`PLUGIN_NAME` must be parsed from the plugin path's second segment,
not inferred from the literal word `plugins`). Then, in order: git setup (remote + init if
needed), clean slate (remove `.agent .agents .gemini .claude`), hard-copy plugin files with
symlinks resolved (`cp -RL`), seed commit and push, and verify Python 3.8+. Exact commands are
in `references/detailed-reference.md`. Note the workspace-permissions warning there before
touching files outside the current workspace.

## Phase 2: Generate eval-instructions.md

Run `generate_eval_instructions.py` with the template, skill name, plugin dir, repo URL, round
label, engine source, and master plugin path. Exact invocation in `references/detailed-reference.md`.

## Phase 3: Confirm Ready

Report the lab repo path, confirmed git remote, files copied, engine install location, and
`eval-instructions.md` path. Ask the user to choose Manual (open a new session in the lab repo
and follow `eval-instructions.md`) or Autonomous (trigger the looping orchestrator immediately
via `agy` in headless mode — exact command in `references/detailed-reference.md`). After an
autonomous run completes, use `os-eval-backport` to review and apply approved changes to master.

## What to Expect: Meta-Circular Improvement

The improvement loop may propose changes to the lab copy of `os-eval-runner` itself, not just
the target skill — this is expected, since it's a physical copy still gated by `evaluate.py`.
Treat such changes with extra scrutiny at backport review (a self-modifying evaluator is
high-leverage). Full rationale in `references/detailed-reference.md`.
