# Procedural Fallback Tree: create-sub-agent

## 1. Scaffold Script Execution Failure
If the underlying Python scaffold script crashes or throws an exception due to a missing template or filesystem error:
- **Action**: Halt the primary workflow. Read the explicit Python stack trace and correct the syntax error if obvious. Otherwise, output the exact stack trace to the user and prompt them to resolve the missing dependency.

## 2. Illegal Directory Write
If the destination path specifically requested by the user does not exist or lacks write permissions:
- **Action**: Stop execution. Do not attempt to guess an alternative path. Prompt the user with a list of available directories and ask them to choose or create the target path manually.

## 3. Template Rendering Engine Crash
If Jinja2 or the internal string templater fails to render constraints due to malformed input during generation:
- **Action**: Do not output partially-rendered code logic. Fallback to extracting the literal variables given by the user, provide the base template inline in the chat, and instruct the user to insert the values manually.

## 4. Name Collision
If the user requests a generation that shares a name with an already existing skill or plugin in the exact same path:
- **Action**: Do NOT overwrite the existing directory without an explicit dual-confirmation loop. Ask the user: "Warning: Directory already exists. Do you want to recursively overwrite it? (yes/no)".
