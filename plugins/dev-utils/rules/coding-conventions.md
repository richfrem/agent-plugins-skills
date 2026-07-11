---
description: PROJECT CODING POLICY - Universal conventions for Python, TypeScript, and C#.
globs: ["*.py", "*.ts", "*.js", "*.cs"]
enforcement: Mandatory - All code must comply. Audited by workspace_conventions_auditor.py
---

## ⚖️ AUTHORITY & SCOPE

**This is PROJECT POLICY** - Not a style guide. Binding on all development.

- **Applies to:** All Python, TypeScript, JavaScript, and C# in repository
- **No exemptions:** Every script, every function, every file
- **Auditor:** `workspace_conventions_auditor.py` enforces across entire codebase
- **Current Status:** 442/454 files in violation (in progress remediation)

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

