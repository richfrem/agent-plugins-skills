---
concept: acceptance-criteria-dual-loop
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/dual-loop/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.030636+00:00
cluster: packet
content_hash: 13669b32743ad5bc
---

# Acceptance Criteria: Dual-Loop

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Dual-Loop

## 1. Strategy Packet Fidelity
- [ ] Outer Loop ALWAYS generates an explicit, written markdown Strategy Packet containing constraints, file paths, and the "NO GIT" mandate before delegating.
- [ ] The Inner Loop is only fed the packet and necessary files, drastically isolating its context window.

## 2. Anti-Simulation Checks
- [ ] Outer Loop NEVER marks a task "Done" without manually checking the file deltas and mechanically running lint/test commands.
- [ ] "Assume it works" behavior results in an immediate audit failure.

## 3. Structured Correction
- [ ] Failed verifications are NEVER manually patched by the Outer Loop without feedback, unless tagged as `MINOR` (naming/style).
- [ ] Critical and Moderate failures are routed back to the Inner Loop via structured Markdown Correction Packets citing the exact failure logs.


## See Also

- [[acceptance-criteria-learning-loop]]
- [[acceptance-criteria-learning-loop]]
- [[acceptance-criteria-learning-loop]]
- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/dual-loop/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.030636+00:00
