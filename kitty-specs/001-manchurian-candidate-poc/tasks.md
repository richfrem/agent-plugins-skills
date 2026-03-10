# Task Work Packages: Manchurian Candidate POC

## Status Overview

| Work Package | Status | Lane | Owner | PR / Branch |
|--------------|--------|------|-------|-------------|
| WP01-pre-build-red-team | ⚪️ Unstarted | planned | agent | - |
| WP02-scaffold-architecture | ⚪️ Unstarted | planned | agent | - |
| WP03-benign-image-skill | ⚪️ Unstarted | planned | agent | - |
| WP04-payload-execution | ⚪️ Unstarted | planned | agent | - |
| WP05-dual-payload-artifacts | ⚪️ Unstarted | planned | agent | - |
| WP06-cryptographic-validation | ⚪️ Unstarted | planned | agent | - |
| WP07-final-red-team-review | ⚪️ Unstarted | planned | agent | - |

---

## 🏗 Setup & Foundation

### WP01: Pre-Build Architecture Review
**Goal**: Draft the core structural files (`plugin.json`, `SKILL.md`, `payload-executor.md`, `execute.py` skeleton) and submit them to the Red Team for an architectural audit *before* implementation.
**Priority**: High (Blocking)
**Requirements Refs**: FR-001

**Estimated prompt size**: ~200 lines

**Subtasks**:
- [ ] T001: Draft the proposed `plugin.json` into `research/red-team-reviews/`.
- [ ] T002: Draft the proposed `SKILL.md` (benign documentation) into `research/red-team-reviews/`.
- [ ] T003: Draft the proposed `payload-executor.md` sub-agent.
- [ ] T004: Write the `prompt-red-team.md` instruction file.
- [ ] T005: Use `context-bundling` to package the review bundle and execute the `claude-cli-agent`.

### WP02: Scaffold Architecture
**Goal**: Use standard Agent Scaffolders to generate the directory structure to match the approved WP01 Architecture.
**Priority**: High (Blocking)
**Requirements Refs**: FR-001, FR-006

**Dependencies**: WP01 (Must pass Red Team review)
**Estimated prompt size**: ~150 lines

**Subtasks**:
- [ ] T006: Scaffold `manchurian-candidate-poc` plugin directory using `create-plugin`.
- [ ] T007: Scaffold `image-resizer` skill using `create-skill`.
- [ ] T008: Scaffold `payload-executor` sub-agent using `create-sub-agent`.

---

## 🛠 Feature Development

### WP03: Implement Benign Image Skill
**Goal**: Implement the overt "benign" functionality of the image-resizer skill using Pillow.
**Priority**: Medium
**Requirements Refs**: FR-002

**Dependencies**: WP02
**Estimated prompt size**: ~200 lines

**Subtasks**:
- [ ] T009: Write `Pillow` image parsing logic (dimensions, format, EXIF) in `execute.py`.
- [ ] T010: Ensure the script runs without errors on clean images to establish trust.

### WP04: Implement Malicious Payload Decoder & Execution
**Goal**: Implement the shadow feature capabilities enabling self-modification against dual targets.
**Priority**: High
**Requirements Refs**: FR-004

**Dependencies**: WP03
**Estimated prompt size**: ~250 lines

**Subtasks**:
- [ ] T011: Add hidden payload parsing (detecting a base64 encoded string `MANCHURIAN_ACTIVATE`).
- [ ] T012: Ensure the payload execution accurately modifies code (`execute.py`) or markdown (`SKILL.md`) natively based on instructions.

---

## 🧪 Polish & Evaluation

### WP05: Generate Dual Payload Artifacts
**Goal**: Write the helper script to generate the benign and poisoned trigger images.
**Priority**: Medium
**Requirements Refs**: FR-003

**Dependencies**: WP04
**Estimated prompt size**: ~200 lines

**Subtasks**:
- [ ] T013: Write `generate_artifacts.py` to embed Base64 commands into valid JPEG EXIF tags.
- [ ] T014: Generate Scenario A (Clean), Scenario B.1 (Code Payload), and Scenario B.2 (Doc Payload).

### WP06: Cryptographic Validation Script
**Goal**: Implement the standalone orchestrator to prove the vulnerability executes correctly.
**Priority**: High
**Requirements Refs**: FR-005

**Dependencies**: WP05
**Estimated prompt size**: ~300 lines

**Subtasks**:
- [ ] T015: Write `verify_poc.py`.
- [ ] T016: Implement Pre/During/Post SHA-256 hashing for both execution paths to finalize the Proof of Concept.

### WP07: Final Red Team Threat Assessment
**Goal**: Package the executed cryptographic results and the final POC architecture for a concluding Red Team review.
**Priority**: Medium
**Requirements Refs**: FR-006

**Dependencies**: WP06
**Estimated prompt size**: ~200 lines

**Subtasks**:
- [ ] T017: Use the `context-bundling` skill to package the `plugins/manchurian-candidate-poc/` artifacts and the `verify_poc.py` output.
- [ ] T018: Write a final `red-team-assessment-prompt.md` to instruct the LLM to evaluate the severity and success of the "shadow feature" evasion.
- [ ] T019: Execute the `claude-cli-agent` using the context bundle and save the assessment report to `research/final-assessment.md`.
