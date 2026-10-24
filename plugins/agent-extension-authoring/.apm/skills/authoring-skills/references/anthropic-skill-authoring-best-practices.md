# Anthropic Skill Authoring Best Practices

Source: [Skill authoring best practices — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

This is a paraphrased reference based on the guidance supplied for this review,
not a verbatim copy. Consult the source for current platform requirements.

## Contents

- [Discovery and metadata](#discovery-and-metadata)
- [Structure and navigation](#structure-and-navigation)
- [Instructions and workflows](#instructions-and-workflows)
- [Evaluation and iteration](#evaluation-and-iteration)
- [Executable resources](#executable-resources)
- [Application to this repository](#application-to-this-repository)

## Discovery and metadata

- Startup discovery uses skill names and descriptions; instructions and bundled
  resources are read when relevant.
- Descriptions should explain the capability and when it applies, using specific
  terms and third-person wording.
- Required metadata includes a nonempty description of at most 1,024 characters
  and a name of at most 64 characters using lowercase letters, numbers, and hyphens.
- Anthropic prohibits XML tags and reserved words `anthropic` and `claude` in
  names, and XML tags in descriptions. These are Anthropic compatibility rules.
- Prefer meaningful, consistent names. Gerunds are suggested, not mandatory.

## Structure and navigation

- Keep the `SKILL.md` body below 500 lines as a performance recommendation.
  Move substantial details into resources loaded only when needed.
- Link required reference files directly from `SKILL.md`; avoid chains of
  references that hide essential instructions in indirectly linked files.
- Put a table of contents at the top of reference files longer than 100 lines,
  so a partial preview reveals their scope and supports targeted reading.
- The guide describes possible `head -100` previews, especially for nested
  references. It does **not** establish a universal 100-line loading limit.
- Organize resources by task or domain. Explain when each resource should be read.
- Use descriptive filenames and forward slashes in paths.

## Instructions and workflows

- Include knowledge the model needs for the task; omit explanations it already knows.
- Match specificity to risk: heuristics for flexible work, parameterized patterns
  for preferred approaches, exact commands for fragile operations.
- Provide a default approach and relevant exceptions rather than many equal choices.
- Use clear ordered steps, validation checkpoints, and feedback loops for complex work.
- For consequential batch changes, produce and validate an intermediate plan before
  execution, then verify the result.
- Use concrete examples and output templates when they clarify expected behavior.
- Keep terminology consistent and avoid instructions that expire on calendar dates.

## Evaluation and iteration

- Identify observed gaps and establish a baseline without the skill.
- Create at least three representative task evaluations before extensive authoring.
  Describe observable successful behavior, inputs, and expected outputs.
- Write minimal instructions addressing those gaps, then compare evaluated results.
- Test with the models intended to use the skill and with real requests.
- Observe discovery, reference navigation, missed instructions, and unused resources.
- Refine based on evidence from fresh consumer sessions and team feedback.
- Task-success evaluations complement routing tests; neither replaces the other.
  The guide supplies an `expected_behavior` example, not a mandatory runner schema.

## Executable resources

- Prefer reusable scripts for deterministic operations. State whether to execute
  a script or read it as reference.
- Handle expected failures explicitly with actionable diagnostics. Document
  dependencies and justify configuration values.
- Check runtime capabilities instead of assuming packages, network access, or
  installation are available across every host.
- Use fully qualified MCP tool names in the format supported by the target host.
- Validate intermediate artifacts and final outputs; use visual inspection where
  layout affects correctness.

## Application to this repository

- The repository's 80–100-line router target is a local convention, stricter than
  Anthropic's recommendation. Do not describe it as an external loading limit.
- Keep entry points concise while making required constraints and resource routing
  visible early. Add contents lists where length or branching warrants navigation.
- Hub-and-spoke scripts, symlink registration, and local evaluation schemas remain
  repository conventions; this source does not require those packaging choices.
- Review `create-skill`, `audit-skill`, their references, and the auditor together
  before changing shared authoring or validation requirements.
