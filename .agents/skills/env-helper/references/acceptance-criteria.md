# Acceptance Criteria: Env-Helper Utility

The `env-helper` workflow MUST satisfy the following success metrics:

1. **Resolution Accuracy**: Given a known environment key, the python command successfully resolves it by walking up the directory tree to find the `.env` file, falling back to process `os.environ`, and finally hardcoded defaults.
2. **Zero Dependencies**: The python script must not `import dotenv` or rely on any local `plugins/` utility modules, allowing it to remain decoupled and avoiding circular import loops across complex meta-plugins.
3. **Context Window Safety**: The agent must NEVER attempt to print the resulting API tokens out into the chat window where they could be logged or compromised.
