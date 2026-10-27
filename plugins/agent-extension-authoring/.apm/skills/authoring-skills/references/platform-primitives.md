# Platform Primitives & Modern Capability Architecture

## Universal Capability Primitives

Across modern AI developer tooling (Claude Code, Antigravity, Cursor, Codex, Gemini CLI, MAF):

1. **Skills ARE Tools & Slash Commands**:
   - Discovery and explicit invocation syntax depend on the host. Verify the installed host's skill capabilities rather than assuming `/name` or `@name` works everywhere.
   - Names and descriptions guide discovery. evals.json measures routing; it is not a runtime discovery registry.

2. **Default to Skills**:
   - Prefer skills for reusable procedural capabilities, including instructions without executable code. Follow [skills-vs-agents-decision-framework.md](skills-vs-agents-decision-framework.md) for the 5-question decision tree.
   - Use `authoring-subagents` only when context isolation, a sandboxed tool set, or an adversarial persona is required; multi-turn conversational wizards, solution architecture interviews, and interactive testing belong in skills in the main thread.
   - Use `create-stateful-skill` only when cross-session state or continuous counters are required.

## Self-Contained APM Architecture

- All helper scripts, references, and assets live directly inside the owning skill: `plugins/<plugin>/.apm/skills/<skill>/scripts/`.
- Zero symlinks and zero copy manifests (`symlinks.json` retired). All resources are real, Git-tracked physical files.
- Modal dispatch architecture: `SKILL.md` is under 100 lines and routes to modular mode documents under `references/modes/<mode>.md`.
