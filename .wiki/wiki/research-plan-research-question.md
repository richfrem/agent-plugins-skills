---
concept: research-plan-research-question
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/research/templates/plan-template.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.342731+00:00
cluster: plugin-code
content_hash: 3850d398e77d8555
---

# Research Plan: [RESEARCH QUESTION]

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Research Plan: [RESEARCH QUESTION]

**Branch**: `[###-research-name]` | **Date**: [DATE] | **Spec**: [link]

## Summary
[One paragraph: research question + methodology + expected outcomes]

## Research Context

**Research Question**: [Primary question]  
**Research Type**: Literature Review | Empirical Study | Case Study  
**Domain**: [Academic field or industry domain]  
**Time Frame**: [When research will be conducted]  
**Resources Available**: [Databases, tools, budget, time]

**Key Background**:
- [Context point 1]
- [Context point 2]

## Methodology

### Research Design

**Approach**: [Systematic Literature Review | Survey | Experiment | Mixed Methods]

**Phases**:
1. **Question Formation** (Week 1)
   - Define precise research question
   - Identify sub-questions
   - Establish scope and boundaries
2. **Methodology Design** (Week 1-2)
   - Select data collection methods
   - Define analysis framework
   - Establish quality criteria
3. **Data Gathering** (Week 2-4)
   - Search academic databases
   - Screen sources for relevance
   - Extract key findings
   - Populate `research/evidence-log.csv`
4. **Analysis** (Week 4-5)
   - Code and categorize findings
   - Identify patterns and themes
   - Assess evidence quality
5. **Synthesis** (Week 5-6)
   - Draw conclusions
   - Address research question
   - Identify limitations
6. **Publication** (Week 6)
   - Write findings report
   - Prepare presentation
   - Share results

### Data Sources

**Primary Sources**:
- [Database 1: e.g., IEEE Xplore, PubMed, arXiv]
- [Database 2]

**Secondary Sources**:
- [Gray literature, industry reports, etc.]

**Search Strategy**:
- **Keywords**: [List search terms]
- **Inclusion Criteria**: [What qualifies for review]
- **Exclusion Criteria**: [What will be filtered out]

### Analysis Framework

**Coding Scheme**: [How findings will be categorized]  
**Synthesis Method**: [Thematic analysis | Meta-analysis | Narrative synthesis]  
**Quality Assessment**: [How source quality will be evaluated]

## Data Management

### Evidence Tracking

**File**: `research/evidence-log.csv`  
**Purpose**: Track all evidence collected with citations and findings

**Columns**:
- `timestamp`: When evidence collected (ISO format)
- `source_type`: journal | conference | book | web | preprint
- `citation`: Full citation (BibTeX or APA format)
- `key_finding`: Main takeaway from this source
- `confidence`: high | medium | low
- `notes`: Additional context or caveats

**Agent Guidance**:
1. Read source and extract key finding.
2. Add row to evidence-log.csv.
3. Assign confidence level based on source quality and clarity.
4. Note limitations or alternative interpretations.

### Source Registry

**File**: `research/source-register.csv`  
**Purpose**: Maintain master list of all sources for bibliography

**Columns**:
- `source_id`: Unique identifier (e.g., "smith2025")
- `citation`: Full citation
- `url`: Link to source (if available)
- `accessed_date`: When source was accessed
- `relevance`: high | medium | low
- `status`: reviewed | pending | archived

**Agent Guidance**:
1. Add source to register when first discovered.
2. Update status as research progresses.
3. Maintain relevance ratings to prioritize review.

## Research Deliverables Location

**REQUIRED**: Specify where research outputs will be stored.

This location is SEPARATE from `kitty-specs/` planning artifacts.

**Deliverables Path**: `docs/research/[###-research-name]/`

*(Update this path during planning - e.g., `docs/research/001-cancer-cure/`, `research-outputs/market-analysis/`)*

This path will:
- Be created in each WP worktree
- Contain the actual research findings (markdown, data, diagrams)
- Be merged to main when WPs complete (like code)

**Do NOT use**:
- `kitty-specs/` (reserved for sprint planning artifacts)
- `research/` at project root without a subdirectory (ambiguous)

### Why Two Locations?

| Type | Location | Purpose |
|------|----------|---------|
| **Planning Artifacts** | `kitty-sp

*(content truncated)*

## See Also

- [[research-specification-research-question]]
- [[work-packages-research-question]]
- [[research-summary-agent-operating-systems-agent-os]]
- [[research-summary-agent-operating-systems-aos]]
- [[sources-template---research-topic-name]]
- [[hooks-research]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/research/templates/plan-template.md`
- **Indexed:** 2026-04-17T06:42:10.342731+00:00
