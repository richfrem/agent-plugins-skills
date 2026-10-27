# Acceptance Criteria: authoring-skills

## Mode: create-skill

**Purpose**: Verify the system generates Microsoft-compliant Skill architectures.

## 1. Directory Structure
- **[PASSED]**: Skill generates `scripts/`, `references/`, and `assets/` folders. It places an `acceptance-criteria.md` inside `references/`.
- **[FAILED]**: Skill fails to create subdirectories, leaving a massive root `./SKILL.md` vulnerable to bloating.

## 2. Shell Enforcement
- **[PASSED]**: Skill uses `.py` Python scripts inside the `scripts/` folder.
- **[FAILED]**: Skill generates legacy bash `.sh` execution scripts.

## Mode: create-stateful-skill

[PASSED] The generated stateful skill explicitly documents its `Draft` vs `Final` interaction modes.
[PASSED] The skill uses the Chained Command Invocation pattern to offer Next Actions.
[FAILED] The skill lacks an explicit state persistence mechanism (e.g. no intermediate artifact creation).
[FAILED] The discovery phase doesn't ask the user what the stopping condition is.

## Mode: audit-skill

> Written during consolidation; the retired skill had no mode-specific gate file.

- [ ] The audit is read-only (`audit_skill.py --fix` only reports; edits are reviewed changes).
- [ ] `--mode source` and `--mode installed` are both run before a skill is declared compliant.
- [ ] Findings are reported with rule id, path and line; errors fail the exit code, warnings do not unless `--strict`.
- [ ] Description, name, size budgets, contents lists, direct references and `evals/evals.json` are checked against `skill-authoring-contract.json`.

## Mode: create-docker-skill

[PASSED] The scaffold creates a valid `Dockerfile` and `docker-compose.yml`.
[PASSED] The scaffold creates a `security_override.json` whitelisting the `subprocess` command to build the image.
[FAILED] The sub-agent attempts to map host data volumes without explicit user consent.
[FAILED] The `./SKILL.md` does not document the image build requirements.

## Mode: create-azure-agent

[PASSED] The generated `scaffold_azure_agent.py` requests required environment variables via os.environ.get safely.
[PASSED] The generated agent skill declares the target API model.
[FAILED] The scaffold outputs hardcoded `.env` files with sample tokens rather than templates.
[FAILED] The `./SKILL.md` does not explain how to pass credentials to the sub-agent.

## Mode: create-mcp-integration

**Purpose**: Verify the system scaffolds standard Model Context Protocol servers.

## 1. Manifest Appending
- **[PASSED]**: The generated schema is correctly appended to the plugin's root `.mcp.json` file.
- **[FAILED]**: The schema creates a misnamed file or overwrites an existing server instead of appending.

## Mode: ecosystem-standards

**Purpose**: Ensure the active auditing logic detects legacy layout structures against the Anthropic/Microsoft plugin standards.

## 1. Error Emitting
- **[PASSED]**: The ecosystem auditor outputs distinct error codes enabling programmatic CI/CD blocking when plugins violate the 500-line skill rule or miss `.claude-plugin/plugin.json`.
- **[FAILED]**: The standard review script crashes or fails to recursively check all local directories.

## Mode: ecosystem-authoritative-sources

**Purpose**: Ensure the agent has read-access to PDF specs and universal fallback guidance.

## 1. Specification Parsing
- **[PASSED]**: The agent is successfully able to route queries into the internal reference repository to understand `mcp.json` specifications directly from the source.
- **[FAILED]**: The agent ignores the authoritative sources and hallucinates legacy schemas.
