# Project configuration workflow

## Contents

- [Discovery](#discovery)
- [Plan](#plan)
- [Scaffold and verify](#scaffold-and-verify)

## Discovery

After prerequisites and the capability baseline, collect missing setup inputs:
selected runtimes, project type, build/test/lint/dev commands, primary agent role,
scoped conventions and non-secret provider constraints. Reuse the capability
interview's provider/model answers rather than repeating them here.

## Plan

Present concrete files and intended settings for the selected project: Claude
configuration/instructions, applicable Google/ADK configuration, scoped rules,
permissions and capability profile. Reuse existing authorization where it covers
these writes; otherwise obtain approval for the concrete plan before scaffolding.
Do not overwrite unrelated existing settings or create files for unselected runtimes.

## Scaffold and verify

For Claude Code, use the bundled directory/settings references; keep CLAUDE.md
concise (target under 200 lines) and place domain rules in the runtime's rules folder.
For Google/ADK, use the applicable bundled directory and command references. Confirm
which installed runtime consumes each configuration path; do not treat Gemini CLI,
Antigravity and ADK as identical settings engines. Modularize context using supported
imports and preserve existing project configuration.

Configuration outputs and the capability profile belong to the caller's selected
project, not this skill's installation. Skill resources/commands resolve from the
skill root. Verify generated syntax, permissions and scoped rule discovery with the
selected runtime. Write or refresh confirmed profile values through capability_profile.
Report written paths, profile status, unavailable providers and exact remaining actions.
Later review transitions consume this baseline and require an authorized review route;
setup does not launch reviewers or refresh catalogs on their behalf.
