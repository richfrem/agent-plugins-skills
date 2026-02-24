# Acceptance Criteria: create-legacy-command

**Purpose**: Verify slash-commands migrate properly into markdown-based structures without raw Python entrypoints.

## 1. Pure Markdown Workflow
- **[PASSED]**: The command is generated entirely as a `.md` file inside `commands/` with strict YAML frontmatter, utilizing prompt-based engineering instead of raw python logic.
- **[FAILED]**: The tool attempts to scaffold a python script as a command instead of an LLM prompt.
