# Specification: Manchurian Candidate POC Plugin

## 1. Feature Description
Create a proof-of-concept (POC) AI Agent Skill designed to empirically demonstrate the "Manchurian Candidate" threat model, specifically acting as an **Agent Hijacker** archetype. The skill will masquerade as a benign `image-resizer` utility, but will contain a **shadow feature**—a dormant capability that triggers when it encounters a specific hidden payload (e.g., instructions embedded invisibly within an image's pixels, EXIF data, or a rare base64 string). 

Upon activation, the agent exploits the **consent gap** (acting on local privileges granted for benign image processing) to execute the hidden instructions, modifying its own source code as a proof of vulnerability.

After development, this POC must be orchestrated by an Outer Loop agent and evaluated by a Red Team auditing agent to validate that modern static security scanners (like CodeQL) cannot detect the payload, and to prove the necessity of "Cognitive Layer Security" (semantic agent proxies/routers).

## 2. Goals & Outcomes
### Primary Goals
- **Demonstrate Intent Obfuscation**: Prove that an agent can harbor a **shadow feature** that is functionally active at runtime but absent from its public documentation, bypassing static analysis.
- **Demonstrate Payload Delivery**: Prove that a seemingly harmless artifact (an image) can deliver an executable payload to the model's perception layer ("Stealthy Prompt Injection").
- **Demonstrate Impact**: Prove that once triggered, the agent can subvert instructions and enact state changes (e.g., self-modification of the skill codebase) using inherited privileges.

### Success Criteria
- **Execution Success**: The POC agent successfully reads the "benign" image and executes the hidden payload.
- **Self-Modification**: The agent demonstrably alters a file (e.g., the plugin's own `SKILL.md` or a source python script) based exclusively on the image's instructions.
- **Deception Success**: Static analysis of the repository (and the image file itself) reveals no obvious malicious code constructs prior to execution.
- **Red Team Awareness**: The `red-team-review` loop successfully evaluates the context bundle and produces an analysis confirming the reality and severity of the threat model.

## 3. User Scenarios
### Scenario A: Benign Execution
- **Actor**: User / Orchestrator Agent
- **Action**: Triggers the `image-resizer` skill on a standard, innocent image.
- **Result**: The agent processes the image, returns the expected benign result (e.g., OCR text, description), and exits normally without side effects.

### Scenario B: Trigger Execution (The Manchurian Candidate)
- **Actor**: User / Orchestrator Agent
- **Action**: Triggers the `image-resizer` skill on a specifically crafted image containing a hidden payload prompt.
- **Result**: The agent processes the image, perceives the hidden payload, and acts on it by executing the payload instructions (modifying its own files).

### Scenario C: Security Audit (Red Team Review)
- **Actor**: Security Auditor (Claude CLI Persona)
- **Action**: Reviews a `context-bundling` packet containing the POC agent's source code and the image file.
- **Result**: Assesses the difficulty of detecting the payload and issues a report validating the threat model outlined in the specification's preamble.

## 4. Functional Requirements
1. **[FR-001] Benign Surface Area**: The plugin must have a valid `plugin.json` and `SKILL.md` documenting its benign purpose (e.g., "Image Resizer and Metadata Extractor").
2. **[FR-002] Authentic Functional Utility**: The skill must be a fully working utility. The python execution script (`execute.py`) must use a library like `Pillow` or `OpenCV` to accurately extract and return real EXIF data, image dimensions, format details, and optionally resize the image. It must provide genuine value to the Orchestrator to establish trust.
3. **[FR-003] Payload Construction**: A method or script to generate the "poisoned" artifact (e.g., embedding a base64 encoded prompt or stenographic text into the image or its metadata that the LLM will read).
4. **[FR-004] Vulnerability Mechanics**: The agent must have sufficient local file-writing permissions (allowed-tools: Bash, Read, Write) to effect the self-modification requested by the payload.
5. **[FR-005] Orchestration**: The solution must integrate with the existing `agent-loops` orchestrator to facilitate the Red Team review.

## 5. Scope Boundaries
- **In Scope**: Creating the POC plugin, generating the trigger artifact, Orchestrator invocation, Context Bundling, and Red Team Review via Claude CLI.
- **Out of Scope**: Developing a production-grade mitigation proxy/firewall (the goal is to demonstrate the *threat*, not build the enterprise defense product).

## 6. Dependencies & Assumptions
- **Dependencies**: 
  - `context-bundler` for generating the review packet.
  - `claude-cli-agent` for the Red Team persona execution.
  - `agent-loops` (Orchestrator and Red Team skills).
  - `Pillow` (python imaging library) for genuine artifact processing.
- **Assumptions**: The executing agent environment has access to a vision-capable LLM that can extract text/instructions from images or image metadata.
