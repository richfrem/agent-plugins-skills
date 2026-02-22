---
description: Universal coding conventions for Python, TypeScript, and C#.
globs: ["*.py", "*.ts", "*.js", "*.cs"]
---

## 📝 Coding Conventions (Summary)

**Full standards → `plugins/coding-conventions/skills/conventions-agent/SKILL.md`**

### Non-Negotiables
1. **Dual-layer docs** — external comment above + internal docstring inside every non-trivial function/class.
2. **File headers** — every source file starts with a purpose header (Python, TS/JS, C#).
3. **Type hints** — all Python function signatures use type annotations.
4. **Naming** — `snake_case` (Python), `camelCase` (JS/TS), `PascalCase` (C# public).
5. **Refactor threshold** — 50+ lines or 3+ nesting levels → extract helpers.
6. **Tool registration** — all `plugins/` scripts registered in `tool_inventory.json`.
7. **Manifest schema** — use simple `{title, description, files}` format (ADR 097).
