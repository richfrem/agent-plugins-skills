# Learning Loop Architecture

The learning loop architecture is defined in the **agent-loops** plugin.

All plugins below install from: `github.com/richfrem/agent-plugins-skills`

## agent-loops

- **GitHub**: https://github.com/richfrem/agent-plugins-skills/tree/main/plugins/agent-loops/skills/learning-loop
- **When installed**: `.agents/skills/learning-loop/SKILL.md`

Provides composable loop architectures: single-loop (tactical), dual-loop
(strategic + tactical), and triple-loop (meta-learning). The learning loop
performs retrospectives, identifies friction patterns, and updates skills.

## agent-agentic-os

- **GitHub**: https://github.com/richfrem/agent-plugins-skills/tree/main/plugins/agent-agentic-os/skills/os-improvement-loop
- **When installed**: `.agents/skills/os-improvement-loop/SKILL.md`

The OS-level improvement loop reviews event logs, detects systemic friction,
and organically updates skills, prompts, or CLAUDE.md.

## agent-execution-disciplines

- **GitHub**: https://github.com/richfrem/agent-plugins-skills/tree/main/plugins/agent-execution-disciplines
- **When installed**: `.agents/skills/` (TDD, debugging, verification, code review, git worktrees)

Core disciplines that learning loops can improve over time.
