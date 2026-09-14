# GitHub Issue Taxonomy Guide

Taxonomy labels and rules are defined in `plugins/dev-utils/skills/github-issue-agent/issue-taxonomy.json`.

## Mandatory Dimensions for Every Issue

- **Type**: `type:bug`, `type:friction`, `type:map-debt`, `type:enhancement`, `type:documentation`, `type:security`, `type:architecture`, `type:test-gap`
- **Tier**: `tier:0-quickfix`, `tier:1-friction`, `tier:2-structural`, `tier:3-architecture`
- **Source**: `source:agent`, `source:human`, `source:script`, `source:test`, `source:review`, `source:migration`
- **Risk**: `risk:low`, `risk:medium`, `risk:high`, `risk:security-sensitive`, `risk:destructive-operation`
- **Location**: Must have at least one `area:*` label or one `plugin:*` label.
- **Status (Sequencing Signal)**: Auto-appends `status:needs-triage` if no status label is provided.
