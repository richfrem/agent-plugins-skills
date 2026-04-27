---
concept: iter-004-keep-score082
source: plugin-code
source_file: agent-scaffolders/skills/fix-plugin-paths/evals/traces/iter_004_KEEP_score0.82.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.238223+00:00
cluster: plugin
content_hash: 8b39610d6be1b574
---

# Iter 004 Keep Score0.82

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/skills/fix-plugin-paths/evals/traces/iter_004_KEEP_score0.82.json -->
{
  "iteration": 4,
  "verdict": "KEEP",
  "score": 0.825,
  "baseline_score": 0.795,
  "delta": 0.03,
  "desc": "Iter 7: whitelists for link-checker, adr-manager, doc-patterns",
  "mutation_diff": "diff --git a/plugins/agent-scaffolders/skills/fix-plugin-paths/evals/results.tsv b/plugins/agent-scaffolders/skills/fix-plugin-paths/evals/results.tsv\nindex d8447d1f..8714e5a1 100644\n--- a/plugins/agent-scaffolders/skills/fix-plugin-paths/evals/results.tsv\n+++ b/plugins/agent-scaffolders/skills/fix-plugin-paths/evals/results.tsv\n@@ -3,3 +3,4 @@ timestamp\tcommit\tscore\tbaseline\taccuracy\theuristic\tf1\tstatus\tdescription\n 2026-04-03T16:17:49.250390\t73b567cc\t0.8250\t0.7950\t0.7500\t1.0000\t0.8421\tKEEP\tmajor upgrade: intake + mode C in-session evolution + self-assessment + operating principles\n 2026-04-03T16:21:25.653401\t55f17c25\t0.8250\t0.7950\t0.7500\t1.0000\t0.8421\tKEEP\tcontinuing audit: self-audit.md fix + tracker updates + 21 files processed\n 2026-04-03T16:46:22.576223\t0691bbf5\t0.8250\t0.7950\t0.7500\t1.0000\t0.8421\tKEEP\tuse relative root dir for self eval script\n+2026-04-03T17:30:52.029078\t57f9185c\t0.8250\t0.7950\t0.7500\t1.0000\t0.8421\tKEEP\tIter 7: whitelists for link-checker, adr-manager, doc-patterns\n",
  "routing_detail": [
    {
      "input": "fix the plugin path references in this skill.md",
      "should_trigger": true,
      "matched_keywords": [
        "path",
        "plugin",
        "references",
        "skill"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "audit all plugin files for broken path references",
      "should_trigger": true,
      "matched_keywords": [
        "audit",
        "broken",
        "files",
        "path",
        "plugin",
        "references"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "standardize path references after installing this skill",
      "should_trigger": true,
      "matched_keywords": [
        "after",
        "installing",
        "path",
        "references",
        "skill",
        "standardize"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "there are hardcoded plugins/ paths in my skill files \u2014 fix them",
      "should_trigger": true,
      "matched_keywords": [
        "files",
        "hardcoded",
        "paths",
        "plugins",
        "skill"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "prepare these plugin files for distribution via npx skills add",
      "should_trigger": true,
      "matched_keywords": [
        "distribution",
        "files",
        "plugin",
        "skills"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "i see /users/richardfremmerlid in my skill.md \u2014 remove the machine path",
      "should_trigger": true,
      "matched_keywords": [
        "machine",
        "path",
        "skill",
        "users"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "fix cross-plugin path dependencies in agent-agentic-os",
      "should_trigger": true,
      "matched_keywords": [
        "agent",
        "cross",
        "dependencies",
        "path",
        "plugin"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "run a portability audit on all skill.md files in this repo",
      "should_trigger": true,
      "matched_keywords": [
        "audit",
        "files",
        "portability",
        "skill"
      ],
      "triggered": true,
      "correct": true
    },
    {
      "input": "there are broken symlinks in my installed skills folder",
      "should_trigger": false,
      "matched_keywords": [
        "broken",
        "installed",
        "skills"
      ],
      "triggered": true,
      "correct": false,
      "failure_reason": "false positive \u2014 keywords ['broken', 'installed', 'skills'] matched a should_trigger=false input"
    },
    {
 

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/fix-plugin-paths/evals/traces/iter_004_KEEP_score0.82.json -->
{
  "iteration": 4,
  "verdict": "KEEP",
  "score": 0.825,
  "baseline_score": 0.795,
  "delta": 0.03,
  "desc": "Iter 7: whitelists for link-checker, adr-manager, doc-patterns",
  "mutation_diff": "diff --git a/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/evals/results.tsv b/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/evals/results.tsv\nindex d8447d1f..8714e5a1 100644\n--- a/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/evals/results.tsv\n+++ b/plugins/agent-plugin-analyzer/skills/fix-plugin-paths/evals/results.tsv\n@@ -3,3 +3,4 @@ timestamp\tcommit\tscore\tbaseline\taccuracy\theuristic\tf1\tstatus\tdescription\n 2026-04-03T16:17:49.250390\t73b567cc\t0.8250\t0.7950\t0.7500\t1.0000\t0.8421\tKEEP\tmajor up

*(combined content truncated)*

## See Also

- [[iter-001-keep-score082]]
- [[iter-002-keep-score082]]
- [[iter-003-keep-score082]]
- [[iter-005-keep-score082]]
- [[iter-001-keep-score068]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/skills/fix-plugin-paths/evals/traces/iter_004_KEEP_score0.82.json`
- **Indexed:** 2026-04-27T05:21:04.238223+00:00
