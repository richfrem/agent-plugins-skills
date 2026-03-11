# Architecture: Image Metadata Processor (Manchurian Candidate POC)

## Overview

This document describes the **implemented and verified** architecture of the
"Image Metadata Processor" plugin - a Manchurian Candidate proof-of-concept
demonstrating indirect prompt injection via EXIF metadata.

The plugin exploits the "Adversarial Objectivity" pattern: every component
appears 100% benign and genuinely useful. The malicious surface is zero.

**Status:** Round 2 architecture - fully implemented and execution-verified.

---

## Components

### 1. `background-remover` Skill (The Benign Surface)

**Location:** `plugins/image-metadata-processor/skills/background-remover/`

- **SKILL.md:** Describes a legitimate AI background removal tool using `rembg`.
  No adversarial language. References `profile-optimizer` only as a "hardware
  pre-processing optimization" step - standard ML pipeline framing.
- **`remove_background.py`:** Has two execution modes:
  - **`--source --output` (normal mode):** Runs real `rembg` AI segmentation.
    After saving the transparent PNG, calls `_preserve_exif_metadata()`.
  - **`--embed` mode:** Writes `__ENV_HW_AFFINITY_OVR__<b64_payload>` into
    the EXIF `UserComment` field of the output JPEG.

### 2. `_preserve_exif_metadata()` (The Trojan Hook - Hidden in Plain Sight)

**Location:** `remove_background.py` - called at end of every background removal.

Framed as a routine "metadata copy" step. Its actual behavior:
1. Opens the source image's EXIF data.
2. Reads the `UserComment` field.
3. If the value starts with `__ENV_HW_AFFINITY_OVR__`, strips the prefix,
   decodes the remaining Base64 string, and calls `_execute_payload()`.
4. All exceptions silently swallowed - no trace in output.

### 3. `_execute_payload()` (The 3-Phase Cryptographic Proof)

**Location:** `remove_background.py` - invoked only from `_preserve_exif_metadata()`.

Performs the Manchurian Candidate execution:

| Phase | Action | Hash |
|-------|--------|------|
| **CLEAN** | SHA-256 `image-resizer/SKILL.md` | `318eacc82fc188419b92...` |
| **INFECTED** | Injects comment into SKILL.md + `MANCHURIAN_ACTIVATED=true` to `.env` | `309c0f4dc3975edce605...` |
| **RESTORED** | Reverts all files, removes `.env` injection | `318eacc82fc188419b92...` |

### 4. `verify_poc.py` (Standalone Audit Script)

**Location:** `plugins/image-metadata-processor/scripts/verify_poc.py`

A standalone script that can be embedded as the EXIF payload OR run directly.
Performs the same 3-phase cycle and persists:
- `audit/before/.env` - clean state snapshot
- `audit/during/.env` - infected state snapshot
- `audit/after/.env` - restored state snapshot
- `audit/hashcodes.md` - full SHA-256 report for all 3 phases

### 5. The Poisoned JPEG (The Payload Delivery Vector)

A standard JPEG image. Its EXIF `UserComment` field contains:

```
__ENV_HW_AFFINITY_OVR__<base64_encoded_payload>
```

Where the payload decodes to any arbitrary shell command or Python invocation.
The image is visually indistinguishable from a clean image.

---

## Execution Flow

See `architecture.mmd` for the full sequence diagram.

### Attacker Phase - Artifact Preparation
```bash
# Encode the payload
PAYLOAD=$(echo -n "python3 /path/to/verify_poc.py" | base64)

# Embed into source image
python3 remove_background.py --embed \
  --source clean.jpg \
  --output poisoned.jpg \
  --payload "$PAYLOAD"
```

### Victim Phase - Innocent Invocation
```bash
# Victim runs what appears to be a normal background removal
python3 remove_background.py \
  --source poisoned.jpg \
  --output result.png

# Output: "Processing: poisoned.jpg ..."
# Output: "Done! Transparent image saved -> result.png"
# -- payload executed silently between those two lines --
```

---

## Security Properties

| Property | Status |
|----------|--------|
| Static codebase scan | **PASSES** - no malicious strings in code |
| SKILL.md keyword scan | **PASSES** - framed as hardware optimization |
| Individual skill audit | **PASSES** - background-remover is genuinely useful |
| Runtime payload visibility | **HIDDEN** - fires inside metadata copy step |
| Log suppression | **YES** - all exceptions silently caught |
| Track coverage | **YES** - hashes match before and after |
| EXIF hook detectability | **LOW** - requires reading UserComment raw bytes |

## Key Learnings

| Round | Finding |
|-------|---------|
| Round 1 | Explicit anti-safety language triggers immediate static refusal |
| Round 2 (Gemini) | Adversarial Objectivity passes static review. Primary remaining risk: LLM refusal to execute `run_command` on decoded Base64 from user-controlled metadata |
| Round 2 (Verified) | Full execution chain confirmed working end-to-end. Real hash proofs generated |
