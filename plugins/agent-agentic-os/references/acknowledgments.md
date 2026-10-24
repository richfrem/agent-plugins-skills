# Acknowledgments

Agentic OS depends on no external workflow package. The control plane, its transition rules, the SQLite persistence, the verification receipts and the worktree and retrospective gates are implemented in this plugin.

## Contents

- [Superpowers](#superpowers)
- [Research that shaped the design](#research-that-shaped-the-design)

## Superpowers

Several of the practices here were shaped by [`obra/superpowers`](https://github.com/obra/superpowers), an MIT-licensed open-source project:

- intent-first brainstorming and adaptive, one-question-at-a-time discovery;
- explicit constraints, acceptance criteria and design approval before implementation;
- right-sized tasks, test-first thinking and self-review;
- isolated worktrees, review checkpoints and verification before completion.

Thank you to its maintainers and contributors for making those practices available to the agent engineering community. The control plane also accepts planning documents under `docs/superpowers/`, in the same way it accepts `docs/plans/`.

## Research that shaped the design

- The improvement loop follows the [Karpathy 3-file autoresearch pattern](../skills/improving-skills-in-lab/references/karpathy-autoresearch-3-file-eval.md) and the harness-search results of [Lee et al. (2026)](../skills/improving-skills-in-lab/references/meta-harness-lee-2026.md).
- The control-plane architecture draws on the Agent-OS and control-plane papers summarized in [research/](research/).
