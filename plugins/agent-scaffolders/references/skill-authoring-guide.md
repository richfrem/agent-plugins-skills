# Skill authoring guide

## Contents

- [Entry point](#entry-point)
- [Resource layout](#resource-layout)
- [Audit rules and reports](#audit-rules-and-reports)
- [Evaluations](#evaluations)

## Entry point

Use purpose, useful Contents, critical constraints, Quick start, Workflow, Verification
and direct References as a default. Tiny skills omit unnecessary sections. Give each
reference a task-specific reading condition. The first 100 lines should reveal the
starting action, critical rules and resource scope. Agents may preview part of a file;
there is no universal 100-line loading limit.

Keep the local 80-line target advisory. Anthropic recommends fewer than 500 body lines
and early contents for references over 100 lines. Split substantial details by task or
topic rather than arbitrary chunks; do not hide required constraints in reference chains.

## Resource layout

Instructional skills need SKILL.md and realistic evaluations, not a Python placeholder.
Executable skills additionally declare commands, dependencies, outputs and validation.
Use plugin-root scripts/references/assets as canonical sources and managed file-level
spokes. Installation materializes portable copies; resolve all paths from the skill root.
Generator receipts propose links and distinguish generated from pending_links status.

## Audit rules and reports

The bundled JSON authoring contract owns version, thresholds, layout variants and
rule definitions. Repository errors cover broken metadata, links, evaluations and
applicable packaging. Navigation and language heuristics are warnings. Anthropic
reserved-name restrictions remain warnings so existing routing identities survive.

Audit source and installed representations separately. Installed resources are real
files; source resources are managed links. Preserve total line_count and separately
report frontmatter_lines/body_lines. Anchor checking ignores fences, lowercases Unicode
headings, removes punctuation and gives duplicate slugs -1, -2 suffixes. Unsupported
reference-style Markdown gets a warning for manual resolution.

Repository report schema 2 replaces the old bare list with skills, noncanonical,
scan_failures and summary counts. --legacy-json provides list compatibility. Each
finding includes rule ID, origin, severity, path and line. Discovery uses exact canonical
locations; installed/fixture/archive/external copies are classified separately. Content
identity alone does not merge distinct routing identities.

The auditor reports facts. Migration actions, preservation decisions and before/after
reviews belong to task evidence joined by canonical path and hashes. No scan invokes
a model. AI review is an optional agent workflow with its own result and route evidence.

## Evaluations

Routing: evals/evals.json is a root array with actual should_trigger booleans.
Task success: evals/task-success.json is a root array with expected_behavior string
lists, query and optional files. Use at least three observed scenarios and compare
against a baseline. Test the intended models; record missing coverage honestly.
Never invent routing outcomes, convert success evaluations into routing tests or
claim a structural scan demonstrates behavioral quality.
