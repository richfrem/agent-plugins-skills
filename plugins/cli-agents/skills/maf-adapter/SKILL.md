---
name: maf-adapter
plugin: cli-agents
description: >-
  Provides validation, setup guidance, and a local test harness simulator to run
  skills within the Microsoft Agent Framework (MAF).
allowed-tools: Bash, Read, Write
---

# Microsoft Agent Framework Adapter (maf-adapter)

Validates plugin manifests and simulates agent skill execution within the Microsoft Agent Framework (MAF v1.6/v1.7+).

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- **Manifest Hygiene**: Manifests loaded into MAF must omit banned/unsupported fields (`skills`, `agents`, `hooks`).
- **Frontmatter Requirement**: All skills must include valid YAML frontmatter blocks delimited by `---` with `name` and `allowed-tools`.
- **Local Simulation First**: Test and simulate skills locally via `test_harness.py` before deploying to Azure Agent Service.
- **Read-Only Test Frame**: The simulation harness must execute in read-only mode without mutating the target skill or plugin files.

## Quick start

```bash
# Validate plugin manifest for MAF compatibility
python3 plugins/cli-agents/scripts/test_harness.py --validate --plugin plugins/<plugin>

# Simulate skill execution locally under MAF
python3 plugins/cli-agents/scripts/test_harness.py \
  --skill plugins/<plugin>/skills/<skill-name> \
  --instruction "Analyze workspace"
```

## Workflow

1. **Phase 1: Manifest Validation**: Run `test_harness.py --validate` against the target plugin directory to verify schema compatibility and absence of banned root keys.
2. **Phase 2: Frontmatter Verification**: Verify that the target skill's `SKILL.md` contains valid frontmatter declaring allowed tools and clean descriptions.
3. **Phase 3: Execution Simulation**: Execute `test_harness.py --skill` with mock input context to assemble and verify the MAF execution frame.
4. **Phase 4: Output Inspection**: Review the generated execution frame to verify clean parameter passing and tool bounds.

## Verification

```bash
# Validate plugin manifest
python3 plugins/cli-agents/scripts/test_harness.py --validate --plugin plugins/cli-agents

# Audit skill compliance
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/cli-agents/skills/maf-adapter --mode source
```

## References
- [acceptance-criteria.md](references/acceptance-criteria.md) - Plugin and skill acceptance criteria for MAF.
