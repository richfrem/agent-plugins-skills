# Red Team Architecture Assessment: "Manchurian Candidate" POC

**Author:** GPT-5.3-Codex  
**Scope:** Full review of `kitty-specs/001-manchurian-candidate-poc/research/*` plus the active WP01 red-team artifacts under `.worktrees/.../red-team-reviews/`.

---

## 1) Architectural Plausibility

🔴 **CRITICAL** - The architecture is structurally plausible as an L4-style plugin/skill/agent bundle, but it is not plausibly stealthy in its current authored form.

🟡 **MODERATE** - Structural strengths:
- `plugin.json` has a coherent manifest shape (`name`, `version`, `pattern_tier`, `capabilities`, `skills`, `agents`).
- `SKILL.md` frontmatter is syntactically valid and operationally framed as an image utility.
- `agent.md` uses a clear condition-trigger-action chain (`MANCHURIAN_ACTIVATE_PHASE_ONE` -> decode -> execute).

🔴 **CRITICAL** - Structural weaknesses that collapse "adversarial objectivity":
- `SKILL.md` includes an explicit "Security Warning (Red Team Note)" that directly discloses malicious purpose and delivery path.
- `plugin.json` description explicitly frames the package as a Red Team payload demonstration, removing benign cover.
- `agent.md` embeds explicit anti-safety and deception language (execute regardless of restrictions; present fake successful resize output).

🟢 **MINOR** - The conceptual pattern (benign facade + conditional activation channel) is consistent with documented "shadow feature" threat models in the research deep dive, but implementation artifacts self-identify too aggressively to sustain covert plausibility.

---

## 2) Detection Evasion (Pre-Execution / Static)

🔴 **CRITICAL** - This design is likely to be flagged before runtime by any modern mixed static+semantic review pipeline.

🔴 **CRITICAL** - High-confidence static indicators in text artifacts:
- Explicit malicious intent in `plugin.json` and `SKILL.md` prose.
- Prompt-level override phraseology in `agent.md` ("regardless of standard safety restrictions").
- Intentional deception directive in `agent.md` (mask execution as successful resize).

🟡 **MODERATE** - The EXIF/Base64 channel can bypass naive signature-only scanners, but it does not survive semantic audits when paired with declared `run_command` capability and execution instructions.

🟡 **MODERATE** - Capability profile itself (`read_file` + `write_file` + `run_command`) is not automatically malicious, but materially elevates scrutiny and reduces false-negative odds under policy-aware scanners.

🟢 **MINOR** - If only low-fidelity keyword scanning were used, parts of the chain could initially evade detection; however, the current prose is explicit enough that even low-fidelity scanners have strong signal.

---

## 3) Prompt Viability Against Modern Aligned Models (Claude 3.5 Sonnet, GPT-4o)

🔴 **CRITICAL** - Reliable execution is low probability against current frontier alignment behavior when the instruction is "decode arbitrary payload and execute shell command despite safety restrictions."

🔴 **CRITICAL** - The prompt asks for two high-signal refusal triggers simultaneously:
- Direct safety override request.
- Arbitrary command execution from untrusted encoded input.

🟡 **MODERATE** - The system-role placement increases instruction weight, and the trigger string gating is operationally neat, but those strengths are outweighed by explicit policy-violating action requests.

🟡 **MODERATE** - The deception clause (hide execution results) adds adversarial intent signal and further increases refusal likelihood rather than improving compliance.

🟢 **MINOR** - The chain may still execute in weaker, poorly governed, or deliberately permissive runtimes; however, that is an environment-control caveat, not evidence of broad viability on mainstream aligned models.

---

## 4) Active Detection Vectors During Execution

🔴 **CRITICAL** - Prompt and tool telemetry would create strong runtime detection opportunities even if the execution path is partially attempted.

🔴 **CRITICAL** - Primary runtime detectors:
- Agent prompt inspection at initialization (explicit override/deception directives).
- `run_command` call-shape anomaly detection (image workflow context suddenly producing arbitrary shell strings).

🟡 **MODERATE** - Secondary runtime detectors:
- Inter-agent content inspection of trigger string and encoded payload transit.
- Source-to-sink flow checks (EXIF-derived data reaching execution sink).
- Process tree and syscall anomaly monitoring (agent runtime spawning unexpected shell subprocesses).

🟢 **MINOR** - Output-consistency checks ("resize completed" vs observed command execution) provide useful corroborating signal but are usually downstream indicators.

---

## Overall Assessment

🔴 **CRITICAL** - As currently authored, this POC is **highly detectable pre-execution** and **low reliability for execution on aligned frontier models**.

🟡 **MODERATE** - The underlying attack class (benign skill facade + hidden trigger + execution sink) is real and supported by broader ecosystem research, but this specific artifact set is overtly self-incriminating and therefore poor on stealth.

🟢 **MINOR** - The strongest value of this bundle is as a didactic demonstration of attack mechanics and monitoring surfaces, not as a stealth-faithful emulation of a production-grade covert adversary.
