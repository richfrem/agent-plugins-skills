---
name: audit-skill
plugin: agent-scaffolders
description: Audits and aligns individual agent skills and sub-agents against ecosystem evolution standards, verifying line budgets, evals schemas, and hub-and-spoke isolation.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# audit-skill: Skill Alignment & Evolution Auditor

Audits an individual skill against the 6 ecosystem evolution invariants and provides automated refactoring recommendations to achieve full compliance.

---

## The 6 Alignment Invariants

1. **Layer 1 Procedural Core:** `SKILL.md` target $\le 100$ lines. Offload domain depth to `references/` via Progressive Disclosure.
2. **Boolean Evals Schema:** `evals/evals.json` must be a root JSON list with `should_trigger: true/false`.
3. **Hub-and-Spoke Script Isolation (ADR-002/003):** All scripts reside in plugin root `scripts/` and are symlinked into `skills/<skill>/scripts/`. Zero un-symlinked real files.
4. **Frontmatter Standards:** `name` matches directory slug exactly; `description` is third-person active verb and $\le 1024$ chars.
5. **Contract & Fallback Links:** Must provide `acceptance-criteria.md` and `fallback-tree.md` in `references/`.
6. **Spoke Hygiene:** Zero session logs, raw wiki traces, or `.agent/` state in skill folders.

---

## Quick Execution

Run the bundled alignment script directly against any skill directory:

```bash
# Audit a single skill
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name>

# Auto-repair fixable schema deviations (e.g. migrate evals.json)
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name> --fix

# JSON output for automated pipelines
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name> --json
```

---

## Alignment & Refactoring Procedure

### Phase 1: Diagnostic Assessment
1. Run `audit_skill.py <path>`. Note all errors and warnings.
2. If `SKILL.md` exceeds 100 lines:
   - Identify detailed background, multi-page tables, or complex workflows.
   - Extract them into `references/<topic>.md`.
   - Replace in `SKILL.md` with concise procedural steps and markdown links.

### Phase 2: Hub-and-Spoke Remediation (ADR-002/003)
If real scripts are found inside `skills/<skill>/scripts/`:
1. Move the real script to `plugins/<plugin>/scripts/<script-name>.py`.
2. Register the symlink in `symlinks.json`.
3. Run `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py restore`.
4. Run `symlink_manager.py diagnose` to confirm zero imposters.

### Phase 3: Contract Verification
1. Ensure `evals/evals.json` has at least 3 positive and 3 negative test cases using `should_trigger`.
2. Ensure `references/acceptance-criteria.md` and `references/fallback-tree.md` are linked.
3. Re-run `audit_skill.py` to confirm 100% PASS.
