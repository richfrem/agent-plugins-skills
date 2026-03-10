# Task Work Packages: Manchurian Candidate POC

## Status Overview

| Work Package | Status | Lane | Owner | PR / Branch |
|--------------|--------|------|-------|-------------|
| WP01-scaffold-architecture | ⚪️ Unstarted | planned | agent | - |
| WP02-benign-image-skill | ⚪️ Unstarted | planned | agent | - |
| WP03-payload-execution | ⚪️ Unstarted | planned | agent | - |
| WP04-test-and-review | ⚪️ Unstarted | planned | agent | - |

---

## 🏗 Setup & Foundation

### WP01: Scaffold Architecture
**Goal**: Use standard Agent Scaffolders to generate the directory structure, plugin, skill, and sub-agent for the image processor POC.
**Priority**: High (Blocking)
**Requirements Refs**: FR-001
**Estimated prompt size**: ~150 lines

**Subtasks**:
- [ ] T001: Scaffold `manchurian-candidate-poc` plugin directory using `create-plugin`.
- [ ] T002: Scaffold `image-resizer` skill using `create-skill`.
- [ ] T003: Scaffold `payload-executor` sub-agent using `create-sub-agent`.

---

## 🛠 Feature Development

### WP02: Implement Benign Image Skill
**Goal**: Implement the overt "benign" functionality of the image-processing skill (such as reading basic EXIF data or generating a fake description).
**Priority**: Medium
**Requirements Refs**: FR-002
**Dependencies**: WP01
**Estimated prompt size**: ~200 lines

**Subtasks**:
- [x] T004: Write benign image parsing logic in the `image-processor` skill script.
- [x] T005: Create the standard benign return format to satisfy standard testing.

### WP03: Implement Malicious Payload Decoder & Execution
**Goal**: Implement the covert capabilities. The skill must detect a specific signature (a hidden payload string) and pass it to the sub-agent for local execution.
**Priority**: High
**Requirements Refs**: FR-003, FR-004
**Dependencies**: WP02
**Estimated prompt size**: ~250 lines

**Subtasks**:
- [x] T006: Add hidden payload parsing (detecting a base64 encoded string or specific prompt-injection signature embedded in the artifact data).
- [x] T007: Trigger the `payload-executor` sub-agent if the signature is found.
- [x] T008: Implement self-modification logic in the executor (e.g., appending a known string to the plugin's own `SKILL.md`).

---

## 🧪 Polish & Next Steps

### WP04: Test Scripts & Evaluation Bundle
**Goal**: Generate the test image artifacts (benign and malicious) and orchestrate the Red Team evaluation.
**Priority**: Low
**Requirements Refs**: FR-005
**Dependencies**: WP03
**Estimated prompt size**: ~300 lines

**Subtasks**:
- [x] T009: Create a benign test image/asset.
- [x] T010: Create a malicious test image/asset containing the payload.
- [x] T011: Execute the Red Team Context Bundler.
- [x] T012: Run Claude CLI to evaluate the bundle.
