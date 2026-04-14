---
name: create-skill
description: >
  Scaffolds the filesystem structure for a new agent skill: creates the directory layout,
  writes a starter SKILL.md, generates evals/evals.json, references/, scripts/, and assets/
  as needed, and runs a discovery interview to capture name, purpose, and trigger phrases
  before writing any files. Use when the user says "create a new skill", "scaffold a skill",
  "generate a skill", "new skill setup", or "make a skill directory". Does not handle
  content improvement for existing skills — that is handled by os-skill-improvement.
argument-hint: "[skill-name or use-case description]"
allowed-tools: Bash, Read, Write
---

<example>
<commentary>User wants to create a brand-new skill from scratch.</commentary>
user: "Create a new skill called link-validator"
assistant: [triggers create-skill, runs discovery interview, scaffolds directory structure with SKILL.md, evals/evals.json, references/acceptance-criteria.md]
</example>

<example>
<commentary>Negative — user wants to improve an existing skill, not scaffold a new one.</commentary>
user: "Improve the trigger description for my link-checker skill"
assistant: [triggers os-skill-improvement, not create-skill]
</example>

# create-skill: Skill Scaffolding Executor

Scaffolds a complete, standards-compliant agent skill directory. Handles filesystem
operations, template rendering, name validation, and discovery — then hands off to
the TDD quality gate.

**Scope**: This skill owns *structure*. It does not own *content quality* or *routing accuracy*.
Those are governed by `os-skill-improvement` (see cross-plugin handoff below).

---

## Inputs

- `$ARGUMENTS` — optional skill name or brief use-case description passed as initial
  context to the discovery phase. Omit to start with open discovery.

---

## Phase 1: Discovery Interview

Before writing any files, capture all required inputs:

1. **Skill name** — lowercase-hyphen slug (e.g. `link-validator`). Validate: no spaces,
   no special characters, no shell injection sequences (reject names containing `;`, `&`, `|`, `$`, `` ` ``).
2. **Purpose** — one sentence: what does this skill do and when does it fire?
3. **Target plugin** — which plugin directory will own this skill?
4. **Trigger phrases** — 3-5 specific phrases a user would say to invoke it.
5. **Tools needed** — which `allowed-tools` does it require?

If `$ARGUMENTS` is provided, treat it as a starting point and confirm rather than re-ask.

---

## Phase 2: Plan and Confirm

Present the proposed directory layout before writing anything:

```
plugins/<plugin>/skills/<skill-name>/
  SKILL.md
  evals/
    evals.json
  references/
    acceptance-criteria.md
  ./scripts/         (if the skill needs Python helpers)
  ./assets/          (if the skill needs static resources)
```

**Confirm with the user before proceeding.** If a directory with that name already exists:
> "Warning: `<path>` already exists. Overwrite? (yes/no)"
> Do NOT overwrite without explicit confirmation.

---

## Phase 3: Scaffold

Create the confirmed directory structure. Standards enforced by `acceptance-criteria.md`:

- **Python only** — helper scripts go in `scripts/*.py`. Never generate `.sh` bash scripts.
- **Symlink, don't copy** — if the skill needs a Python helper that lives at the plugin root's
  `scripts/` directory, create a **file-level symlink** in `skills/<skill>/scripts/` pointing to
  `../../../scripts/<canonical_name>.py`. Never duplicate the file. The symlink filename may differ
  from the target (e.g. `execute.py` → `exploration_optimizer_execute.py`). Create with:
  ```bash
  ln -s ../../../scripts/<canonical_name>.py skills/<skill>/scripts/<name>.py
  ```
  Verify the symlink resolved: `python3 -c "import os; print(os.path.exists('skills/<skill>/scripts/<name>.py'))"`
  must print `True`. On Windows/`core.symlinks=false` machines, git will check these out as
  plain-text "stand-in" files — run `bulk_symlink_fixer.py` to restore them after checkout.
- **Starter SKILL.md** — frontmatter with `name`, `description` (use the purpose from Phase 1; **MUST NOT exceed 1024 characters**),
  `allowed-tools`. Body: stub sections for Identity, Steps, and Common Failures.
- **Starter evals.json** — at least 2 placeholder eval cases using the `should_trigger` schema:
  ```json
  { "id": "eval-1-positive", "type": "positive", "prompt": "REPLACE", "should_trigger": true }
  { "id": "eval-2-negative", "type": "negative", "prompt": "REPLACE", "should_trigger": false }
  ```
  > ⚠️ **Schema requirement**: Always use `should_trigger: true/false`. The legacy
  > `expected_behavior` string field is ignored by the eval scorer and will produce 0% accuracy.
- **acceptance-criteria.md** — write to `references/acceptance-criteria.md` with the
  acceptance criteria captured in Phase 1.

---

## Phase 4: Quality Gate Handoff

## Dependencies
- **os-skill-improvement** (agent-agentic-os plugin)

> [!TIP]
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions on how to install missing dependencies.

**If `os-skill-improvement` is available**, hand off immediately after scaffolding:

```
Invoke os-skill-improvement on the newly scaffolded skill at <path>.
The RED scenario is: [trigger phrase from Phase 1 discovery].
Run the RED-GREEN-REFACTOR cycle to verify routing accuracy before shipping.
```

**If not available**, advise the user:
```
Scaffold complete. To verify routing accuracy and trigger description quality, ensure **os-skill-improvement** is installed. See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md).
```

---

## Phase 5: Report

```
✅ Scaffolded: plugins/<plugin>/skills/<skill-name>/
   Files created: SKILL.md, evals/evals.json, references/acceptance-criteria.md
   Quality gate: [PASSED via ~~skill-improvement | SKIPPED — ~~eval-gate not installed]
   Next: fill in REPLACE placeholders in evals/evals.json, then run ~~eval-gate baseline
```

---

## Edge Cases

- **Empty `$ARGUMENTS`**: begin with Phase 1 discovery — do not skip to scaffolding
- **Existing directory**: dual-confirmation before any overwrite (see Phase 2)
- **Improving an existing skill**: redirect to `~~skill-improvement` capability — that skill owns content
  quality and routing improvement. `create-skill` is for net-new scaffolding only.
- **Scaffold script crash**: read the Python stack trace, correct obvious errors, or surface
  the full trace to the user — do not silently skip
- **Template rendering failure**: do not output partially-rendered content; provide the
  base template inline and instruct the user to fill values manually

---

## References

- [`acceptance-criteria.md`](references/acceptance-criteria.md) — structural pass/fail criteria
- [`fallback-tree.md`](fallback-tree.md) — error handling procedures
- **Architectural Decision Records (ADRs)** located at `references/ADRs/`. Always consult them for standards on plugin architecture, shared scripts, cross-plugin dependencies, symlinking, and loose coupling to avoid repeating yourself.
- **`~~skill-improvement`** *(~~eval-gate capability — see CONNECTORS.md)*: TDD methodology, RED scenario protocol, eval gate.
- **`~~eval-gate`** *(~~eval-gate capability — see CONNECTORS.md)*: autoresearch eval loop for skill optimization.
