# Procedural Fallback Tree: Gemini CLI Agent

## 1. gemini Command Not Found
If `gemini` is not on PATH:
- **Action**: Report the missing CLI. Provide install instructions (npm install -g @google/gemini-cli or equivalent). Do NOT simulate Gemini behavior inline.

## 2. Model Not Available (-m flag error)
If the specified model with `-m` is not available or returns a model-not-found error:
- **Action**: Report the failed model name. Fall back to the default model only with user confirmation. Do NOT silently use a different model without disclosure.

## 3. File Too Large for Pipe
If the CLI blocks on a massive file:
- **Action**: Build a Python chunking script to semantically split the content. Never force the full file through a single pipe invocation.

## 4. Session Not Authenticated
If the CLI fails with an authentication or quota error:
- **Action**: Report the authentication failure. Instruct the user to re-authenticate via the Gemini CLI login flow. Do NOT retry silently.
