# Instruction File Optimization Heuristics

## Target Budget
- **Budget**: <= 80 lines / <= ~800 tokens per file (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`).

## What to Keep (Direct Behavioral Impact)
- Project purpose — 2-3 sentences max
- Key development commands (build, test, install) — one-liners only
- Universal coding rules / ADRs — keep as bullet list
- Skill/agent standards — if they gate mistakes
- Scratch/temp directory rules

## What to Remove (Descriptive / Aspirational / Noise)
- Stats that go stale (counts of skills/plugins)
- Duplicate install command variants — keep canonical one only
- Overly detailed architecture diagrams
- Descriptions of internal subsystem mechanics
- Script tables — reference directory paths instead
- Content where removing it would not cause an agent mistake

## Mirror Sync Protocol
When syncing `CLAUDE.md` to `GEMINI.md` and `.github/copilot-instructions.md`, preserve tool mappings in `GEMINI.md` and Copilot header blocks.
