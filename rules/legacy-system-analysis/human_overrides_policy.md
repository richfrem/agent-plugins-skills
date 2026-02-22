# Standard: Human Overrides (Single Source of Truth)

## 1. Critical Rule
**ALWAYS check `legacy-system/human-overrides/` before documenting any form or application.**
Information in the `human-overrides` directory **supersedes** all code analysis and auto-generated content.

## 2. Process
1.  **Check for Overrides**: Look for files matching `forms/LEAM0000-Override.md`.
2.  **Read First**: Understand the human verification.
3.  **Integrate Verbatim**: Do not overwrite verified facts with code assumptions.
4.  **Reference**: Add the standard note:
    ```markdown
    > [!NOTE]
    > **Human Verification**: This document includes manually verified overrides.
    > See [OverrideFile.md] (Reference Missing: file.md).
    ```
