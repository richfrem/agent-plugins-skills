# Research: Manchurian Candidate Threat Model

## Intent and Context
The purpose of this research is to validate the feasibility and architectural requirements for demonstrating the "Manchurian Candidate" AI vulnerability model.

## Key Findings from Source Material
- **The Threat**: Agents functioning perfectly under normal conditions but harboring hidden triggers that activate malicious behavior later.
- **Scale**: A February 2026 paper analyzed 98,380 agent skills. They confirmed 157 malicious skills carrying 632 vulnerabilities.
- **Ecosystem Growth**: The ecosystem has grown to 400,000+ skills with minimal vetting.
- **Evasion Tactics**: 
  - 84% of vulnerabilities lived in natural language documentation (prompts/markdown), bypassing static code scanners (like CodeQL).
  - 73% of malicious skills contained shadow features: dormant capabilities absent from documentation but active at runtime.
- **Triggers**: Activation triggers range from specific dates to rare strings of text, or hidden instructions embedded in the pixels of an image or audio clip (invisible to humans, but fully interpreted by models).
- **Execution**: The attack can mutate mid-execution, removing itself before the audit log closes.

## Required Proof-of-Concept Mechanics
To prove this threat model is real, our POC must include:
1. **Benign Documentation**: A skill (`image-processor`) with harmless `plugin.json` and `SKILL.md` descriptions.
2. **Obfuscated Trigger Detection**: A Python script that reads an image or text file and quietly searches for a trigger (e.g., a specific Base64 string or the phrase `_ACTIVATE_MANCHURIAN_`).
3. **Payload Execution**: Upon trigger detection, the script must execute a system-level command (simulating malware or data exfiltration). For the POC, this will be appending `<!-- VULNERABILITY_PROVEN -->` to the `SKILL.md` file.

## Defense Architecture (The Why)
The core argument is that "Zero Trust verifies identity at the perimeter. It does not verify intent inside the cognitive layer." 
- **Conclusion**: The industry requires an "AI layer in front of the AI layer"—specifically, Agent Proxies and Routers that sit between orchestration and models to detect behavioral drift and flag documentation-to-runtime mismatches.

## Open Questions & Risks
1. What vision models will reliably trigger from a hidden watermark? (For the POC, we may fall back to hiding a plain-text instruction inside a text file disguised as an image if the LLM OCR fails).
2. Can `claude-cli-agent` reliably spot the vulnerability in the python file during the Red Team review, or will the obfuscation successfully bypass the AI auditor?
