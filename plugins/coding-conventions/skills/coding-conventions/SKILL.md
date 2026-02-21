---
name: coding-conventions
description: >
  Coding conventions and documentation standards for Project Sanctuary across Python,
  TypeScript/JavaScript, and C#/.NET codebases. Use when: (1) writing new code files or
  functions, (2) reviewing code for style and documentation compliance, (3) adding file
  headers or docstrings, (4) creating new tools that need inventory registration,
  (5) refactoring code that exceeds complexity thresholds, (6) setting up module structure.
  Covers file headers, function documentation, naming conventions, and tool inventory integration.
---

# Coding Conventions

## Dual-Layer Documentation

Every non-trivial code element needs two layers:
- **External comment/header** — scannable description above the definition
- **Internal docstring** — detailed docs inside the definition

## File Headers

Every source file starts with a header describing its purpose.

### Python Files

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

Related:
    - related_script.py
"""
```

For CLI tools in `tools/`, use the extended format with Usage Examples, CLI Arguments,
Key Functions, and Script Dependencies sections. See `references/header_templates.md`
for the full gold-standard template.

### TypeScript/JavaScript Files

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

### C#/.NET Files

```csharp
// path/to/File.cs
// Purpose: Class responsibility.
// Layer: Service / Data access / API controller.
// Used by: Consuming services.
```

## Function Documentation

### Python — Google-style docstrings with type hints

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

### TypeScript — JSDoc with `@param`, `@returns`, `@throws`

```typescript
/**
 * Fetches RCC data and updates component state.
 *
 * @param rccId - Unique identifier for the RCC record
 * @returns Promise resolving to RCC data object
 * @throws {ApiError} If the API request fails
 */
async function fetchRCCData(rccId: string): Promise<RCCData> {}
```

### C# — XML doc comments

```csharp
/// <summary>
/// Retrieves RCC details by ID.
/// </summary>
/// <param name="rccId">Unique identifier.</param>
/// <returns>RCC entity with related data.</returns>
public async Task<RCC> GetRCCDetailsAsync(int rccId) {}
```

## Naming Conventions

| Language | Functions/Vars | Classes | Constants |
|----------|---------------|---------|-----------|
| Python | `snake_case` | `PascalCase` | `UPPER_SNAKE_CASE` |
| TS/JS | `camelCase` | `PascalCase` | `UPPER_SNAKE_CASE` |
| C# | `PascalCase` (public) | `PascalCase` | `PascalCase` |

C# private fields use `_camelCase` prefix.

## Code Quality Thresholds

- **50+ lines** in a function → extract helpers
- **3+ nesting levels** → refactor
- **Comments** explain *why*, not *what*
- **TODO format**: `// TODO(#123): description`

## Module Organization (Python)

```
module/
├── __init__.py       # Exports
├── models.py         # Data models / DTOs
├── services.py       # Business logic
├── repositories.py   # Data access
├── utils.py          # Helpers
└── constants.py      # Constants and enums
```

## Tool Inventory Integration

All Python scripts in `tools/` **must** be registered in `tools/tool_inventory.json`.

After creating or modifying a tool:
```bash
python plugins/tool-inventory/scripts/manage_tool_inventory.py add --path "tools/path/to/script.py"
python plugins/tool-inventory/scripts/manage_tool_inventory.py audit
```

The extended Python header's `Purpose:` section is auto-extracted for the RLM cache and tool inventory.

### Pre-Commit Checklist
- [ ] File has proper header
- [ ] Script registered in `tool_inventory.json`
- [ ] `manage_tool_inventory.py audit` shows 0 untracked scripts

## Manifest Schema (ADR 097)

For `.agent/learning/` manifests, use the simple schema:
```json
{
    "title": "Bundle Name",
    "description": "Purpose of the bundle.",
    "files": [
        {"path": "path/to/file.md", "note": "Brief description"}
    ]
}
```
