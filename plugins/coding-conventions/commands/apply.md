---
description: Apply the coding conventions — review code or generate compliant headers
argument-hint: "[review <file>] | [header python|js|csharp]"
---

# Apply Coding Conventions

## Review a File for Compliance
Check if a file follows the project's coding conventions:
1. Read the file
2. Check for proper header (Purpose, Layer, Usage)
3. Check function documentation (dual-layer)
4. Check naming conventions
5. Report findings

## Generate a Compliant Header

### Python
Use template from `${CLAUDE_PLUGIN_ROOT}/templates/python-tool-header-template.py`

### JavaScript/TypeScript
Use template from `${CLAUDE_PLUGIN_ROOT}/templates/js-tool-header-template.js`

### C#/.NET
```csharp
// path/to/File.cs
// Purpose: Class responsibility.
// Layer: Service / Data access / API controller.
// Used by: Consuming services.
```

## Pre-Commit Checklist
- [ ] File has proper header
- [ ] All functions have type hints (Python) / JSDoc (TS) / XML docs (C#)
- [ ] Naming follows convention table
- [ ] No function > 50 lines
- [ ] No nesting > 3 levels
