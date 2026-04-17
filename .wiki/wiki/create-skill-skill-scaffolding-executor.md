---
concept: create-skill-skill-scaffolding-executor
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-skill.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.318919+00:00
cluster: plugin-code
content_hash: 47af5b1a5bb78a24
---

# create-skill: Skill Scaffolding Executor

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: create-skill
description: >
  Scaffolds the filesystem structure for a new agent skill: creates the directory layout,
  writes a starter SKILL.md, generates evals/evals.json, references/, scripts/, and assets/
  as needed, and runs a discovery interview to capture name, purpose, and trigger phrases
  before writing any files. Trigger with "create a new skill", "scaffold a skill",
  "generate a skill", "new skill setup", or "make a skill directory".

  <example>
  Context: User wants to create a brand-new skill from scratch.
  user: "Create a new skill called link-validator"
  assistant: [triggers create-skill, runs discovery interview, scaffolds directory structure]
  
  </example>

  <example>
  Context: User wants to improve an existing skill's content, not scaffold a new one.
  user: "Improve the trigger description for my link-checker skill"
  assistant: [triggers os-skill-improvement, not create-skill]
  
  </example>
argument-hint: "[skill-name or use-case description]"
allowed-tools: Bash, Read, Write
---

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
> See [INSTALL.md](h

*(content truncated)*

## See Also

- [[procedural-fallback-tree-create-docker-skill]]
- [[acceptance-criteria-create-skill]]
- [[procedural-fallback-tree-create-skill]]
- [[procedural-fallback-tree-create-stateful-skill]]
- [[procedural-fallback-tree-create-docker-skill]]
- [[procedural-fallback-tree-create-docker-skill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-skill.md`
- **Indexed:** 2026-04-17T06:42:10.318919+00:00
