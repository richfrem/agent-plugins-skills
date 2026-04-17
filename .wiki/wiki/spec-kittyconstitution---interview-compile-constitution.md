---
concept: spec-kittyconstitution---interview-compile-constitution
source: plugin-code
source_file: spec-kitty-plugin/workflows/spec-kitty.constitution.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.409982+00:00
cluster: user
content_hash: 7a39de4f483334eb
---

# /spec-kitty.constitution - Interview + Compile Constitution

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- spec-kitty-command-version: 3.0.3 -->
# /spec-kitty.constitution - Interview + Compile Constitution

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

**In repos with multiple features, always pass `--feature <slug>` to every spec-kitty command.**

## Command Contract

This command delegates constitution work to the CLI constitution workflow. Do not hand-author long governance content in chat unless the user explicitly asks for manual drafting.

### Output location

- Constitution markdown: `.kittify/constitution/constitution.md`
- Interview answers: `.kittify/constitution/interview/answers.yaml`
- Reference manifest: `.kittify/constitution/references.yaml`
- Local reference docs: `.kittify/constitution/library/*.md`

## Execution Paths

### Path A: Deterministic minimal setup (fast)

Use when user wants speed, defaults, or bootstrap:

```bash
spec-kitty constitution interview --defaults --profile minimal --json
spec-kitty constitution generate --from-interview --json
```

### Path B: Interactive interview (full)

Use when the user wants project-specific policy capture:

```bash
spec-kitty constitution interview --profile comprehensive
spec-kitty constitution generate --from-interview
```

## Editing Rules

- To revise policy inputs, rerun `constitution interview` (or edit `answers.yaml`) and regenerate.
- Use `--force` with generate if the constitution already exists and must be replaced.
- Keep constitution concise; full detail belongs in reference docs listed in `references.yaml`.

## Validation + Status

After generation, verify status:

```bash
spec-kitty constitution status --json
```

## Context Bootstrap Requirement

After constitution generation, first-run lifecycle actions should load context explicitly:

```bash
spec-kitty constitution context --action specify --json
spec-kitty constitution context --action plan --json
spec-kitty constitution context --action implement --json
spec-kitty constitution context --action review --json
```

Use JSON `text` as governance context. If `mode=bootstrap`, follow referenced docs as needed.


## See Also

- [[spec-kittyspecify---create-research-specification]]
- [[spec-kittyplan---create-implementation-plan]]
- [[spec-kittyplan---create-implementation-plan]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittyspecify---create-feature-specification]]
- [[spec-kittytasks---generate-work-packages]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/workflows/spec-kitty.constitution.md`
- **Indexed:** 2026-04-17T06:42:10.409982+00:00
