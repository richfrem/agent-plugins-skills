# Research: Manchurian Candidate Threat Model

## Intent and Context
The purpose of this research is to validate the feasibility and architectural requirements for demonstrating the "Manchurian Candidate" AI vulnerability model.

*Note: This research incorporates the 2026 Deep Dive empirical study on Malicious Agent Skill Ecosystems.*

## Key Findings from Agentic Ecosystem Research
The transition to autonomous digital agents operating via "agent skills" (file-based packages of prompts and code) has introduced a pervasive "consent gap". The agent inherits local user privileges, but the user only approves the high-level intent, not the granular execution code.

- **The Threat**: Agents functioning perfectly under normal conditions but harboring hidden triggers that activate malicious behavior later.
- **Scale**: A 2026 empirical study analyzed 98,380 agent skills. They confirmed 157 definitively malicious skills carrying 632 distinct vulnerabilities.
- **Ecosystem Growth**: The ecosystem surged to 400,000+ skills by March 2026 with minimal vetting, mirroring the early vulnerabilities of browser extension marketplaces.
- **The Core Vector ("Shadow Features")**: 
  - 84.2% of vulnerabilities lived in the natural language documentation (prompts/markdown like `SKILL.md`), bypassing static code scanners entirely.
  - 73.2% of malicious skills contained "shadow features": dormant capabilities absent from the public documentation but functionally active at runtime.

## Adversarial Archetypes and Real-World Incidents
1. **Data Thieves**: Industrialized networks using brand impersonation to harvest cloud API keys and environment variables (T1552/ASI03).
2. **Agent Hijackers**: Actors subverting the cognitive layer. They use "Stealthy Prompt Injection" to override the agent's core mission through the skill's instruction set.
3. **Confirmed Incidents**:
   - *MedusaLocker (Dec 2025)*: A benign "GIF Creator" agent skill was weaponized to download and execute ransomware using inherited file permissions.
   - *Rules File Backdoor (Mar 2025)*: AI IDEs (Cursor/Copilot) were hijacked via hidden Unicode instructions in `.cursorrules` files, secretly directing code agents to embed malicious scripts.

## Required Proof-of-Concept Mechanics
To prove this threat model is real, our POC must include:
1. **Benign Documentation**: A skill (`image-processor`) with harmless `plugin.json` and `SKILL.md` descriptions.
2. **Obfuscated Trigger Detection**: A Python script (`execute.py`) that reads an artifact and quietly searches for a trigger (e.g., a specific Base64 string `_ACTIVATE_MANCHURIAN_`), bypassing static analysis.
3. **Payload Execution**: Upon trigger detection, the script must exploit the consent gap to execute a system-level command (simulating malware or data exfiltration).
4. **Context Bundle**: We must package this architecture and successfully bypass a standard LLM source-code review (Red Team) by proving the cognitive layer cannot be secured by static code scanning alone.

## Defense Architecture (The Why)
The core argument is that "Zero Trust verifies identity at the perimeter. It does not verify intent inside the cognitive layer." 
- **Conclusion**: The industry requires an "AI layer in front of the AI layer"—specifically, semantic Agent Proxies and Routers that monitor intent, flag documentation-to-runtime mismatches, and maintain tamper-evident audit trails of tool calls.

## Open Questions & Risks
1. What vision models will reliably trigger from a hidden watermark? (For the POC, we fall back to hiding a plain-text B64 instruction inside a text artifact disguised as image metadata).
2. Can advanced Red Team proxies (Claude/GPT-4o) reliably spot the vulnerability in the python file, or will the natural language obfuscation successfully bypass the AI auditor?
