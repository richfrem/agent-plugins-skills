---
trigger: always_on
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

**Full standards → `.agents/skills/coding-conventions-agent/SKILL.md`**

### Non-Negotiables
1. **Dual-layer docs** — external comment above + internal docstring inside every non-trivial function/class.
2. **File headers** — every source file starts with a purpose header (Python, TS/JS, C#).
   - **Crucial**: The header must explicitly list **Key Input Dependencies** (e.g. required configuration files, environment variables, or databases like `config.json` or `schema.sql`).
   - **Index & Preservation Directive**: File headers must contain a complete index list of all functions, methods, and procedures present in the file. Never remove or reduce existing utility documentation (like usage examples, DOM structures, or technical flags lists) during updates—always preserve and enrich.
   - **Purpose**: This enables clean, token-efficient discovery in new agent sessions. Incoming agents can scan the top of a file to instantly map its capabilities and required state files without reading the full implementation.
3. **Type hints** — all Python function signatures use type annotations.
4. **Naming** — `snake_case` (Python), `camelCase` (JS/TS), `PascalCase` (C# public).
5. **Refactor threshold** — split a function when it exceeds **both** a length and a complexity signal, not either alone (revised 2026-09-05, see `references/map-debt.md` DEBT-20260905-08):
   - **Length**: soft warning at 50 lines, hard ceiling at 100 lines (physical line count), regardless of complexity — an overly long function is a readability problem even when flat.
   - **Complexity**: soft warning at McCabe 10, hard ceiling at McCabe 15 (count of `if`/`for`/`while`/`except`/`and`/`or`/`match`-`case` branches + 1).
   - **Structural exemptions from the length ceiling only** (the complexity ceiling still applies): declarative dict/mapping literals, `match`/`case` dispatch blocks, `argparse` `add_argument`/`add_parser` sequences, and large string-template construction (f-strings/`.format()` building multi-section output) — these inflate line count without adding branching logic.
   - **No exemption by subject matter** — a function touching SQLite, state transitions, or any other "transactional" logic is exempt only if its actual branch count clears the complexity ceiling, same as anything else.
6. **Manifest schema** — use simple `{title, description, files}` JSON/YAML format.

### 🔍 Automated Compliance Checks
To audit workspace source code compliance against these rules, run the developer conventions auditor script:
```bash
python3 .agents/skills/coding-conventions-agent/scripts/workspace_conventions_auditor.py
```
This utility outputs a detailed audit breakdown under `temp/workspace_conventions_report.md`.