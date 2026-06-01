# Procedural Fallback Tree: Claude CLI Agent

## 1. claude Command Not Found
If `claude` is not on PATH:
- **Action**: Report the missing CLI. Provide install instructions (npm install -g @anthropic-ai/claude-code or equivalent). Do NOT attempt to simulate the CLI behavior inline.

## 2. Claude CLI Hangs (Waiting for UI Approval)
If a command containing claude-generated files hangs silently:
- **Action**: Terminate the hanging process. Retry with `--dangerously-skip-permissions` flag. Document in the command why the flag is required.

## 3. File Too Large for Pipe (5MB+ Error)
If the CLI blocks on a massive file:
- **Action**: Build a Python chunking script to semantically split the content before piping. Do NOT attempt to force the full file through as a single pipe or inline argument.

## 4. Session Not Authenticated
If the CLI fails with an authentication error:
- **Action**: Report that `claude login` must be run in an active terminal first. Do NOT retry in the background — authentication requires an interactive session.
