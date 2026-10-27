# Create GitHub Action (create-github-action)

Scaffolds deterministic GitHub Actions CI/CD workflow configurations (`.github/workflows/<name>.yml`) without runtime AI orchestration.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Deterministic Scope**: Traditional CI/CD only (no runtime LLMs). For agentic or prompt-driven automation, use `create-agentic-workflow`. For local tool hooks, use `authoring-instructions`.
- **Least-Privilege Permissions**: Explicitly specify minimal `permissions:` blocks (e.g. `contents: read`) at workflow or job level; never omit or use broad write tokens.
- **Action Pinning & Timeouts**: Pin third-party actions to verified major versions or SHAs. Set explicit `timeout-minutes` on all jobs.
- **Secret Sanitization**: Reference secrets exclusively via `${{ secrets.NAME }}`; never hardcode sensitive values or log secret outputs.

## Quick start

```bash
# Seed discovery for a specific workflow type (test, build, deploy, lint, release)
python3 scripts/scaffold_github_action.py --category test --platform python --name "CI"   # writes .github/workflows/
```

## Workflow

1. **Phase 1: Pipeline Discovery**: Identify workflow trigger events (`push`, `pull_request`, `workflow_dispatch`), target runner environments (`ubuntu-latest`), matrix strategies, and dependencies.
2. **Phase 2: Scaffolding Generation**: Construct `.github/workflows/<name>.yml` with explicit triggers, concurrency controls, least-privilege permissions, and step caching.
3. **Phase 3: Secrets & Environment Setup**: Document required repository secrets and environment variables without logging actual secrets.
4. **Phase 4: Schema Validation**: Validate the generated YAML syntax and step structure against GitHub Actions schema standards.

## Verification

```bash
# Check YAML syntax and schema formatting
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/<name>.yml'))"

# Audit skill compliance
python3 ../authoring-skills/scripts/audit_skill.py . --mode source
```

## References
- [fallback-tree.md](../fallback-tree.md) - Procedural fallbacks for generation failures.
- [action-types.md](../action-types.md) - Supported GitHub Action pipeline archetypes.
- [acceptance-criteria.md](../acceptance-criteria.md) - Quality gates for CI/CD workflows.
