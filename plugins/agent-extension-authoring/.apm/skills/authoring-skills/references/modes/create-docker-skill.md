> Retired skill `create-docker-skill`, kept as the **create-docker-skill** mode of `authoring-skills`. Body unchanged apart from link targets, retired-skill names (now the new skills) and the corrected commands. Frontmatter removed.
>
> Original description: Scaffolds an agent skill with a Docker runtime environment. NOT for normal local skills (use `create-skill`) and NOT for Azure hosted agents (use `create-azure-agent`).

# Create Docker Skill (create-docker-skill)

Scaffolds a compliant agent skill that executes workloads within containerized runtimes (Docker, Nextflow, HPC).

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Container Scope**: Only for container-dependent workloads. For standard local skills, use `create-skill`. For Azure AI Foundry, use `create-azure-agent`.
- **Pre-Flight Validation**: Generated skills must verify container daemon availability (`docker info`) and fail gracefully with actionable remediation.
- **Security Boundaries**: Restrict mount scopes to designated working directories; never mount the root filesystem or run in privileged mode unless requested.
- **Non-Destructive**: Never overwrite existing directories without explicit confirmation.

## Quick start

```bash
python3 scripts/scaffold.py \
  --type skill \
  --name <skill-name> \
  --path plugins/<plugin>/.apm/skills \
  --desc "Containerized workload execution"
```

## Workflow

1. **Phase 1: Runtime Discovery**: Gather container runtime (Docker, Nextflow, Podman), base image, CPU/memory limits, volume mounts, and network isolation needs.
2. **Phase 2: Directory Scaffolding**: Execute `scaffold.py` to generate the skill structure with `SKILL.md`, `scripts/`, `evals/`, and `references/`.
3. **Phase 3: Runtime Harnessing**: Configure container pre-flight checks, subprocess invocation wrapper, stdout/stderr streaming, and container cleanup traps.
4. **Phase 4: Verification & Evals**: Populate `evals/evals.json` with positive/negative trigger cases and validate skill compliance.

## Verification

```bash
# Validate generated skill compliance
python3 scripts/audit_skill.py plugins/<plugin>/.apm/skills/<skill-name> --mode source

# Verify container runtime pre-flight logic
docker info >/dev/null 2>&1 || echo "Docker daemon unreachable"
```

## References
- [fallback-tree.md](../fallback-tree.md) - Procedural fallback handling for scaffolding failures.
- [acceptance-criteria.md](../acceptance-criteria.md) - Standard acceptance criteria for container skills.
- [references/patterns/client-side-compute-sandbox-constraint.md](../patterns/client-side-compute-sandbox-constraint.md) - Sandbox isolation pattern.
