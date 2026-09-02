---
name: create-skill
plugin: agent-scaffolders
description: >
  Creates a new stateless skill in an existing plugin. Use this for procedural skills with no persistent state. NOT for sub-agents (use `create-sub-agent`) and NOT for skills that need stateful counters or session memory (use `create-stateful-skill`).
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
assistant: [triggers os-improvement-loop, not create-skill]
</example>

# create-skill: Skill Scaffolding Executor

Scaffolds a complete, standards-compliant agent skill directory. Handles filesystem
operations, template rendering, name validation, and discovery — then hands off to
the TDD quality gate.

**Scope**: This skill owns *structure*. It does not own *content quality* or *routing accuracy*.
Those are governed by `os-improvement-loop` (see cross-plugin handoff below).

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

- **Python only** — helper scripts go in plugin root `scripts/*.py`. Never generate `.sh` bash scripts.
- **Symlink, don't copy (ADR-002/003)** — if the skill needs a Python helper that lives at the plugin root's
  `scripts/` directory, create a **file-level symlink** using `symlink_manager.py`:
  ```bash
  python3 .agents/skills/symlink-manager/scripts/symlink_manager.py create \
    --src plugins/<plugin>/scripts/<canonical_name>.py \
    --dst plugins/<plugin>/skills/<skill>/scripts/<name>.py
  ```
  Never use raw `ln -s` directly.
- **Starter SKILL.md (Layer 1 Core)** — target **<= 100 lines**. Frontmatter with `name` (matches directory),
  `description` (third-person active verb, **MUST NOT exceed 1024 characters**), `allowed-tools`.
  Keep the body focused strictly on procedural steps; offload operational background, schemas, and tables to `references/<topic>.md` (Progressive Disclosure).
- **Starter evals.json** — root JSON array of at least 2 placeholder eval cases using the `should_trigger` schema:
  ```json
  [
    { "id": "eval-1-positive", "type": "positive", "prompt": "REPLACE", "should_trigger": true },
    { "id": "eval-2-negative", "type": "negative", "prompt": "REPLACE", "should_trigger": false }
  ]
  ```
  > ⚠️ **Schema requirement**: Always use root JSON array with `should_trigger: true/false`. The legacy
  > `expected_behavior` string field and dictionary wrappers are deprecated.
- **acceptance-criteria.md & fallback-tree.md** — wire standard contract symlinks from plugin `references/` via `symlink_manager.py`.

---

## Phase 4: Quality Gate & Alignment Verification

Run `audit_skill.py` to verify the scaffolded skill satisfies all 6 evolution invariants:

```bash
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name>
```

Ensure the output displays `[✅ PASS]` with 0 errors before proceeding to `os-improvement-loop` for routing calibration.

---

## Dependencies
- **symlink-manager** (dev-utils plugin)
- **audit-skill** (agent-scaffolders plugin)
- **os-improvement-loop** (agent-agentic-os plugin)

> [!TIP]
> See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md) for instructions on how to install missing dependencies.

**If `os-improvement-loop` is available**, hand off immediately after scaffolding:

```
Invoke os-improvement-loop on the newly scaffolded skill at <path>.
The RED scenario is: [trigger phrase from Phase 1 discovery].
Run the RED-GREEN-REFACTOR cycle to verify routing accuracy before shipping.
```

**If not available**, advise the user:
```
Scaffold complete. To verify routing accuracy and trigger description quality, ensure **os-improvement-loop** is installed. See [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md).
```

---

## Phase 5: Report

```
✅ Scaffolded: plugins/<plugin>/skills/<skill-name>/
   Files created: SKILL.md, evals/evals.json, references/acceptance-criteria.md
   Quality gate: [PASSED via os-improvement-loop | SKIPPED — os-eval-runner not installed]
   Next: fill in REPLACE placeholders in evals/evals.json, then run os-eval-runner baseline
```

---

## Edge Cases

- **Empty `$ARGUMENTS`**: begin with Phase 1 discovery — do not skip to scaffolding
- **Existing directory**: dual-confirmation before any overwrite (see Phase 2)
- **Improving an existing skill**: redirect to `os-improvement-loop` capability — that skill owns content
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
- **`os-improvement-loop`**: TDD methodology, RED scenario protocol, eval gate.
- **`os-eval-runner`**: autoresearch eval loop for skill optimization.
