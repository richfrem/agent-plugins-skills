---
description: Scaffold a new APM-native package with skills, agents, commands, hooks, MCP, governance docs, and validation scaffolding.
argument-hint: "[package-name] [--path ./target] [--targets copilot,claude,cursor] [--governance experimental|team|enterprise]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# create-apm-package

Scaffold a new APM-native package from scratch using the existing agent-scaffolders standards. This command creates a dedicated `.apm/` source tree for governed agent assets. Note: APM commands are authored in `.apm/prompts/`.

## Usage

```bash
/create-apm-package my-package --path ./packages --governance team
```

## Workflow

1. **Discovery**: Identifies if the target directory is safe for a new APM package.
2. **Strategy**: Confirms metadata (author, version, targets) and governance lane.
3. **Execution**: Invokes `scripts/scaffold_apm.py` to build the structure.
4. **Validation**: Runs `scripts/validate_apm_package.py` to ensure compliance.
5. **Handoff**: Provides a summary report and next steps for primitive authoring.

## Governance Lanes

- **experimental**: Minimal docs, no enterprise policy.
- **team**: README and governance.md required.
- **enterprise**: Full audit trail, apm-policy.yml, and validation report required.

> [!IMPORTANT]
> Do not use this command for existing plugin migration; use `/convert-plugin-to-apm` instead to preserve existing structures.
