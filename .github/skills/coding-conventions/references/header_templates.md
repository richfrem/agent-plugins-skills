# Header Templates — Detailed Reference

## Extended Python CLI/Tool Header (Gold Standard)

For CLI tools and complex scripts (especially in `plugins/` and `scripts/`):

```python
#!/usr/bin/env python3
"""
{{script_name}} (CLI)
=====================================

Purpose:
    Detailed multi-paragraph description of what this script does.
    Explain its role in the system and when it should be used.

    This tool is critical for [context] because [reason].

Layer: Investigate / Codify / Curate / Retrieve  (Pick one)

Usage Examples:
    python plugins/path/to/script.py --target JCSE0004 --deep
    python plugins/path/to/script.py --target MY_PKG --direction upstream --json

Supported Object Types:
    - Type 1: Description
    - Type 2: Description

CLI Arguments:
    --target        : Target Object ID (required)
    --deep          : Enable recursive/deep search (optional)
    --json          : Output in JSON format (optional)
    --direction     : Analysis direction: upstream/downstream/both (default: both)

Input Files:
    - File 1: Description
    - File 2: Description

Output:
    - JSON to stdout (with --json flag)
    - Human-readable report (default)

Key Functions:
    - load_dependency_map(): Loads the pre-computed dependency inventory.
    - find_upstream(): Identifies incoming calls (Who calls me?).
    - find_downstream(): Identifies outgoing calls (Who do I call?).
    - deep_search(): Greps source code for loose references.

Script Dependencies:
    - dependency1.py: Purpose
    - dependency2.py: Purpose

Consumed by:
    - parent_script.py: How it uses this script
"""
```

> The `manage_tool_inventory.py` tool auto-extracts the "Purpose:" section from this header.

## TypeScript Utility Module Header (Extended)

```javascript
/**
 * path/to/file.js
 * ================
 *
 * Purpose:
 *   Brief description of the component's responsibility.
 *   Explain the role in the larger system.
 *
 * Input:
 *   - Input source 1 (e.g., XML files, JSON configs)
 *   - Input source 2
 *
 * Output:
 *   - Output artifact 1 (e.g., Markdown files)
 *   - Output artifact 2
 *
 * Assumptions:
 *   - Assumption about input format or state
 *   - Assumption about environment or dependencies
 *
 * Key Functions/Classes:
 *   - functionName() - Brief description
 *   - ClassName - Brief description
 *
 * Usage:
 *   import { something } from './file.js';
 *   await something(params);
 *
 * Related:
 *   - relatedFile.js (description)
 *   - relatedPolicy.md (description)
 *
 * @module ModuleName
 */
```

## React Component Header (Short Form)

```typescript
/**
 * path/to/Component.tsx
 *
 * Purpose: Brief description of the component's responsibility.
 * Layer: Presentation layer (React component).
 * Used by: Parent components or route definitions.
 */
```

## Comment Style Guide

| Do | Don't |
|----|-------|
| `// TODO(#123): Add error handling for timeout` | `// TODO: fix this` |
| `// Workaround for Oracle Forms trigger order dependency` | `// Set x to 5` |
