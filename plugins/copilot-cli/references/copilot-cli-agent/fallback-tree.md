# Procedural Fallback Tree: Copilot CLI Agent

## 1. copilot Command Not Found
If `copilot` is not on PATH:
- **Action**: Report the missing CLI. Provide install instructions (gh extension install github/gh-copilot or equivalent). Do NOT simulate Copilot behavior inline.

## 2. Smoke Test Fails
If 'copilot -p "Reply with exactly: COPILOT_CLI_OK"' does not return the expected string:
- **Action**: HALT. Do NOT dispatch the full analysis task. Report the smoke test failure. Ask user to verify CLI installation, PATH, and authentication before retrying.

## 3. Permission Flag Required by Task
If a task appears to require elevated permission flags (--allow-all-tools, --allow-all-paths):
- **Action**: Ask the user to confirm whether the elevated access is intentional. Document the reason in the command. Default is always to run without elevated permissions.

## 4. Session Not Authenticated
If the CLI returns an authentication error:
- **Action**: Report the failure and instruct the user to authenticate via the Copilot CLI session interactively. Do NOT retry in a background process.
