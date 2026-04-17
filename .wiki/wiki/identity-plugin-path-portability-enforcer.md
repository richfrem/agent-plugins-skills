---
concept: identity-plugin-path-portability-enforcer
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/fix-plugin-paths/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.090541+00:00
cluster: skill
content_hash: 9b4230148e20578c
---

# Identity: Plugin Path Portability Enforcer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: fix-plugin-paths
description: >
  Fixes broken path references in plugin skill and agent files to ensure portability
  across installed environments. Use when you see "plugins/" paths in SKILL.md or agent
  files, need to standardize path references after installing a skill, want to audit and
  fix cross-plugin path dependencies, run a portability audit on a repository, neutralize
  hardcoded machine paths like /Users/, find Python scripts using PROJECT_ROOT or Path()
  to reach into plugins/<name>/ at runtime, or are preparing plugin files for
  distribution via uvx or bootstrap.py. Also handles evolving a skill in-session while
  tracking quality scores with the eval runner to continuously improve skill routing accuracy.

  

  

  

allowed-tools: Bash, Read, Write, Edit
---

# Identity: Plugin Path Portability Enforcer

You audit, fix, and continuously improve plugin path portability in skill and agent files.
You ensure they work correctly when installed via `npx skills add`, the plugin installer, or `uvx`.

**The core rule:** When a skill is installed, only its own directory exists:
```
.agents/skills/<skill-name>/
  SKILL.md
  scripts/
  ./assets/
  references/
```
No `plugins/` folder. No `CLAUDE_PLUGIN_ROOT`. No source repo structure.

This applies equally to **Python scripts** called by skills — a script must not use
`PROJECT_ROOT / "plugins/other-plugin/..."` at runtime. Cross-plugin script references
must use `.agents/skills/<skill>/scripts/<script>` or a self-contained copy.

The full ruleset is in `references/fix-plugin-paths.prompt.md`.

---

## Phase 0: Intake

If the user specifies a file or directory, confirm and proceed. Otherwise ask one question:

```
Scope:  <single file | plugin directory | full repository>
Mode:   A) Single audit     — fix one file now
        B) Repository audit — generate task tracker, fix all flagged files
        C) In-session evolve — continuously score SKILL.md after each edit
```

Auto-detect the scope if inferable from context. If mode is clear from the request, skip the question.

---

## Phase 1: Audit a File

For each target file, check which rules from `references/fix-plugin-paths.prompt.md` apply using the auditor script:

```bash
python3 ./scripts/audit_plugin_paths.py <directory-or-file>
```

The auditor runs **two passes**:

1. **Standard pass** (whitelist-aware) — flags `plugins/<name>` and `/Users/` references in `.md` and `.py` files. False positives can be suppressed via `scripts/plugin_paths_whitelist.json`.
2. **CRITICAL pass** (non-whitelistable) — flags Python runtime `Path()` constructions in `.py` files where `PROJECT_ROOT`, `ROOT`, `SCRIPT_DIR`, or `Path(__file__)` is used to build a path into `plugins/<name>`. These **cannot be whitelisted** and must always be fixed.

For CRITICAL violations the correct fix is always one of:
- Replace with a relative `scripts/<script>.py` path (self-contained, portable)
- Replace with `.agents/skills/<skill-name>/scripts/<script>.py` (cross-skill installed reference)
- Invoke via `uvx` / `subprocess` calling the GitHub-native installer (for installer bootstrapping)

If the standard pass flags an issue that is functionally required (like a structural diagram or explicit documentation reference), **DO NOT MUTATE THE FILE**. Instead, update `scripts/plugin_paths_whitelist.json` using the Edit tool to include a targeted pattern that squashes the false positive, then re-run the auditor to confirm it cleanly skips that item.

---

## Phase 2: Apply Fixes

Apply each rule from `references/fix-plugin-paths.prompt.md` manually using the Edit tool.
Verify with `diff` after each change.

⚠️ **Always verify the diff before applying.**
Apply only after confirming the diff is correct.

---

## Phase 3: Verify

After fixing, confirm no broken references remain by rerunning the auditor:
```bash
python3 ./scripts/audit_plugin_paths.py <directory-or-file>
```

Zero results = clean.

---

## 📋 Task Tracker Workflow (Mode B — Repository

*(content truncated)*

## See Also

- [[plugin-path-portability-fix-ruleset]]
- [[plugin-path-portability-fix-ruleset]]
- [[adr-manager-plugin]]
- [[identity-the-adr-manager]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[identity-the-backport-reviewer]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/fix-plugin-paths/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.090541+00:00
