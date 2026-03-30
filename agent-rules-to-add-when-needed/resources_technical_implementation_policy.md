# Standard: Technical Implementation & Linking

## 1. Objective
To provide direct traceability between the high-level documentation and the low-level source artifacts (FMB, XML, Code).

## 2. Checklist
- [ ] **Source Links**:
    - Run `py scripts/documentation/find_source_links.py <ID>` to generate correct paths.
    - Format: `[FormName] [[xml-md]] (...) [[xml]] (...)`.
- [ ] **Attached Libraries**:
    - List all libraries found in the `AttachedLibrary` section of the Form XML.
    - Link them using the standard format (e.g., `[JUSLIB]`).
- [ ] **Database Objects**:
    - If recognized (e.g., PL/SQL Packages), link them.

## 3. Link Verification
- Verify that `[[xml]]` links point to valid `legacy-system/oracle-forms/XML/...` files.
- Verify that `[[xml-md]]` links point to valid `legacy-system/oracle-forms-markdown/XML/...` files.
- Use `scripts/documentation/enrich_links_v2.py` to auto-repair/enhance links where possible.

## 4. Output Format
```markdown
## Technical Implementation
*   **Form Module**: [RCCE0147.fmb] [[MD]] [[XML]]
*   **Libraries Attached**:
    *   [RCC_LIB3] [[XML]]
    *   [ITSLIB] [[XML]]
```
