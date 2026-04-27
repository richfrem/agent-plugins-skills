---
name: create-docker-skill
plugin: agent-scaffolders
description: Scaffold an agent skill with Docker runtime support
argument-hint: "[skill-name]"
allowed-tools: Bash, Read, Write
---

Follow the `create-docker-skill` skill workflow to scaffold a compliant agent skill
that depends on containerized runtimes (Docker, Nextflow, HPC).

## Inputs

- `$ARGUMENTS` — optional skill name or use-case description. Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` provides a skill name, use it to seed the discovery phase
2. Follow the create-docker-skill phased workflow: determine container runtime and
   workflow type, gather environment check requirements, design pre-flight validation
   and subprocess execution scaffolding, then generate the skill directory
3. Report the created skill path and Docker environment setup instructions

## Output

Skill directory with `SKILL.md` containing pre-flight environment checks, subprocess
execution patterns, security-override config, and Docker-aware error handling.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with discovery — do not assume Docker is available
- If Docker is not installed in the target environment: generate graceful degradation
- If the workflow uses HPC or Nextflow instead of Docker: adapt scaffolding accordingly
