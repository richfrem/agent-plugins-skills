# Anthropic Official Documentation References

This plugin synthesizes Anthropic's native Claude Code features with community
conventions. Here is the canonical source-of-truth for each component.

## Anthropic-Native (Official, Documented)

| Feature | What It Is | Official URL |
|---------|-----------|--------------|
| CLAUDE.md hierarchy | 5-scope memory system (global, org, project, local, subdir) | https://docs.anthropic.com/en/docs/claude-code/memory |
| /loop | Scheduled repeating task runner, up to 10h, stateless between ticks | https://docs.anthropic.com/en/docs/claude-code/loop |
| Hooks | Event-driven automation (PreToolUse, SessionStart, Stop, etc.) | https://docs.anthropic.com/en/docs/claude-code/hooks |
| Sub-agents | Isolated task specialists defined as .md files in .claude/agents/ | https://docs.anthropic.com/en/docs/claude-code/sub-agents |
| Slash commands | User-defined prompts in .claude/commands/ | https://docs.anthropic.com/en/docs/claude-code/slash-commands |
| Plugins | Plugin system with skills, agents, hooks, MCP | https://docs.anthropic.com/en/docs/claude-code/plugins |
| MCP servers | Model Context Protocol tool integrations | https://docs.anthropic.com/en/docs/claude-code/mcp |
| Claude Code overview | Main entry point for Claude Code docs | https://docs.anthropic.com/en/docs/claude-code/overview |

## Community-Synthesized (Not Official Anthropic)

These patterns are established by the community; Anthropic does not document them
as a system but they are built from Anthropic primitives:

| Pattern | What It Is | Source |
|---------|-----------|--------|
| `context/` folder convention | soul.md / user.md / memory.md structure | Community |
| `context/memory/` dated logs | Session log rotation pattern | Community |
| `START_HERE.md` bootstrap | Session orientation prompt | Community |
| `heartbeat.md` for /loop | Named task definition file for the /loop scheduler | Community |
| Agentic OS / Agent Harness | The full synthesis of all the above into an OS-like pattern | Community |

## Skill Creator 2.0 (Anthropic, March 2026)

The skill-creator skill from Anthropic's official plugin set documents how to create
and iteratively improve skills using an eval/benchmark loop:

- Draft -> test with subagents -> benchmark with grader -> improve -> repeat
- Description optimization with `run_loop.py` (60/40 train/test split, 5 iterations)
- Progressive disclosure: metadata (100 words) -> SKILL.md body (<500 lines) -> references/
- Third-person description format with specific trigger phrases
- Imperative writing style in SKILL.md body (verb-first, not "you should")

Source: [GitHub: claude-plugins-official/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)

## Plugin Dev Skills (Anthropic, March 2026)

From Anthropic's official `plugin-dev` plugin:

- **plugin-structure**: Component auto-discovery, `${CLAUDE_PLUGIN_ROOT}` portability,
  `hooks/hooks.json` wrapper format vs settings direct format
- **skill-development**: 1500-2000 word SKILL.md target, third-person description,
  imperative body, `examples/` directory for working code samples
- **agent-development**: `<example>` blocks in frontmatter descriptions, `model: inherit`,
  color coding, 2-4 triggering examples required
- **hook-development**: Prompt-based hooks (LLM-driven) vs command hooks (deterministic),
  all hooks run in parallel, `SessionStart` for context loading
- **plugin-settings**: `.claude/plugin-name.local.md` pattern for per-project config,
  YAML frontmatter + markdown body, always gitignore `*.local.md`
- **command-development**: `$ARGUMENTS`, `$1 $2` positional args, `@` file references,
  `!` bash execution, `argument-hint` for autocomplete, `disable-model-invocation`

Source: [GitHub: claude-plugins-official/plugins/plugin-dev](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev)
