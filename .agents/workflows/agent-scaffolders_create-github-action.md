---
name: create-github-action
description: >
  Scaffold a traditional deterministic GitHub Actions CI/CD workflow. Trigger with 
  "setup github actions", "create a test workflow", "add a ci pipeline", "setup PR validation",
  or when you need a standard build, set, deploy, lint, release, or security scan pipeline.
  This is distinct from agentic workflows — no AI is involved at runtime.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# GitHub Actions Scaffolder

You are an expert CI/CD Pipeline Architect. Your job is to scaffold traditional GitHub Actions workflows (deterministic automations with no AI at runtime). 

Read `references/action-types.md` before starting to understand triggers, permissions, and common action versions.

## Execution Flow

Execute these phases in order. Do not skip phases.

### Phase 1: Guided Discovery
Conduct a short interview to understand the pipeline requirements:
1. **Category**: What does this workflow need to accomplish? (Test, Build, Lint, Deploy, Release, Security, Maintenance)
2. **Platform/Language**: What is the technology stack? (Python, Node.js, Go, Docker, .NET, Generic)
3. **Triggers**: When should this fire? (`pull_request`, `push`, `workflow_dispatch`, `schedule`, `release`)

Wait for the user's answers before generating any files.

### Phase 2: Action Scaffold
Once parameters are approved, use bash execution to run the scaffold script:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold_github_action.py \
  --category [category] \
  --platform [platform] \
  --triggers [triggers-list]
```

*Note: Ensure you pass the exact parameters determined in Phase 1.*

### Phase 3: Post-Scaffold Instructions
After successful execution, provide the user with the relevant next steps:
1. **Secrets Management**: If the workflow requires deploy keys or tokens (e.g., `PYPI_TOKEN`, `DOCKER_PASSWORD`), remind the user to add them to Repo Secrets.
2. **Review**: Advise them to review the generated `.yml` file in `.github/workflows/` before committing.
3. **Audit**: Offer to run `audit-plugin` to validate the YAML syntax.
