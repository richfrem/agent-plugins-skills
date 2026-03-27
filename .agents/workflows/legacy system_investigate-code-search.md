---
description: Search across all stored PL/SQL (Packages, Procs, Triggers) for specific patterns.
inputs: [FilePath, SearchTerm]
tier: 2
---

# /investigate-code-search

**Purpose:** Search across all stored PL/SQL (Packages, Procs, Triggers) for specific patterns.

**When to use:** To find specific code patterns, function calls, or terms in Oracle Forms Markdown or PL/SQL files.

**Modes:**

**1. Text Search:**
```bash
python scripts/search_plsql.py --file [FilePath] --term "SEARCH_TERM"
```

**2. Regex Search:**
```bash
python scripts/search_plsql.py --file [FilePath] --term "PATTERN.*" --regex
```

**3. Structure Extraction (Forms only):**
```bash
python scripts/search_plsql.py --file [FilePath] --structure
```
Extracts: TabPages, Blocks, Canvases, Windows, ProgramUnits, Triggers.

**4. Search with Context Lines:**
```bash
python scripts/search_plsql.py --file [FilePath] --term "keyword" --context 3
```

**5. JSON Output:**
```bash
python scripts/search_plsql.py --file [FilePath] --term "keyword" --json
```

**Examples:**
```bash
# Find all RAISE_APPLICATION_ERROR in a package
python scripts/search_plsql.py --file legacy-system/oracle-database/source/Packages/JUSTIN_DEMS_INTERFACE.sql --term "RAISE_APPLICATION_ERROR"

# Analyze form structure
python scripts/search_plsql.py --file legacy-system/oracle-forms-markdown/XML/jcse0030-FormModule.md --structure --json
```

**See Also (Cross-File Search):**
- `/investigate-lineage` - Find all callers/callees of an object
- `dependencies.py --deep` - Grep all source directories for references
- `search_collection.py` - Look up object type and path

// turbo