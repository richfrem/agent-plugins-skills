# Discovery Interview & Scaffolding Protocol

## Phase 1: Discovery Interview

When creating a new skill, capture and validate the following inputs before writing any files:

1. **Skill Slug**:
   - Format: Lowercase kebab-case (e.g. `link-validator`).
   - Validation: 1–64 characters, letters, numbers, and single hyphens. No special characters or shell metacharacters (`;`, `&`, `|`, `$`, ``` ` ```).
   - Invariant: Name in `SKILL.md` frontmatter MUST match directory name exactly.

2. **Core Purpose**:
   - Single active sentence describing capability and trigger context.
   - Example: "Extracts text and tabular content from PDF documents for downstream analysis."

3. **Target Plugin**:
   - Monorepo directory (`plugins/<plugin-name>`) that will own this skill.
   - Invariant: All skills must belong to an existing plugin.

4. **Trigger Routing Invariants**:
   - 3–5 realistic prompts where this skill MUST trigger (`should_trigger: true`).
   - 3–5 realistic negative prompts where another skill should handle it (`should_trigger: false`).

5. **Tool Permissions**:
   - List required tools in frontmatter (`allowed-tools: Bash, Read, Write`).

## Phase 2: Plan and Confirm

Present the proposed layout:
```
plugins/<plugin>/skills/<skill-slug>/
  SKILL.md                       (lean router <= 80 lines)
  evals/
    evals.json                   (root JSON array with should_trigger)
  references/
    acceptance-criteria.md       (symlink)
    fallback-tree.md             (symlink)
```
Reuse the user's recorded authorization and requirements; ask only for genuine gaps.
If a directory already exists, generation fails without overwriting it. Propose a
bounded update instead. Choose instructional or executable output explicitly;
executable generation returns proposed plugin-root script links. Delegate link
registration/restoration to symlink-manager before final audit.

Keep the first action and critical constraints early. Long references need early
contents and direct entry-point links. Create at least three task-success scenarios
in addition to routing cases; expected_behavior belongs to the task-success contract.
