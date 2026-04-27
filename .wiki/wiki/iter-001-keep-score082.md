---
concept: iter-001-keep-score082
source: plugin-code
source_file: agent-scaffolders/skills/fix-plugin-paths/evals/traces/iter_001_KEEP_score0.82.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.236954+00:00
cluster: plugin
content_hash: 5dc5181b5e8f818a
---

# Iter 001 Keep Score0.82

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/skills/fix-plugin-paths/evals/traces/iter_001_KEEP_score0.82.json -->
{
  "iteration": 1,
  "verdict": "KEEP",
  "score": 0.825,
  "baseline_score": 0.795,
  "delta": 0.03,
  "desc": "major upgrade: intake + mode C in-session evolution + self-assessment + operating principles",
  "mutation_diff": "diff --git a/plugins/agent-scaffolders/skills/fix-plugin-paths/SKILL.md b/plugins/agent-scaffolders/skills/fix-plugin-paths/SKILL.md\nindex ec79e5ed..cbd34154 100644\n--- a/plugins/agent-scaffolders/skills/fix-plugin-paths/SKILL.md\n+++ b/plugins/agent-scaffolders/skills/fix-plugin-paths/SKILL.md\n@@ -4,8 +4,10 @@ description: >\n   Fixes broken path references in plugin skill and agent files to ensure portability\n   across installed environments. Use when you see \"plugins/\" paths in SKILL.md or agent\n   files, need to standardize path references after installing a skill, want to audit and\n-  fix cross-plugin path dependencies, or are preparing plugin files for distribution via\n-  npx skills add or uvx.\n+  fix cross-plugin path dependencies, run a portability audit on a repository, neutralize\n+  hardcoded machine paths like /Users/, or are preparing plugin files for distribution via\n+  npx skills add or uvx. Also handles evolving a skill in-session while tracking quality\n+  scores with the eval runner to continuously improve skill routing accuracy.\n \n   <example>\n   Context: Agent just wrote a SKILL.md with a hardcoded source repo path.\n@@ -16,13 +18,31 @@ description: >\n   </commentary>\n   </example>\n \n+  <example>\n+  Context: User wants all plugin files ready for distribution.\n+  user: \"Run a portability audit on all SKILL.md files in this repo\"\n+  assistant: [triggers fix-plugin-paths, generates task tracker, audits each file one-by-one, marks complete, runs final sweep]\n+  <commentary>\n+  Repository-wide remediation request \u2014 use the Task Tracker Workflow.\n+  </commentary>\n+  </example>\n+\n+  <example>\n+  Context: Agent is mid-session doing related work and wants continuous skill improvement.\n+  user: \"Evolve the fix-plugin-paths skill while you work\"\n+  assistant: [triggers fix-plugin-paths Mode C, scaffolds evals if missing, establishes baseline, scores after each SKILL.md edit]\n+  <commentary>\n+  In-session evolution request \u2014 use Mode C: Direct Evolution Protocol.\n+  </commentary>\n+  </example>\n+\n allowed-tools: Bash, Read, Write, Edit\n ---\n \n # Identity: Plugin Path Portability Enforcer\n \n-You audit and fix path references in plugin skill and agent files to ensure they work\n-correctly when installed via `npx skills add`, the plugin installer, or `uvx`.\n+You audit, fix, and continuously improve plugin path portability in skill and agent files.\n+You ensure they work correctly when installed via `npx skills add`, the plugin installer, or `uvx`.\n \n **The core rule:** When a skill is installed, only its own directory exists:\n ```\n@@ -38,17 +58,19 @@ The full ruleset is in `references/fix-plugin-paths.prompt.md`.\n \n ---\n \n-## Phase 0: Identify Target\n+## Phase 0: Intake\n \n-If the user specifies a file or directory, use those. Otherwise:\n-```bash\n-# Find all .md files in the current plugin folder with broken path references\n-grep -rl \"plugins/[a-z][a-z-]*/\" . --include=\"*.md\" \\\n-  | grep -v \"CHANGELOG\\|broken_symlinks\\|repair_report\" \\\n-  | sort > /tmp/files_to_fix.txt\n-wc -l /tmp/files_to_fix.txt\n+If the user specifies a file or directory, confirm and proceed. Otherwise ask one question:\n+\n+```\n+Scope:  <single file | plugin directory | full repository>\n+Mode:   A) Single audit     \u2014 fix one file now\n+        B) Repository audit \u2014 generate task tracker, fix all flagged files\n+        C) In-session evolve \u2014 continuously score SKILL.md after each edit\n ```\n \n+Auto-detect the scope if inferable from context. If mode is clear from the request, skip the question.\n+\n ---\n \n ## Phase 1: Audit a File\n@@ -86,12 +108,12 @@ Zero results = clean.\n \n ---\n \n-## \ud83d\udccb Task Tracker Workflow (

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/fix-plugin-paths/evals/traces/iter_001_KEEP_score0.82.json -->
{
  "iteration": 1,
  "verdict": "KEEP",
  "score": 0.825,
  "baseline_score": 0.795,
  "delta": 0.03,
  "desc": "major upgrade: intake + mode C in-session evolution + self-assessment + operating principles",
  "mutation_diff": "diff --git a/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/SKILL.md b/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/SKILL.md\nindex ec79e5ed..cbd34154 100644\n--- a/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/SKILL.md\n+++ b/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/SKILL.md\n@@ -4,8 +4,10 @@ description: >\n   Fixes broken path references in plugin skill and agent files to ensure portability\n   across installed environments. Use when you see \"plugins/\" paths in SKIL

*(combined content truncated)*

## See Also

- [[iter-001-keep-score068]]
- [[iter-002-keep-score082]]
- [[iter-003-keep-score082]]
- [[iter-004-keep-score082]]
- [[iter-005-keep-score082]]
- [[improve-iter-1]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/skills/fix-plugin-paths/evals/traces/iter_001_KEEP_score0.82.json`
- **Indexed:** 2026-04-27T05:21:04.236954+00:00
