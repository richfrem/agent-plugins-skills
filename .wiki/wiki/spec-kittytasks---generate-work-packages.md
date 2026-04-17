---
concept: spec-kittytasks---generate-work-packages
source: plugin-code
source_file: spec-kitty-plugin/workflows/spec-kitty.tasks.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.416981+00:00
cluster: subtasks
content_hash: bbe4689c06014620
---

# /spec-kitty.tasks - Generate Work Packages

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- spec-kitty-command-version: 3.0.3 -->
# /spec-kitty.tasks - Generate Work Packages

**Version**: 0.11.0+

## ⚠️ CRITICAL: THIS IS THE MOST IMPORTANT PLANNING WORK

**You are creating the blueprint for implementation**. The quality of work packages determines:
- How easily agents can implement the feature
- How parallelizable the work is
- How reviewable the code will be
- Whether the feature succeeds or fails

**QUALITY OVER SPEED**: This is NOT the time to save tokens or rush. Take your time to:
- Understand the full scope deeply
- Break work into clear, manageable pieces
- Write detailed, actionable guidance
- Think through risks and edge cases

**Token usage is EXPECTED and GOOD here**. A thorough task breakdown saves 10x the effort during implementation. Do not cut corners.

---

## 📍 WORKING DIRECTORY: Stay in the project root checkout

**IMPORTANT**: Tasks works in the project root checkout. NO worktrees created.

```bash
# Run from project root (same directory as /spec-kitty.plan):
# You should already be here if you just ran /spec-kitty.plan

# Creates:
# - kitty-specs/###-feature/tasks/WP01-*.md → In project root checkout
# - kitty-specs/###-feature/tasks/WP02-*.md → In project root checkout
# - Commits ALL to target branch
# - NO worktrees created
```

**Do NOT cd anywhere**. Stay in the project root checkout root.

**Worktrees created later**: After tasks are generated, use `spec-kitty implement WP##` to create workspace for each WP.

**In repos with multiple features, always pass `--feature <slug>` to every spec-kitty command.**

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Context Resolution (0.11.0+)

Before proceeding, resolve canonical command context:

```bash
spec-kitty agent context resolve --action tasks --json
```

Treat the resolver JSON as canonical for:
- `feature_slug`
- `feature_dir`
- `current_branch`
- `target_branch`
- `planning_base_branch`
- `merge_target_branch`
- `branch_matches_target`
- exact follow-up commands (`check_prerequisites`, `finalize_tasks`)

Prompts do not rediscover feature context. Commands do.

## Outline

1. **Setup**: Run the exact `check_prerequisites` command returned by the resolver and capture:
   - `feature_dir`
   - `artifact_files` / `artifact_dirs` (if present)
   - `available_docs`
   - `current_branch`
   - `target_branch` / `base_branch`
   - `planning_base_branch` / `merge_target_branch`
   - `branch_matches_target`
   All paths must be absolute.

   If `branch_matches_target` is false, stop and tell the user the checkout is on the wrong planning branch instead of probing git manually in the prompt.

   **CRITICAL**: The command returns JSON with `feature_dir` as an ABSOLUTE path. It also returns `runtime_vars.now_utc_iso` (`NOW_UTC_ISO`) for deterministic timestamp fields.

   **YOU MUST USE THIS PATH** for ALL subsequent file operations. Example:
   ```
   feature_dir = "/path/to/project/kitty-specs/001-a-simple-hello"
   tasks.md location: feature_dir + "/tasks.md"
   prompt location: feature_dir + "/tasks/WP01-slug.md"
   ```

   **DO NOT CREATE** paths like:
   - ❌ `tasks/WP01-slug.md` (missing feature_dir prefix)
   - ❌ `/tasks/WP01-slug.md` (wrong root)
   - ❌ `feature_dir/tasks/planned/WP01-slug.md` (WRONG - no subdirectories!)
   - ❌ `WP01-slug.md` (wrong directory)

3. **Load design documents** from `feature_dir` (only those present):
   - **Required**: plan.md (tech architecture, stack), spec.md (user stories & priorities)
   - **Optional**: data-model.md (entities), contracts/ (API schemas), research.md (decisions), quickstart.md (validation scenarios)
   - Scale your effort to the feature: simple UI tweaks deserve lighter coverage, multi-system releases require deeper decomposition.

4. **Derive fine-grained subtasks** (IDs `T001`, `T002`, ...):
   - Parse plan/spec to enumerate concrete implementation steps, tests (only if explicitly requested), migrations, and operational work

*(content truncated)*

## See Also

- [[spec-kittytasks-packages---generate-work-package-files]]
- [[spec-kittytasks-packages---generate-work-package-files]]
- [[spec-kittytasks-packages---generate-work-package-files]]
- [[spec-kittytasks-packages---generate-work-package-files]]
- [[spec-kittytasks-packages---generate-work-package-files]]
- [[spec-kittytasks-outline---create-task-breakdown-document]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/workflows/spec-kitty.tasks.md`
- **Indexed:** 2026-04-17T06:42:10.416981+00:00
