# Improvement Mapping

This reference maps discovered pattern categories to the specific files and specs they should improve in our core meta-architecture. Use this when synthesizing recommendations.

## Target 1: agent-scaffolders

Changes here affect how *new* plugins and skills are bootstrapped.

| Discovery Category | Modify File | Type of Change |
| :--- | :--- | :--- |
| **Structural Innovation** | `scripts/scaffold.py` | Update `create_plugin()` or `create_skill()` directory generation logic. |
| **Quality Pattern** | `skills/create-skill/templates/SKILL.md.jinja` | Embed new checklists or compliance instructions into standard templates. |
| **Execution Pattern** | `skills/create-skill/SKILL.md` | Add instructions on when to generate branching/phase logic. |
| **Meta Pattern** | `plugins reference/agent-scaffolders/plugin.json` | Add entire new scaffolder skills (e.g., `create-connector`) |

## Target 2: agent-skill-open-specifications

Changes here affect the written law of the ecosystem.

| Discovery Category | Modify File | Type of Change |
| :--- | :--- | :--- |
| **Any Pattern** | `skills/ecosystem-authoritative-sources/reference/skills.md` | Add to the "Best Practices & Authoring Guidelines" section. |
| **Integration Pattern** | `skills/ecosystem-authoritative-sources/reference/plugins.md` | Add details about how `mcp.json` or `CONNECTORS.md` should be standardized. |
| **Anti-Pattern** | `skills/ecosystem-standards/SKILL.md` | Add new hard requirements to the code audit phase. |
| **Anti-Pattern** | `agent-scaffolders/scripts/audit.py` | Codify the anti-pattern as an automatic failure in the `audit_plugin()` script. |

## Target 3: agent-plugin-analyzer

Changes here improve our ability to analyze future plugins.

| Discovery Category | Modify File | Type of Change |
| :--- | :--- | :--- |
| **Any Pattern** | `skills/analyze-plugin/references/pattern-catalog.md` | Register the new pattern so it is recognized in future scans. |
| **Analysis Gap** | `skills/analyze-plugin/SKILL.md` | Add new checks to Phase 3 (Content Analysis). |

## Target 4: Domain Plugins (oracle-legacy-system-analysis)

Changes here apply knowledge-work patterns to our primary engineering domain.

| Discovery Category | Mapping Scenario |
| :--- | :--- |
| **Severity Frameworks** | Legal deviation (GREEN/RED) → Oracle API migration risk (GREEN/RED). |
| **Decision Tables** | Chart selection guide → Forms-to-React migration strategy table. |
| **Output Templates** | HTML Sales artifacts → HTML Code Modernization analysis reports. |
| **Playbook Reviews** | Contract standard positions → Architecture standard positions for DB refactoring. |
