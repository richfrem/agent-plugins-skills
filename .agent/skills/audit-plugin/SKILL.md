---
name: audit-plugin
description: Audits a local plugin directory to ensure it perfectly matches the Agent Skills and Claude Plugin Open Standards.
disable-model-invocation: false
---

# Ecosystem Auditor

## Overview
This skill acts as the final CI/CD review gate for the agent ecosystem. It runs a deterministic Python script to analyze a plugin's directory structure, manifest files, and nested skills against our strict specifications.

## Instructions
When instructed to audit or validate a plugin, or to verify if a skill is compliant, use the Python auditor script.

**Usage:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit.py --path <path-to-plugin>
```

**Parameters:**
- `--path`: The absolute or relative path to the root of the plugin being audited.

**Audit Checks Include:**
- Presence of `.claude-plugin/plugin.json`
- Verification of standard directories (`skills/`, `agents/`, etc.)
- Detection of `SKILL.md` files exceeding 500 lines.
- **Critical Failure:** Detection of any `.sh` or `.ps1` files inside skill script directories (Only Python `.py` is allowed cross-platform).

**Remediation:**
If the script outputs `❌ AUDIT FAILED ❌`, you MUST read the exact error messages and actively use your file editing tools to fix the compliance issues in the target plugin. Run the audit again until it passes.
