---
name: setting-up-agentic-os
plugin: agent-agentic-os
description: >
  Sets up and retrofits a project for the Agentic OS and guides a human through creating the approval
  signing key. Use for "set up agentic OS", "initialize agent harness", "init my project for AI agents",
  "retrofit repository", "upgrade project for evolution", "sync instruction files", "where do I put
  CLAUDE.md", "what goes in the context folder", "create my agent environment", "set up persistent
  memory", "get Claude to use skills in this project", "set up my approval key", "create the ssh
  signing key", "set up signing identity", "HUMAN_PROOF_REQUIRED", "test my signing key". Keeps AGENTS.md
  the sole canonical instruction file; bootstraps 3-layer memory, the control-plane database, git
  guards and the agent's simulation identity. Needs running-control-plane installed beside it. Not for running tasks (use running-control-plane).
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Setting up the Agentic OS

One-time and occasional setup: bootstrap or retrofit a repository, and help a human create the SSH key that authorizes the approval gates. Each mode below was a separate skill; its full workflow is a reference loaded when that mode starts.

## Contents

- [Critical constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical constraints

1. **Read-only preflight.** Probe first to classify the repository; never blindly overwrite existing instructions.
2. **`AGENTS.md` is canonical.** `CLAUDE.md` is at most a short pointer. Preserve custom user instructions during a retrofit.
3. **Humans create keys, agents never do.** Never run key enrollment, never read, copy or move a private key, never edit `allowed_signers*`, never pipe a passphrase or fabricate a signature.
4. **The agent has its own identity.** Init creates the agent's simulation key for the simulator and the setup validation; it never writes the human's production trust file. See [agent-identity.md](references/agent-identity.md).
5. **Depends on `running-control-plane`.** The scripts import its `control_plane` package from the sibling skill folder and stop with a clear message when it is missing.

## Quick start

Classify the target repository before doing anything (from this skill's folder; the script ships with `running-control-plane`):

```bash
python3 ../running-control-plane/scripts/control_plane/installation_probe.py --target <project-path>
```

## Workflow

| Mode | Use when | Run | Workflow |
|---|---|---|---|
| `init` | Setting up a new project or retrofitting one: where CLAUDE.md and the context folder go, blending an existing CLAUDE.md or AGENTS.md, persistent memory between sessions, skills and scheduled loops in a project, agent harness for a docs or legacy project | `python3 scripts/init_agentic_os.py --target <path> [--retrofit \| --sync-instructions]` | [init](references/modes/init.md) |
| `signing-setup` | A human must create or test the approval key | `python3 scripts/setup_ciba_identity.py` (the human runs it in their own terminal), `scripts/test_signing_mechanics.py` | [signing-setup](references/modes/signing-setup.md) |

**Routing rule:** the table above only routes. Before acting in a mode, read that mode's workflow file in full (the last column); open the detail references below only from inside it.

## Verification

The post-setup healthcheck is [setup-healthcheck-validation.md](references/setup-healthcheck-validation.md). Run `python3 -m pytest` against the init and signing tests in the `running-control-plane` skill (they exercise both skills together). Each mode's gates are in [acceptance-criteria.md](references/acceptance-criteria.md); on failure follow [fallback-tree.md](references/fallback-tree.md).

## References

Detail files, grouped by the mode that uses them. Read the mode workflow first.

- **init**: [setup-healthcheck-validation](references/setup-healthcheck-validation.md) • [agent-identity](references/agent-identity.md) • [init-detailed-reference](references/init-detailed-reference.md) • [init-interview](references/init-interview.md) • [instruction-blending](references/instruction-blending.md) • [retrofit-planning](references/retrofit-planning.md)
- **signing-setup**: [SIGNING_WORKFLOW_OVERVIEW](references/SIGNING_WORKFLOW_OVERVIEW.md) • [signing-setup-guide](references/signing-setup-guide.md) • [isolation-setup](references/isolation-setup.md)
