> Retired skill `create-agents-md`, kept as the **create-agents-md** mode of `authoring-instructions`. Body unchanged apart from link targets and corrected commands. Frontmatter removed.
>
> Original description: Scaffolds a lean, progressive-disclosure AGENTS.md root instruction file and a thin CLAUDE.md bridge. Use when setting up, migrating, or standardizing root instruction files across a repository.

# Create AGENTS.md / CLAUDE.md

Scaffolds a lean, progressive-disclosure repository root instruction file (`AGENTS.md`) and establishes a thin `CLAUDE.md` bridge conforming to `references/agents-md-contract.md`.

## Quick Start

```bash
# Validate existing files before scaffolding or migrating
python3 scripts/audit_agents_md.py AGENTS.md
```

## Workflow

1. **Discovery & Safety Check**:
   - Check if `AGENTS.md` or `CLAUDE.md` already exist. **NEVER silently overwrite an existing file.** Propose a unified diff instead.
   - Inspect build files (`package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`) to identify primary build and test commands.
2. **Drafting `AGENTS.md`**:
   - Load template from `assets/templates/AGENTS.md.jinja`.
   - Adhere strictly to the 5-part skeleton in contract §6:
     1. `# AGENTS.md` with `## Overview`: One concise paragraph describing stack and purpose.
     2. `## Architecture & Layout`: <= 8 lines pointing to `architecture.md` (zero ASCII trees).
     3. `## Core Commands`: <= 8 lines of essential build/test commands.
     4. `## Non-Negotiable Rules / Invariants`: Inline 1-line statements using uppercase modal tokens (`MUST`, `NEVER`, `ALWAYS`, `DO NOT`, `REQUIRED`, `PROHIBITED`) linking to detailed policy rules in `.agent/rules/`.
     5. `## On-Demand Skills & Reference Index`: Lazy pointers with "Read when..." triggers.
3. **Establishing the `CLAUDE.md` Bridge & Handling Migrations**:
   - **Greenfield**: If `CLAUDE.md` does not exist, write the minimal bridge:
     ```markdown
     # CLAUDE.md

     Read [AGENTS.md](AGENTS.md).
     ```
   - **Brownfield**: If `CLAUDE.md` exists with unique instructions not present in `AGENTS.md`, **NEVER overwrite it directly**. Propose a migration diff that moves unique instructions into `AGENTS.md` (or `.agent/rules/`), and then convert `CLAUDE.md` into the minimal bridge.
   - Hard limit: Keep `CLAUDE.md` under 5 lines. Never maintain duplicate rules in both files.
4. **Verification**:
   - Run the audit script:
     ```bash
     python3 scripts/audit_agents_md.py AGENTS.md --strict
     python3 scripts/audit_agents_md.py CLAUDE.md --strict
     ```
   - Verify transitive eager payload is <= 100 lines.

## References

- [Contract](../agents-md-contract.md)
- [Template](../../assets/templates/AGENTS.md.jinja)
