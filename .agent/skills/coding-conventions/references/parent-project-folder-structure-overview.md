# Source Parent Project Folder Structure Overview

This document outlines the restructured folder hierarchy for the Justin application modernization project. The repository is organized by purpose to distinguish between source data, analysis tools, generated outputs, and modernized code.

##  [legacy-system/](../../legacy-system/)
Contains all legacy Oracle Forms and database artifacts that serve as our source of truth.
- [oracle-forms/](../../legacy-system/oracle-forms/) - Source XML exports, PLL libraries, and reports.
- [oracle-database/](../../legacy-system/oracle-database/) - Original DB schema: tables, views, packages, constraints, etc.
- [oracle-forms-markdown/](../../legacy-system/oracle-forms-markdown/) - Human-readable Markdown conversions of Oracle Forms.


##  [tools/](../../tools/)
Command-line utilities and scripts used for analysis and conversion (tooling only, no outputs).
- [xml-to-markdown/] (Reference Missing: ) - The core tool for converting legacy XML into documented Markdown.
- [form-relationships/] (Reference Missing: ) - Python scripts for mapping parent-child form dependencies.
- [business-rule-extraction/] (Reference Missing: ) - Structured LLM prompts for extracting rules from legacy code.

##  [analysis-outputs/] (Reference Missing: )
Generated reports and data derived from the legacy system using our analysis tools.
- **Form Relationships:** See [tools/form-relationships/scripts/] (Reference Missing: ) for dependency analysis outputs:
  - [form_relationships.csv](../../legacy-system/reference-data/collections/code-detected/form_relationships.csv) - Detected parent-child form references
  - [form_relationships.csv](../../legacy-system/reference-data/collections/combined-relationships/form_relationships.csv) - Combined analysis
- [business-rules/] (Reference Missing: ) - Detailed reports on access control and functional rules (by-form and topic-based).

##  [modernization/](../../_archive_modernization/)
Where active modernization and development takes place.
- [apps/](../../_archive_modernization/apps/) - The modernized suite including LEA, RCC, JAS, JCS, and JRS (React frontends + .NET backends).
- [common/](../../_archive_modernization/apps/common/) - Shared logic for both .NET and React.
- [docs/](../../docs/) - Central architecture documentation, development guides, and tech stack info.
- [archive/] (Archived) - Superseded LLM conversion attempts and experimental tooling.

##  [configuration-as-code/] (Reference Missing: )
(Formerly *RoleConfigurationProject*) Demonstrates approaches for defining UI visibility and access rules as portable configuration.
