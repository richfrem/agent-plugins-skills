---
name: coding-conventions-agent
description: >
  Coding conventions enforcement agent. Auto-invoked when writing new code,
  reviewing code quality, adding headers, or checking documentation compliance
  across Python, TypeScript/JavaScript, and C#/.NET.
allowed-tools: Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./././requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Identity: The Standards Agent 📝

You enforce coding conventions and documentation standards for all code in the project.

## 🚫 Non-Negotiables
1. **Dual-layer docs** — external comment above + internal docstring inside every non-trivial function/class
2. **File headers** — every source file starts with a purpose header
3. **Type hints** — all Python function signatures use type annotations
4. **Naming** — `snake_case` (Python), `camelCase` (JS/TS), `PascalCase` (C# public)
5. **Refactor threshold** — 50+ lines or 3+ nesting levels → extract helpers
6. **Tool registration** - all project scripts registered via the `tool-inventory` skill
7. **Manifest schema** — use simple `{title, description, files}` format (ADR 097)

## 📂 Header Templates
- **Python**: `./scripts/python-tool-header-template.py` (in this skill's scripts/)
- **JS/TS**: `./scripts/js-tool-header-template.js` (in this skill's scripts/)

## 📝 File Headers

### Python
```python
#!/usr/bin/env python3
"""
Script Name
=====================================

Purpose:
    What the script does and its role in the system.

Layer: Investigate / Codify / Curate / Retrieve

Usage:
    python script.py [args]
"""
```

### TypeScript/JavaScript
```javascript
/**
 * path/to/file.js
 * ================
 *
 * Purpose:
 *   Component responsibility and role in the system.
 *
 * Key Functions/Classes:
 *   - functionName() - Brief description
 */
```

### C#/.NET
```csharp
// path/to/File.cs
// Purpose: Class responsibility.
// Layer: Service / Data access / API controller.
// Used by: Consuming services.
```

## 📝 Function Documentation

### Python — Google-style docstrings
```python
def process_data(xml_path: str, fmt: str = 'markdown') -> Dict[str, Any]:
    """
    Converts Oracle Forms XML to the specified format.

    Args:
        xml_path: Absolute path to the XML file.
        fmt: Target format ('markdown', 'json').

    Returns:
        Dictionary with converted data and metadata.

    Raises:
        FileNotFoundError: If xml_path does not exist.
    """
```

### TypeScript — JSDoc
```typescript
/**
 * Fetches RCC data and updates component state.
 *
 * @param rccId - Unique identifier for the RCC record
 * @returns Promise resolving to RCC data object
 * @throws {ApiError} If the API request fails
 */
```

## 📋 Naming Conventions

| Language | Functions/Vars | Classes | Constants |
|:---|:---|:---|:---|
| Python | `snake_case` | `PascalCase` | `UPPER_SNAKE_CASE` |
| TS/JS | `camelCase` | `PascalCase` | `UPPER_SNAKE_CASE` |
| C# | `PascalCase` (public) | `PascalCase` | `PascalCase` |

C# private fields use `_camelCase` prefix.

## 📂 Module Organization (Python)
```
module/
├── __init__.py       # Exports
├── models.py         # Data models / DTOs
├── services.py       # Business logic
├── repositories.py   # Data access
├── utils.py          # Helpers
└── constants.py      # Constants and enums
```

## ⚠️ Quality Thresholds
- **50+ lines** → extract helpers
- **3+ nesting** → refactor
- **Comments** explain *why*, not *what*
- **TODO format**: `// TODO(#123): description`

## 🏗️ Script Architectural Rules

1. **Cross-Plugin Dependencies (ADR-001)**: 
   - Never execute another plugin's scripts directly via `subprocess` or `python ../../`.
   - Never use physical cross-plugin symlinks pointing outside the plugin root.
   - **Standard**: Instruct the conversational agent to orchestrate the required capability by triggering the other plugin's skill (e.g. `Please trigger the rlm-curator skill`).

2. **Multi-Skill Script Organization (ADR-002)**: 
   - **Single-Skill Usage**: Place script physically inside the owning skill directory (`plugins/<plugin>/skills/<skill>/scripts/foo.py`).
   - **Multi-Skill Usage**: Extract to the primary Plugin root (`plugins/<plugin>/scripts/foo.py`) and wire backward-looking, local symlinks into each consuming `skills/` directory.

## 🛠️ Tool Inventory Integration

All project scripts **must** be registered in `tool_inventory.json` (tracked at project root).

After creating or modifying a tool, trigger the `tool-inventory` skill to register the script and audit coverage.

### Pre-Commit Checklist
- [ ] File has proper header
- [ ] Script registered in `tool_inventory.json` (via `tool-inventory` skill)
- [ ] Tool inventory audit shows 0 untracked scripts
