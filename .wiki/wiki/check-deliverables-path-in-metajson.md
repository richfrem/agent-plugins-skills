---
concept: check-deliverables-path-in-metajson
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/implement.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.359334+00:00
cluster: research
content_hash: 02f06f4253ae89f7
---

# Check deliverables_path in meta.json

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Implement a research work package by conducting research and documenting findings.
---

## Research WP Implementation

**CRITICAL**: Research missions separate PLANNING ARTIFACTS from RESEARCH DELIVERABLES.

### Two Types of Artifacts (IMPORTANT)

| Type | Location | Edited Where | Purpose |
|------|----------|--------------|---------|
| **Sprint Planning** | `kitty-specs/{{feature_slug}}/research/` | Main repo | Evidence/sources for planning THIS sprint |
| **Research Deliverables** | `{{deliverables_path}}` | Worktree | Actual research outputs (your work product) |

### Where to Put Your Research

**Your research findings go in:** `{{deliverables_path}}`

This is configured in `meta.json` during planning. To find it:

```bash
# Check deliverables_path in meta.json
cat kitty-specs/{{feature_slug}}/meta.json | grep deliverables_path
```

Examples of valid deliverables paths:
- `docs/research/001-market-analysis/`
- `research-outputs/002-literature-review/`

**DO NOT** put research deliverables in:
- `kitty-specs/` (reserved for sprint planning)
- `research/` at project root (ambiguous, conflicts with kitty-specs/###/research/)

---

## Implementation Workflow

Run this command to get started:

```bash
spec-kitty agent workflow implement $ARGUMENTS --agent <your-name>
```

<details><summary>PowerShell equivalent</summary>

```powershell
spec-kitty agent workflow implement $ARGUMENTS --agent <your-name>
```

</details>

**CRITICAL**: You MUST provide `--agent <your-name>` to track who is implementing!

### Step 1: Navigate to Your Worktree

```bash
cd {{workspace_path}}
```

<details><summary>PowerShell equivalent</summary>

```powershell
Set-Location {{workspace_path}}
```

</details>

Your worktree is an isolated workspace for this WP. The deliverables path is accessible here.

### Step 2: Create Research Deliverables (In Worktree)

Create your research outputs in the deliverables path:

```bash
# Create the deliverables directory if it doesn't exist
mkdir -p {{deliverables_path}}

# Create your research files
# Examples:
# - {{deliverables_path}}/findings.md
# - {{deliverables_path}}/report.md
# - {{deliverables_path}}/data/analysis.csv
# - {{deliverables_path}}/recommendations.md
```

### Step 3: Commit Research Deliverables (In Worktree)

**BEFORE moving to for_review**, commit your research outputs:

```bash
cd {{workspace_path}}
git add {{deliverables_path}}/
git commit -m "research({{wp_id}}): <describe your research findings>"
```

<details><summary>PowerShell equivalent</summary>

```powershell
Set-Location {{workspace_path}}
git add {{deliverables_path}}/
git commit -m "research({{wp_id}}): <describe your research findings>"
```

</details>

Example commit messages:
- `research(WP01): Document core entities and relationships`
- `research(WP03): Add market analysis findings and recommendations`
- `research(WP05): Complete literature review synthesis`

### Step 4: Move to Review

**Only after committing**, move your WP to review:

```bash
spec-kitty agent tasks move-task {{wp_id}} --to for_review --note "Ready for review: <summary>"
```

---

## Sprint Planning Artifacts (Separate)

Planning artifacts in `kitty-specs/{{feature_slug}}/research/` are:
- `evidence-log.csv` - Evidence collected DURING PLANNING
- `source-register.csv` - Sources cited DURING PLANNING

**If you need to update these** (rare during implementation):
- They're in the planning repo (sparse-excluded from worktrees)
- Edit them directly in the planning repository
- Commit to the target branch before moving status

**Most research WPs only produce deliverables, not planning updates.**

---

## Research CSV Schemas (CRITICAL - DO NOT MODIFY HEADERS)

**⚠️  WARNING:** These schemas are validated during review. Modifying headers will BLOCK your review.

### evidence-log.csv Schema

**Required columns (exact order, do not change):**
```csv
timestamp,source_type,citation,key_finding,confidence,notes
```

| Column | Type | Description | Val

*(content truncated)*

## See Also

- [[os-health-check-sub-agent]]
- [[todo-check]]
- [[defense-in-depth-validation]]
- [[red-team-audit-template-epistemic-integrity-check]]
- [[human-in-the-loop-hitl-interaction-design-guide]]
- [[quantification-enforcement-in-analysis]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/implement.md`
- **Indexed:** 2026-04-17T06:42:10.359334+00:00
