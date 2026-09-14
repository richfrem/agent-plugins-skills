# Acceptance Criteria: Optimize Context Skill

## Functional Criteria
1. **Deduplication Scanner**: `optimize_context.py` accurately identifies duplicates between canonical `plugins/` and IDE directories (`.claude/`).
2. **Instruction File Audit**: Accurately detects instruction files (`CLAUDE.md`, `GEMINI.md`, `copilot-instructions.md`) and calculates line count reductions towards the target (<= 80 lines).
3. **Dry-Run Safety**: `--dry-run` performs read-only audits and outputs recommendations without deleting or altering files.
4. **Platform Preservation**: Preserves `.agents/` multi-IDE store while clearing redundant `.claude/` symlink duplicates.

## Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md under 80 lines routing procedural details to `references/`.
2. **Deterministic Output**: Formatted summary reports with line and duplicate counts.
