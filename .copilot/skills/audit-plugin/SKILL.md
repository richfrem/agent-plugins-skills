---
name: audit-plugin
description: Audits a local plugin directory to ensure it perfectly matches the Agent Skills and Claude Plugin Open Standards.
disable-model-invocation: false
allowed-tools: Bash, Read, Write
---

# Ecosystem Auditor

## Overview
This skill acts as the final CI/CD review gate for the agent ecosystem. It delegates to the `agent-plugin-analyzer` to execute a deep, multi-dimensional semantic scrub of a target plugin against our strict Level 4 specifications.

## Instructions
When instructed to audit or validate a plugin, or to verify if a skill is compliant, use the Python analyzer script. Do not use legacy basic audit scripts.

**Usage:**
```bash
python3 "plugins reference/agent-plugin-analyzer/skills/analyze-plugin/scripts/analyze_plugin.py" --dir <path-to-plugin> --security
```

*(Note: Always run with the `--security` flag to catch P0 malware heuristics before reviewing architecture.)*

**Parameters:**
- `--dir`: The absolute or relative path to the root of the plugin being audited.

**Audit Checks Include:**
- **Execution Patterns (L4):** Checks for Graduated Autonomy, Source Transparency, Escalation Triggers.
- **State Management:** Checks for conditional inclusions and explicit state checklists.
- **Architectural Strictness:** Validates `CONNECTORS.md`, `README.md`, YAML frontmatter purity.
- **Security Vectors:** Flags un-sandboxed execution, prompt injection vulnerabilities, and raw binary execution.

**Remediation & Next Steps:**
If the script outputs a low Maturity Score or fails the `--security` gate (which forces an immediate `sys.exit(1)`), you MUST read the generated output report and actively use your file editing tools to fix the compliance issues in the target plugin. Run the audit again until it achieves Level 3 or higher.


## Next Actions
- Offer to run `create-skill` to fix identified gaps.
- Offer to run `create-stateful-skill` to upgrade to L4 maturity.
