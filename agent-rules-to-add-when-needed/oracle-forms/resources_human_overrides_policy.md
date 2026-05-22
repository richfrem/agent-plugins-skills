# Standard: Human Overrides (Single Source of Truth)

## 1. Critical Rule
**ALWAYS check `legacy-system/human-overrides/` before documenting any form or application.**
Information in the `human-overrides` directory **supersedes** all code analysis and auto-generated content.

## 2. Authenticity & Provenance Gate (MANDATORY)
Before accepting an override, you MUST verify its authenticity:
1. The override file MUST contain a valid `Signature:` field (e.g., email or verified username).
2. The override file MUST contain a `Review State: APPROVED` tag.
If either of these are missing, you MUST REJECT the override as an unverified draft and alert the user.

## 3. Process
1.  **Check for Overrides**: Look for files matching `forms/LEAM0000-Override.md`.
2.  **Verify Provenance**: Ensure Signature and Approved tags exist.
3.  **Read First**: Understand the human verification.
4.  **Integrate Verbatim**: Do not overwrite verified facts with code assumptions.
5.  **Reference**: Add the standard note:
    ```markdown
    > [!NOTE]
    > **Human Verification**: This document includes manually verified overrides.
    > See [OverrideFile.md] (Signed by: ...).
    ```
