---
description: Universal coding conventions for Python, TypeScript, and C#.
globs: ["*.py", "*.ts", "*.js", "*.cs"]
---

## 🎯 PURPOSE: Enable Agents to Understand Code at a Glance

Every script must document **what it does, what it needs, and how to use it** in the first 20 lines.

**Why:** In fresh agent sessions, agents cannot afford to spend 5-10 minutes reading implementations or running exploratory commands. By reading a 20-line header, agents must be able to:
- Understand the script's purpose in 30 seconds
- Know what files/APIs/dependencies it requires
- See usage examples without trial-and-error
- Identify key functions without code diving

This transforms agent onboarding from minutes to seconds.

---

## 📝 Coding Conventions (Summary)

**Full standards → `.agents/skills/coding-conventions-agent/SKILL.md` (installed locally via `bridge_installer.py`)**

### Non-Negotiables
1. **Dual-layer docs** — external comment above + internal docstring inside every non-trivial function/class.
2. **File headers** — every source file starts with a purpose header (Python, TS/JS, C#).
   - **Crucial**: The header must explicitly list **Key Input Dependencies** (e.g. private JSON databases like `portfolio.json` or `cash_flows.json`).
   - **Purpose**: This enables clean, token-efficient discovery in new agent sessions. Incoming agents can scan the top of a file to instantly map its capabilities and required state files without reading the full implementation.
3. **Type hints** — all Python function signatures use type annotations.
4. **Naming** — `snake_case` (Python), `camelCase` (JS/TS), `PascalCase` (C# public).
5. **Refactor threshold** — 50+ lines or 3+ nesting levels → extract helpers.
6. **Tool registration** — all `plugins/` scripts registered in `plugins/tool_inventory.json`.
7. **Manifest schema** — use simple `{title, description, files}` format (ADR 097).

### 🔍 Automated Compliance Checks
To audit workspace source code compliance against these rules, run the developer conventions auditor script:
```bash
python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py
```
This utility outputs a detailed audit breakdown under `temp/workspace_conventions_report.md`.
