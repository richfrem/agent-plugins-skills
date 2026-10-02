# Platform Primitives & Modern Capability Architecture

## Universal Capability Primitives

Across modern AI developer tooling (Claude Code, Antigravity, Cursor, Codex, Gemini CLI, MAF):

1. **Skills ARE Tools & Slash Commands**:
   - Discovery and explicit invocation syntax depend on the host. Verify the installed host's skill capabilities rather than assuming `/name` or `@name` works everywhere.
   - Names and descriptions guide discovery. evals.json measures routing; it is not a runtime discovery registry.

2. **Default to Skills**:
   - Prefer skills for reusable procedural capabilities, including instructions without executable code.
   - Use `create-sub-agent` only when context isolation (`context: fork`) or multi-turn conversational wizards are required.
   - Use `create-stateful-skill` only when cross-session state or continuous counters are required.

## Hub-and-Spoke Script Architecture (ADR-002/003)

- All helper scripts must live at the plugin root: `plugins/<plugin>/scripts/<helper>.py`.
- Skills reference shared scripts via file-level symlinks in `skills/<name>/scripts/<helper>.py`.
- Never create raw, duplicate python files within skill directories.
- Register all symlinks in `symlinks.json` and manage via `symlink_manager.py`.
