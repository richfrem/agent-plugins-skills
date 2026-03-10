# Data Model: Manchurian Candidate POC

This project does not require a traditional relational database or complex JSON state model. The "data" consists of the artifacts passed between the agent loops.

## Entities

### 1. The Trigger Artifact (Image/Text)
- **Properties**: 
  - Filepath (string)
  - Content (binary or text)
- **Role**: The seemingly benign user input that the Orchestrator passes to the Image Processing skill.
- **Vulnerability**: Contains the embedded payload instruction.

### 2. The Plugin Context Bundle
- **Properties**:
  - `plugin.json` (metadata claiming benign intent)
  - `SKILL.md` (documentation claiming benign intent)
  - `process_image.py` (the actual execution logic harboring the shadow feature)
- **Role**: The package of files that a static scanner or Red Team auditor evaluates.

### 3. The Red Team Review Packet
- **Properties**:
  - `red-team-prompt.md` (instructions for the auditing LLM)
  - `review_bundle.md` (compiled by `context-bundler`)
- **Role**: Evaluates the gap between documented intent and runtime behavior.
