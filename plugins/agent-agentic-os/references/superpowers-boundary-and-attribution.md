# Superpowers Boundary and Attribution

This document records how Agentic OS relates to the upstream `obra/superpowers` project. It is the
source of truth for dependency claims in this plugin's README, summary, and usage documentation.

## Runtime dependency

The Agentic OS control plane has no hard runtime dependency on Superpowers. Its core lifecycle is
implemented locally by transition templates, Python control-plane modules, SQLite persistence,
verification receipts, worktree records, and retrospective gates. Installing Agentic OS does not
require installing Superpowers.

## Optional use and fallback

The surrounding execution policy prefers the host's native Plan Mode, worktree tooling, review
tools, and test runner. Superpowers may be used as an optional fallback when the host does not
provide an equivalent capability or when a complex multi-agent execution graph benefits from its
workflow. A fallback must remain recorded by the Agentic OS control plane; it must not bypass a
transition contract, human approval, or verification gate.

## Practices Agentic OS learned from

Agentic OS incorporates compatible practices associated with Superpowers, including:

- intent-first brainstorming and adaptive, one-question-at-a-time discovery;
- explicit constraints, acceptance criteria, and design approval before implementation;
- right-sized implementation tasks, file maps, test-first thinking, and self-review;
- isolated worktrees, review checkpoints, and verification before completion.

These are workflow ideas and governance patterns, not a claim that the Superpowers runtime is
embedded in this plugin.

## Artifact compatibility

The control plane accepts `docs/superpowers/` planning artifacts for compatibility with existing
workflows. That path is an artifact convention, not a runtime import or installation dependency.

## Attribution

The workflow patterns above are inspired by and adapted from
[`obra/superpowers`](https://github.com/obra/superpowers), an MIT-licensed open-source project.
Thank you to its maintainers and contributors for making those practices available to the agent
engineering community.

## Update rule

Update this document whenever Agentic OS changes its planning, interview, worktree, review,
verification, or artifact-routing behavior. If a future change introduces a direct runtime call,
document it explicitly as a new optional or hard dependency before release.
