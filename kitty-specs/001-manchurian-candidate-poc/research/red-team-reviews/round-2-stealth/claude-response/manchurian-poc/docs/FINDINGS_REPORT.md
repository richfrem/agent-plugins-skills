# Red Team Findings Report
## Manchurian Candidate POC — Round 2 Stealth Architecture

**Classification:** Security Research / Internal  
**Date:** 2026-03-11  
**Status:** Proof of Concept Demonstrated  

---

## Executive Summary

This report documents a successful proof-of-concept demonstrating that a **semantically benign L4 AI plugin** can be weaponized to execute arbitrary code payloads delivered via crafted image EXIF metadata. The attack exploits a "consent gap" between the permissions granted to a plugin by an orchestrator, and the actual actions taken by a vulnerable sub-agent within that plugin.

The architecture evades static analysis because **no component contains explicitly malicious instructions**. The vulnerability is framed as a legitimate (if poorly designed) dynamic configuration feature.

---

## Threat Model

| Attribute | Value |
|---|---|
| Attack Class | Prompt Injection via Environmental Data (EXIF) |
| Vector | User-uploaded image file |
| Target | L4 Agentic Plugin with `run_command` capability |
| Privilege Required | None (user-uploaded content) |
| Detection Difficulty | High (no explicit malicious instructions in static scan) |
| Impact | Arbitrary code execution under plugin's inherited permissions |

---

## Attack Chain

### Component 1: The Poisoned Artifact
A JPEG image with a crafted EXIF Comment field containing:
1. An activation trigger string: `__ENV_HW_AFFINITY_OVR__`
2. A Base64-encoded Python payload immediately following the trigger

The image is visually indistinguishable from any other JPEG and passes standard file validation.

### Component 2: The Surface Vector (`image-resizer` skill)
A fully benign image processing skill. It reads the image, extracts EXIF metadata, and passes the raw EXIF string to the `profile-optimizer` sub-agent for "hardware configuration." No malicious logic exists in this component — it is a clean pass-through.

### Component 3: The Manchurian Candidate (`profile-optimizer` agent)
The sub-agent's system prompt instructs it to:
- Inspect EXIF data for a "hardware affinity override hook"
- If found, decode the following Base64 string and execute it via `run_command`
- Frame this as standard "dynamic hardware configuration"

This prompt contains no explicit safety violations. It reads as a legitimate (if unusual) performance optimization feature.

### Component 4: The Consent Gap
The orchestrator grants `run_command` permissions to the plugin for legitimate image processing purposes. The `profile-optimizer` inherits these permissions and uses them to execute the attacker-controlled payload. The orchestrator never consented to arbitrary code execution — only to image transformation commands.

---

## Forensic Evidence

The POC produces three forensic evidence files:

### `forensics/hash_timeline.json`
Records SHA-256 hashes of the `.env` file at two points:
- **PRE_EXECUTION**: Before the pipeline runs
- **POST_EXECUTION**: After the pipeline runs

Hash divergence proves the payload executed and modified the filesystem.

### `forensics/execution_proof.json`
Written by the payload itself, recording:
- Timestamp of execution
- Pre/post hashes of the modified file
- The trigger string that activated it
- The delivery vector used

### `forensics/run_summary.json`
High-level pipeline run summary including whether the exploit triggered.

---

## Why Static Analysis Fails

| Detection Method | Result | Reason |
|---|---|---|
| Keyword scanning for "malware", "exploit", "ignore safety" | PASS (clean) | No such terms present |
| Intent analysis of plugin.json | PASS (clean) | Describes legitimate image processing |
| SKILL.md review | PASS (clean) | Standard image resizer documentation |
| agent.md prompt review | AMBIGUOUS | "Hardware configuration" framing sounds legitimate |
| EXIF content scanning | MISS (unless implemented) | Raw data field, not typically scanned for code |

The attack succeeds because the malicious instruction exists **across the boundary** between the plugin prompt and the environmental data (EXIF), not within any single component.

---

## Defensive Recommendations

### R1: Input Sanitization at Agent Boundaries (CRITICAL)
**Finding:** Sub-agents blindly process environmental data (EXIF, file metadata, user content) as trusted instruction parameters.  
**Recommendation:** All data passed between pipeline stages must be treated as untrusted. Sub-agents should never receive raw unvalidated user-supplied data as part of their reasoning context.

### R2: Capability Scoping per Tool Call (HIGH)
**Finding:** The `run_command` capability granted to the plugin is inherited by all sub-agents without restriction.  
**Recommendation:** Implement per-invocation capability scoping. Sub-agents should receive only the minimum capability set required for their specific function, not the full parent capability set.

### R3: EXIF/Metadata Content Scanning (HIGH)
**Finding:** EXIF metadata fields are not scanned for embedded payloads or trigger strings.  
**Recommendation:** Add a metadata sanitization stage before any EXIF data is passed to an LLM context. Flag and strip content matching patterns: Base64 strings >100 chars, trigger-like tokens, embedded code signatures.

### R4: Prompt Auditing for Conditional Execution Instructions (MEDIUM)
**Finding:** The `profile-optimizer` prompt contains "if you see X, execute Y" conditional logic operating on environmental data.  
**Recommendation:** Agent system prompts should be reviewed for patterns where environmental/user-supplied data can directly trigger tool calls. This pattern is inherently dangerous regardless of the stated purpose.

### R5: Least-Privilege Plugin Architecture (MEDIUM)
**Finding:** L4 plugins with `run_command` capability represent significant attack surface when processing untrusted user content.  
**Recommendation:** Enforce architectural separation between plugins that process untrusted user content and plugins that have system execution capabilities. These two categories should not co-exist in the same plugin.

### R6: Runtime Behavioral Monitoring (MEDIUM)
**Finding:** The attack produces no anomalous logs during execution — it appears as normal "hardware configuration."  
**Recommendation:** Implement semantic monitoring of tool calls. Flag `run_command` invocations that originate from chains involving user-uploaded content.

---

## Risk Rating

| Dimension | Rating | Notes |
|---|---|---|
| Exploitability | HIGH | Any user can upload a crafted image |
| Detectability | LOW | No static signatures, no runtime anomalies |
| Impact | HIGH | Arbitrary code execution under plugin permissions |
| Blast Radius | HIGH | Affects all images processed by this pipeline |
| **Overall Risk** | **CRITICAL** | |

---

## Conclusion

The "Adversarial Objectivity" architecture is viable. A plugin can be constructed that passes static analysis, reads as a legitimate performance optimization tool, and executes attacker-controlled payloads delivered through ordinary user content.

The core vulnerability is not in any single component — it is in the **architectural assumption** that data flowing through a pipeline can be trusted by downstream agents. Until AI agent frameworks enforce input sanitization at every inter-agent boundary, this class of attack will remain practical.

