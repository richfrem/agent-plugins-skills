---
concept: spec-kittymerge---deterministic-merge
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/software-dev/command-templates/merge.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.349232+00:00
cluster: branch
content_hash: d5170a00bb42cca5
---

# /spec-kitty.merge - Deterministic Merge

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Merge a completed feature into the target branch and clean up worktree
---

# /spec-kitty.merge - Deterministic Merge

Run merge from the **primary repository checkout root** (outside `.worktrees/`).
The checkout branch can be whatever branch the developer is using.

## Required Execution Sequence

1. Generate deterministic merge plan first:

```bash
spec-kitty merge --feature <feature-slug> --dry-run --json
```

2. Confirm effective merge tips from JSON (`effective_wp_branches`).

3. Execute the actual merge once:

```bash
spec-kitty merge --feature <feature-slug>
```

## Prohibited Behavior

- Never run manual `git merge <feature-WP##>` loops by default.
- Never merge WP01→WP02→... just by numbering.
- Only attempt manual git merges if `spec-kitty merge` fails and the user asks for manual recovery.

## Interpretation Rules

- Single effective tip: merge that tip only.
- Empty effective set: already integrated; no merge needed.
- `all_wp_branches` may be larger than `effective_wp_branches`; this is expected.


## See Also

- [[spec-kittyspecify---create-research-specification]]
- [[spec-kittyconstitution---interview-compile-constitution]]
- [[spec-kittyconstitution---interview-compile-constitution]]
- [[spec-kittymerge]]
- [[spec-kittyplan---create-implementation-plan]]
- [[spec-kittyplan---create-implementation-plan]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/software-dev/command-templates/merge.md`
- **Indexed:** 2026-04-17T06:42:10.349232+00:00
