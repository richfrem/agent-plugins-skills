---
name: xml-to-markdown
description: Convert Oracle Forms XML exports into Markdown. Now implements Pre-Conversion Classification for large files and 6-step structural routing.
disable-model-invocation: false
tier: 1
---

# XML to Markdown

## Installation & Setup

> [!IMPORTANT]
> This skill requires specific environment setup after installation (e.g., via `npx skills add`).

### Node.js Plugin Setup (e.g., xml-to-markdown)
1. **npm install**: Run this inside the `.agents/skills/xml-to-markdown` directory. This installs critical dependencies:
   - `xml2js`: The primary XML parser.
   - `@xmldom/xmldom`
   - `fast-xml-parser`
   - `prettier`
2. **npm audit fix**: Run to resolve any high-level vulnerabilities in nested dependencies.

> [!CAUTION]
> **xml2js** MUST be installed locally within the `.agents/skills/xml-to-markdown` directory. Because this script is an ESM (ECMAScript Module), it will not resolve packages installed at the project root unless explicitly linked.

### Python Plugin Setup (e.g., legacy-system-database)
Most other Oracle parsing scripts in this ecosystem are Python-based and require:
1. **pip install -r requirements.txt**: Ensures presence of libraries like `pyyaml`, `click`, and `typer`.
2. **pip-compile**: (For developers) Use this to keep lockfiles in sync if requirements change.


## Overview

Converts verbose Oracle XML exports (`_fmb.xml`, `_pll.xml`, `_rdf.xml`) into human-readable Markdown format for downstream AI processing and extraction.

## Document Format Agnosticism
Before executing, seamlessly handle the user's input type. If they provide:
- **File Path**: Proceed directly.
- **Directory**: Locate all valid XML children recursively.
- **Relative String**: Use workspace context to resolve absolute paths.

## Pre-Conversion Classification
Check the size of the target `.xml` files. 
- If the file is **> 20MB**: Do not attempt to process it linearly. Alert the user that the structure implies excessive size (e.g., massive internal graphical structures or embedded binary icons in Reports). Suggest chunking the execution limits or selectively parsing specific form triggers first.

## Phase-Based Workflows (6-Step Procedure)

### Phase 1: Ingestion
Accept inputs agnostically. Confirm targets.

### Phase 2: Classification
Assess sizes. Apply the `>20MB` chunking advisory if applicable.

### Phase 3: Orchestration
Select the appropriate conversion script based on the target extension:
- `.fmb.xml` -> `/xml-to-markdown_convert-form`
- `.pll.xml` -> `/xml-to-markdown_convert-pll`
- `.rdf.xml` -> `/xml-to-markdown_convert-report`

### Phase 4: Parsing
Execute the parser, gracefully trapping any malformed syntax errors without failing silently.

### Phase 5: Markdown Generation
Output the `.md` files directly adjacent to the `.xml` sources in the workspace.

### Phase 6: Source Transparency Review
Conclude by summarizing the operational success using the Transparency Declaration:
**Sources Checked / Converted:** [List of paths]
**Sources Unavailable / Failed:** [List of issues]
**Next Recommended Action:** Proceed to Code Extraction.
