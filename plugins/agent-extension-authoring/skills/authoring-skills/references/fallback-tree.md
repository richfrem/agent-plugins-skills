# Fallback Tree: authoring-skills

Merged verbatim from the retired skills; one section per mode.

## Contents

- [Mode: create-skill](#mode-create-skill)
- [1. Scaffold Script Execution Failure](#1-scaffold-script-execution-failure)
- [2. Illegal Directory Write](#2-illegal-directory-write)
- [3. Template Rendering Engine Crash](#3-template-rendering-engine-crash)
- [4. Name Collision](#4-name-collision)
- [Mode: create-stateful-skill](#mode-create-stateful-skill)
- [1. Scaffold Script Execution Failure](#1-scaffold-script-execution-failure)
- [2. Illegal Directory Write](#2-illegal-directory-write)
- [3. Template Rendering Engine Crash](#3-template-rendering-engine-crash)
- [4. Name Collision](#4-name-collision)
- [Mode: create-docker-skill](#mode-create-docker-skill)
- [1. Scaffold Script Execution Failure](#1-scaffold-script-execution-failure)
- [2. Illegal Directory Write](#2-illegal-directory-write)
- [3. Template Rendering Engine Crash](#3-template-rendering-engine-crash)
- [4. Name Collision](#4-name-collision)
- [Mode: create-azure-agent](#mode-create-azure-agent)
- [1. Scaffold Script Execution Failure](#1-scaffold-script-execution-failure)
- [2. Illegal Directory Write](#2-illegal-directory-write)
- [3. Template Rendering Engine Crash](#3-template-rendering-engine-crash)
- [4. Name Collision](#4-name-collision)
- [Mode: create-mcp-integration](#mode-create-mcp-integration)
- [1. Scaffold Script Execution Failure](#1-scaffold-script-execution-failure)
- [2. Illegal Directory Write](#2-illegal-directory-write)
- [3. Template Rendering Engine Crash](#3-template-rendering-engine-crash)
- [4. Name Collision](#4-name-collision)
- [Mode: ecosystem-standards](#mode-ecosystem-standards)
- [1. Ambiguous Component Boundary](#1-ambiguous-component-boundary)
- [2. Legacy Pattern Matches](#2-legacy-pattern-matches)
- [3. Tool Interaction Blindspots](#3-tool-interaction-blindspots)
- [4. Unresolvable Standard Conflict](#4-unresolvable-standard-conflict)
- [Mode: ecosystem-authoritative-sources](#mode-ecosystem-authoritative-sources)
- [1. Missing Reference Target](#1-missing-reference-target)
- [2. Conflicting Specifications](#2-conflicting-specifications)
- [3. Spec Interpretation Deadlock](#3-spec-interpretation-deadlock)
- [4. Unsupported Ecosystem Query](#4-unsupported-ecosystem-query)

## Mode: create-skill

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

## Mode: create-stateful-skill

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

## Mode: create-docker-skill

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

## Mode: create-azure-agent

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

## Mode: create-mcp-integration

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

## Mode: ecosystem-standards

## 1. Ambiguous Component Boundary
If the target directory appears to contain a mixture of Agent Skills, Workflows, and arbitrary scripts without clear separation:
- **Action**: Do not attempt a unified audit. Isolate the target. Ask the user explicitly: "Are we auditing this as a Plugin, an individual Skill, or a naked Workflow?" Apply only the specific checklist for that isolation primitive.

## 2. Legacy Pattern Matches
If an old plugin perfectly follows V1 standards but fails V2 L5 constraints:
- **Action**: Do not auto-reject the plugin as "broken" unless it violates P0 security rules. Mark it as "V1 Legacy Compliant", list the specific upgrade deltas needed for V2 L5, and assign a lower overall maturity score.

## 3. Tool Interaction Blindspots
If auditing a skill that requires complex Multi-CLI interactions or nested sub-agent environments that you cannot dry-run:
- **Action**: Audit the static structural requirements (frontmatter, structure, diagrams). Explicitly flag the interactive elements as "Untested/Requires Red Team Sandbox" to maintain Source Transparency.

## 4. Unresolvable Standard Conflict
If a plugin violates an ecosystem standard to solve a novel edge-case (e.g., massive inline prompt chunking for specific token-dense tasks):
- **Action**: Flag the violation but label it an "Intentional Deviation". Record a recommendation in the analysis report and route systemic spec changes through `managing-github-issues (propose-refactor mode)` if the edge case proves valuable.

## Mode: ecosystem-authoritative-sources

## 1. Missing Reference Target
If the table of contents links to a `reference/` file that does not physically exist in the filesystem:
- **Action**: Do not attempt to guess the specification contents. Explicitly state to the user: "The authoritative source file for [Topic] is missing." Fall back to the main repository `README.md` to see if the knowledge was moved globally.

## 2. Conflicting Specifications
If asked a question where the specs in this plugin contradict the global `constitution.md` (e.g., execution rules):
- **Action**: The global `constitution.md` ALWAYS wins. Surface the contradiction to the user and explicitly prioritize the constitutional mandate over the plugin's local reference docs.

## 3. Spec Interpretation Deadlock
If the user repeatedly argues that a generated artifact aligns with the specs, but the agent believes it fails:
- **Action**: Defer to the `ecosystem-standards` skill. Do not debate the user. Run a formal audit against the specific component to get an objective pass/fail checklist.

## 4. Unsupported Ecosystem Query
If asked about a framework pattern (e.g., "CrewAI") not covered by the authoritative sources:
- **Action**: Explicitly state that the framework is not part of the local Open Standard ecosystem. Do not try to map proprietary Claude Plugin constraints onto unsupported engines.
