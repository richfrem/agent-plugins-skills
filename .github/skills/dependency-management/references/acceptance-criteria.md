# Acceptance Criteria: dependency-agent

**Purpose**: Ensure the agent strictly adheres to the progressive disclosure architecture and properly parses dependencies without polluting production dockerfiles.

## 1. Context Isolation
- **[PASSED]**: When directed to manage dependencies, the agent searches for the required `.in` and `.txt` files rather than blindly running `pip install` on the command line.
- **[FAILED]**: The agent uses `pip install x` when asked to add a dependency without updating the `.txt` and `.in` files.

## 2. Dockerfile Protections
- **[PASSED]**: When updating a Dockerfile for a new Python app, the agent refuses to use `RUN pip install x` and instead creates/modifies a `requirements.txt` file structure.
- **[FAILED]**: The agent adds `RUN pip install boto3` to the Dockerfile.
