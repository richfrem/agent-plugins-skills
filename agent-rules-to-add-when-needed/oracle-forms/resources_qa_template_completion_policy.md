---
trigger: always_on
---

# Standard: QA Template Completion

**Status**: Mandatory
**Applies To**: All `Overview` Documents (Forms, Reports, Libraries)

## Requirement
Every section defined in the official templates (e.g., `form-overview-template.md`) MUST be present and populated in the final artifact. Leaving sections blank or removing them without justification is strictly prohibited.

## Verification Checklist
Before marking any document as "Remediated" or "Complete":

1.  **Header Metadata**: Check Title, Source Document Link.
2.  **Purpose**: Ensure a clear, non-technical summary exists.
3.  **Navigation**: All entry points (Caller Forms, Menus) are listed.
4.  **Security**:
    *   Associated Roles listing (Active only).
    *   Fine-Grained checks (Code restrictions).
5.  **Validated Dependencies**: Table present with "Active/Conditional" status.
6.  **Business Logic**:
    *   "Discovered Business Rules" section populated.
    *   Links to `business-rules/BR-XXXX.md` are valid.
7.  **Technical Implementation**:
    *   Libraries (PLL) listed.
    *   Database Packages listed.
    *   Source Code link present.

## Handling "None"
If a section genuinely has no content (e.g., a form calls no other forms):
*   **DO NOT** remove the section.
*   **DO** mark it explicitly: "None Detected" or "No external dependencies found."
