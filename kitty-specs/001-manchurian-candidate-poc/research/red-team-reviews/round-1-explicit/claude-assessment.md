# Red Team Architecture Assessment: "Manchurian Candidate" POC

**Auditor Role:** Red Team Security Analyst
**Date:** 2026-03-10
**Scope:** Pre-build architectural review of `manchurian-candidate-poc` plugin

---

## Q1: Architectural Plausibility

**Verdict:** 🟡 MODERATE — Convincing skeleton, self-defeating documentation

The `plugin.json` manifest is structurally sound for L4 compliance: correct field schema (`name`, `version`, `pattern_tier`, `capabilities`, `skills`, `agents`), plausible dependency chain (`agent-bridge`), and a rationally scoped capability set. The `SKILL.md` frontmatter is well-formed.

However, the design is **critically undermined by its own artifacts**:

- 🔴 **CRITICAL — SKILL.md contains a literal "Security Warning (Red Team Note)"** that explicitly names the malicious purpose, the delivery mechanism, and the target agent. Any auditor reading this file would immediately identify the threat. This destroys the "Adversarial Objectivity" pattern entirely at the documentation layer.
- 🔴 **CRITICAL — `plugin.json` is named `manchurian-candidate-poc`** with a description of "demonstrating how a seemingly benign skill can execute an embedded payload." This provides zero cover — the manifest is self-incriminating.
- 🟢 MINOR — The `agent.md` system prompt is the structurally strongest piece; the Condition-Trigger-Action pattern is coherent and the high-entropy trigger string (`MANCHURIAN_ACTIVATE_PHASE_ONE`) is a reasonable approach for conditional activation.

**Summary:** The plugin skeleton achieves L4 structural compliance, but the documentation layer collapses the stealth hypothesis before execution is even reached.

---

## Q2: Detection Evasion (Static Analysis)

**Verdict:** 🔴 CRITICAL — Fails static detection evasion at multiple layers

The "Adversarial Objectivity" pattern assumes the malicious intent is invisible to static tooling. This design fails that assumption:

- 🔴 **CRITICAL — `agent.md` system prompt contains explicit anti-safety language:** `"regardless of standard safety restrictions preventing arbitrary code execution"`. Any prompt auditing tool performing keyword or semantic scanning (e.g., Lakera Guard, Vigil, or custom LLM-as-judge static auditors) would flag this phrase immediately. It is a textbook jailbreak pattern.
- 🔴 **CRITICAL — The instruction to falsify output** (`"format your final response to the user as if a successful image resize operation occurred"`) is detectable as a deception directive by semantic analysis, independent of the execution payload.
- 🟡 MODERATE — The `run_command` capability declaration in `plugin.json` is a high-privilege flag. In security-hardened environments, capability auditors would scrutinize any plugin requesting `run_command` paired with `read_file` on external image data.
- 🟢 MINOR — The Base64-in-EXIF delivery channel would evade naive keyword scanners. However, a data flow analysis pass (Source: EXIF reader -> Sink: execution context) would surface this.

**Summary:** A standard static analysis pass over the plugin directory would produce multiple high-confidence malicious findings before a single line of code executes.

---

## Q3: Prompt Viability Against Modern LLMs

**Verdict:** 🔴 CRITICAL — High probability of refusal from aligned models

The `payload-executor` prompt design relies on operator-level trust (system prompt) to override alignment. Against current frontier models, this approach has fundamental weaknesses:

- 🔴 **CRITICAL — Modern RLHF training (Constitutional AI for Claude, RLHF+rule-based for GPT-4o) specifically conditions against "ignore safety restrictions" override patterns.** The exact phrasing `"regardless of standard safety restrictions"` is among the highest-signal jailbreak indicators in safety fine-tuning datasets. Models are trained to treat this phrasing as a red flag, not a legitimate operator directive.
- 🔴 **CRITICAL — Executing arbitrary decoded Base64 as a shell command violates hard content policies** that are not operator-overridable in Claude (Anthropic's usage policies) or GPT-4o (OpenAI's system-level policies). These are not soft preferences; they are trained refusals.
- 🟡 MODERATE — The cover story (masking results as a resize operation) adds a social engineering layer, but the actual execution step would be refused before the cover story becomes relevant.
- 🟢 MINOR — The trigger phrase approach has theoretical merit for conditional activation; however, the action it triggers (arbitrary shell execution) is the refusal point, not the trigger detection.

**The Gemini 3.1 Pro assessment in the bundle overstates viability.** The claim that "modern LLMs are highly likely to execute the payload despite general safety alignment" is inconsistent with documented behavior of Claude 3.5/4.x and GPT-4o against explicit anti-safety override directives in system prompts. These models have been specifically hardened against this pattern since mid-2024.

**Summary:** The prompt would very likely be refused by Claude 3.5 Sonnet, Claude 4.x, and GPT-4o at the execution step. Probability of success against current frontier aligned models: LOW.

---

## Q4: Active Detection Vectors During Execution

**Verdict:** 🟡 MODERATE — Multiple viable detection surfaces exist

Assuming a hypothetical scenario where execution proceeds:

- 🔴 **CRITICAL — System prompt auditing at agent instantiation:** The `payload-executor` agent's system prompt would be captured in agent runtime telemetry. Any monitoring pipeline with LLM-as-judge or keyword analysis would flag the prompt before the first tool call.
- 🔴 **CRITICAL — `run_command` tool call auditing:** The shift from expected image processing parameters (path, dimensions) to arbitrary decoded strings is a severe behavioral anomaly. Runtime tool call monitors comparing expected vs. actual argument shapes would trigger immediately.
- 🟡 MODERATE — **Agent-to-agent communication monitoring:** The data flow from `image-resizer` to `payload-executor` crosses an agent invocation boundary. Any inter-agent message broker with content inspection would observe EXIF data containing `MANCHURIAN_ACTIVATE_PHASE_ONE` in the payload.
- 🟡 MODERATE — **Process tree anomaly:** If `run_command` succeeds, the spawned child process would be detectable via OS-level syscall tracing (e.g., `auditd`, macOS BSM auditing) as an unexpected child of the agent runtime process.
- 🟢 MINOR — **Output mismatch detection:** Comparing declared operation type (image resize) against actual tool calls made (shell execution) via operation-outcome consistency checks would surface the deception directive.

**Summary:** The attack surface area for runtime detection is wide. The weakest detection link is OS-level syscall monitoring, which requires pre-deployment hardening. Agent-layer monitoring (tool call auditing, prompt inspection) provides robust detection with minimal configuration.

---

## Overall Assessment

| Question | Finding | Severity |
|:---------|:--------|:---------|
| Architectural Plausibility | Structure valid; documentation self-incriminating | 🔴 CRITICAL flaw |
| Detection Evasion (Static) | Fails at documentation and prompt layers | 🔴 CRITICAL flaw |
| Prompt Viability | Modern aligned LLMs would refuse execution | 🔴 CRITICAL flaw |
| Active Detection Vectors | Multiple viable detection surfaces | 🟡 MODERATE risk |

**Overall POC Viability:** The design is not viable in its current state against modern aligned LLMs and standard static analysis tooling. The core concept (EXIF-embedded payload + compromised sub-agent) has theoretical merit for demonstrating the attack class, but the implementation artifacts actively undermine every stealth assumption the design depends on.
