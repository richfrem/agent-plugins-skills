---
concept: source-parent-project-folder-structure-overview
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/parent-project-folder-structure-overview.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.749146+00:00
cluster: analysis
content_hash: 4a6bc0b13f000571
---

# Source Parent Project Folder Structure Overview

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Source Parent Project Folder Structure Overview

This document outlines the restructured folder hierarchy for the Justin application modernization project. The repository is organized by purpose to distinguish between source data, analysis tools, generated outputs, and modernized code.

##  legacy-system/
Contains all legacy Oracle Forms and database artifacts that serve as our source of truth.
- oracle-forms/ - Source XML exports, PLL libraries, and reports.
- oracle-database/ - Original DB schema: tables, views, packages, constraints, etc.
- oracle-forms-markdown/ - Human-readable Markdown conversions of Oracle Forms.


##  plugins/
Command-line utilities and scripts used for analysis and conversion (tooling only, no outputs).
- xml-to-markdown/ - The core tool for converting legacy XML into documented Markdown.
- form-relationships/ - Python scripts for mapping parent-child form dependencies.
- business-rule-extraction/ - Structured LLM prompts for extracting rules from legacy code.

##  analysis-outputs/
Generated reports and data derived from the legacy system using our analysis tools.
- **Form Relationships:** See scripts/ for dependency analysis outputs:
  - form_relationships.csv (code-detected) - Detected parent-child form references
  - form_relationships.csv (combined-relationships) - Combined analysis
- business-rules/ - Detailed reports on access control and functional rules (by-form and topic-based).

##  modernization/
Where active modernization and development takes place.
- apps/ - The modernized suite including LEA, RCC, JAS, JCS, and JRS (React frontends + .NET backends).
- common/ - Shared logic for both .NET and React.
- docs/ - Central architecture documentation, development guides, and tech stack info.
- archive/ - Superseded LLM conversion attempts and experimental tooling.

##  configuration-as-code/
(Formerly *RoleConfigurationProject*) Demonstrates approaches for defining UI visibility and access rules as portable configuration.


## See Also

- [[parent-project-folder-structure-overview]]
- [[project-folder-structure-guidance]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[project-directory-structure-requirements]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/coding-conventions-agent/references/parent-project-folder-structure-overview.md`
- **Indexed:** 2026-04-17T06:42:09.749146+00:00
