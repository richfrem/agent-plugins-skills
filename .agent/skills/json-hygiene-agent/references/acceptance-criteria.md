# Acceptance Criteria: JSON Hygiene Converter

The `json-hygiene` workflow MUST satisfy the following success metrics:

1. **Successful AST Sweeps**: Given any JSON file, the command successfully triggers the Python algorithm to walk the Abstract Syntax Tree looking for key collision.
2. **Determinism**: The script must catch 100% of duplicate keys, regardless of nesting depth, casing, formatting, or if the value is an array, object, int, or string.
3. **Context Window Safety**: The agent must NEVER attempt to print or `cat` massive generated JSON payloads into its own chat context to "look" for keys visually.
