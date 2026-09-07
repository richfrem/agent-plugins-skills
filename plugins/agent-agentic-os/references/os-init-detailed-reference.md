# os-init — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Phase 3 — Retrofit call-list history and invariant

> [!IMPORTANT]
> **Retrofit mode must call every scaffolding substrate explicitly — it does not inherit them
> from fresh setup.** `create_project_structure()` (the non-`--retrofit` path) calls
> `_scaffold_root_files()`, `_scaffold_context_dir()` (→ `_init_control_plane_db()`),
> `_scaffold_claude_dir()` (→ `.claude/hooks/hooks.json`, the Stop turn hook config), and
> `_validate_and_finalize()` (→ `.git/hooks/pre-commit-evolution-guard`) as one sequence. The
> `--retrofit` branch in `_execute_action()` is a **separate, independently-maintained list** —
> historically it only called `_scaffold_3layer_memory()` + instructions/rules/skills sync, so
> retrofit runs silently skipped `control_plane.db`, `.claude/hooks/hooks.json`, and the git
> pre-commit hook, all three, while this doc and the script's own completion banner claimed both
> modes initialize them. Fixed in two passes: `_init_control_plane_db()` first (found via a
> downstream consumer repo where `context/control_plane.db` was missing post-retrofit), then
> `_scaffold_claude_dir()` + `_validate_and_finalize()` (found immediately after, by auditing the
> rest of `create_project_structure()`'s call list against what `--retrofit` actually reaches).
> All three are idempotent (skip-if-exists / merge-not-clobber), so calling them unconditionally
> on every retrofit run is safe. **When modifying `_execute_action()` again, diff its two
> branches' call lists against each other explicitly** — do not assume retrofit is a subset of
> fresh-setup; every fresh-setup scaffolding call needs a deliberate yes/no decision for whether
> retrofit should also make it, not silent omission.

## Phase 5 — Mandatory Post-Init Health Check (commands)

```bash
test -f context/control_plane.db && echo "OK control_plane.db" || echo "MISSING control_plane.db"
test -f .claude/hooks/hooks.json && echo "OK hooks.json (Stop turn hook)" || echo "MISSING hooks.json"
test -f .git/hooks/pre-commit-evolution-guard && echo "OK pre-commit-evolution-guard" || echo "MISSING pre-commit-evolution-guard"
test -f .github/workflows/verify-evolution-integrity.yml && echo "OK verify-evolution-integrity.yml" || echo "MISSING verify-evolution-integrity.yml"
```
If any report `MISSING`, re-run with `--retrofit`.

## Consumer Guidance & Upstream Contribution Protocol

When consuming plugins and skills from `agent-plugins-skills` (e.g. via `plugin-add` or direct clone):

1. **Maintainer vs. Consumer Separation**:
   - Consumers should **not** treat installed `.agents/skills/` or `plugins/` as unmaintainable black boxes.
   - If a bug, syntax error, or missing capability is detected in an installed skill or script, you have three primary workflows:

2. **Workflow A: Local Fix with Upstream Contribution (Recommended)**:
   - Identify the gap in the installed skill/script.
   - Test and verify the fix locally in your target repository.
   - Clone or checkout a feature branch in `richfrem/agent-plugins-skills`.
   - Port the fix, run `pytest plugins/agent-agentic-os/tests/`, and submit a Pull Request upstream.
   - Once merged, consuming projects can pull clean updates via `plugin-add -y` or `init_agentic_os.py --retrofit`.

3. **Workflow B: Project-Specific Overrides (Domain Divergence)**:
   - If your project requires rules or behavior specific to your domain (e.g., custom brokerage rules, private API endpoints), do **not** edit shared OS skills directly.
   - Place project-specific customizations in `.agent/rules/local-*` or define project-owned plugins under `plugins/<your-plugin>/`.
   - Shared OS rules in `CLAUDE.md`/`GEMINI.md` layer the fundamental control plane first; local rules layer on top without contradiction.

4. **Workflow C: Issue Reporting for Upstream Gaps**:
   - If unable to submit a PR directly, capture the exact reproduction trace, failure mode, and OS substrate versions, and log an issue in `https://github.com/richfrem/agent-plugins-skills/issues`.
   - Maintain the temporary local patch in `.agents/skills/` until the upstream fix is released and retrofitted.
