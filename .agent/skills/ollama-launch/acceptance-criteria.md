# Acceptance Criteria: Ollama Launch

This skill MUST satisfy the following success metrics:

1. **Pre-flight Accuracy**: Before starting any processes, the agent must check if Ollama is already active on `port 11434` to prevent double-boxing or port collision errors.
2. **Determinism**: The agent successfully brings the engine online or properly surfaces errors (like `command not found`) instead of entering a blind infinite wait state.
