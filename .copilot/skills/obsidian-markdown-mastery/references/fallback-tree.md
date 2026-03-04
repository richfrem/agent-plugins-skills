# Procedural Fallback Tree: Obsidian Markdown Mastery

## 1. parser.py Not Found
If `parser.py` cannot be located at `plugins/obsidian-integration/obsidian-parser/parser.py`:
- **Action**: Do NOT write ad-hoc regex to parse markdown. Report that the parser module is missing. Ask the user to verify the plugin is installed correctly.

## 2. OBSIDIAN_VAULT_PATH Not Set
If the `OBSIDIAN_VAULT_PATH` environment variable is not set and a tool needs the vault root:
- **Action**: Default to the project root (current working directory) as per the skill spec. Log a warning. Do NOT fail — this is documented fallback behavior.

## 3. Unsupported Callout Type
If the user requests a callout type not in the supported list (info, warning, error, success, note):
- **Action**: Report the unsupported type. Map to the closest supported type and ask the user to confirm before injecting the callout. Do NOT silently use an arbitrary type.
