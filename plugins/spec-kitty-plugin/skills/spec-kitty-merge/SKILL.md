---
name: spec-kitty-merge
description: A standard Spec-Kitty workflow routine.
---

## 🔗 Workflow Provenance

> **Source**: This skill augments the baseline workflow located at [`./workflows/spec-kitty.merge.md`](./workflows/spec-kitty.merge.md).
> It acts as an intelligent wrapper that is continuously improved with each execution.

<!-- spec-kitty-command-version: 3.0.0 -->
Run this exact command and treat its output as authoritative.
Do not rediscover context from branches, files, or prompt contents.

`spec-kitty agent shim merge --agent windsurf --raw-args "$ARGUMENTS"`
