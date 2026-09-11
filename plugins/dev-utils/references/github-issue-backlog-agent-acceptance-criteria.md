# Acceptance Criteria: GitHub Issue Backlog Agent

## Functional Criteria
1. **Payload Generation**: Without `--execute`, outputs preview JSON of the issue title, body, and labels.
2. **Taxonomy Conformance**: Verifies labels match taxonomy rules before attempting live execution.
3. **Task Parsing**: Accurately parses task markdown files and maps sections to GitHub issue format.
4. **Safety Scans**: Blocks files containing unredacted credentials or secrets.

## Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md under 80 lines routing to references.
2. **Clear Error Reporting**: Reports missing files or validation failures with clear messages and non-zero exit codes.
