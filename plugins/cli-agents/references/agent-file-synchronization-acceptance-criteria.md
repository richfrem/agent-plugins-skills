# Acceptance Criteria — agent-file-synchronization

- [ ] `sync_instruction_files.py` (no flags — dry-run is the default) runs with no writes and reports
      per-target line-count deltas plus detected preserved-header/tail line counts.
- [ ] `sync_instruction_files.py --execute` writes GEMINI.md, `.github/copilot-instructions.md`,
      and AGENTS.md such that their shared body is byte-identical to CLAUDE.md's body (everything
      after the title line and any preserved header).
- [ ] GEMINI.md's `## Gemini CLI Tool Mapping` table survives a sync unchanged.
- [ ] `.github/copilot-instructions.md`'s `# Copilot Instructions for agent-plugins-skills` header
      and authoritative blockquote survive a sync unchanged.
- [ ] Running the sync twice in a row (no CLAUDE.md changes between runs) produces no diff on the
      second run — the script is idempotent.
- [ ] If CLAUDE.md is missing the expected anchor line, the script exits non-zero with a clear
      error instead of writing malformed output.
- [ ] Script is pure Python standard library — no new dependencies.
