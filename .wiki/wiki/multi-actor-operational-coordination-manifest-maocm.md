---
concept: multi-actor-operational-coordination-manifest-maocm
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/multi-actor-operational-coordination-manifest.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.010976+00:00
cluster: document
content_hash: 0188d51dafb7bfab
---

# Multi-Actor Operational Coordination Manifest (MAOCM)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: multi-actor-operational-coordination-manifest
description: Structuring a single generated document as an actionable distributed workflow by embedding explicit actor roles in section headers or column labels, prompting simultaneous multi-party execution.
category: Input / Interpretation Constraints
priority: Medium
---

# Multi-Actor Operational Coordination Manifest (MAOCM)

## Executive Summary
A single generated document functions simultaneously as an **operational orchestration artifact** for distinct organizational actors. Rather than producing one customized document for one specific audience, MAOCM structures sections so each is implicitly addressed to a different actor class (e.g., IT, Manager, QA, Developer) with a different **action verb and action scope**. The document's structural labeling acts as the distribution mechanism for work.

## Why This Pattern Matters
In cross-functional processes (onboarding, feature deployments, incident triage), generating one narrative document shifts the burden of slicing tasks up onto human project managers. By rendering the final output as a role-partitioned checklist, the document inherently coordinates downstream execution without requiring a secondary breakdown step.

## Diagnostic Questions
- Does the resulting artifact govern an ongoing workflow spanning multiple departments or organizational roles?
- Do different parties need to execute distinct actions sequenced in a specific chronological order?
- Is there a likelihood of "bystander effect" where tasks drop because ownership across teams is ambiguous?

## Core Mechanics
1. **Explicit Actor Headers / Columns:** Label every actionable section, phase, or table row with the exact organizational role responsible for its execution. No task should lack an actor binding.
2. **Action-Forced Formatting:** Sections must use checkboxes (`[ ]`), `Requested/Granted` columns, or explicit status tracking semantics, reinforcing that the section requires action, not just passive reading.
3. **Chronological Scope Matching:** Structure the workflow sequentially over time, aligning the sections with the temporal window in which the actors must operate.

## Implementation Standard

```markdown
# Process Manifest: [Event Name]

### Pre-Flight Clearance (T-Minus 24H)
- [ ] Ensure infrastructure is provisioned...      ← [IT/DevOps]
- [ ] Lock the deployment branch...                ← [Release Manager]
- [ ] Send advisory notification to internal...    ← [Communications]

### Day 0 Execution
| Time  | Sequence Activity | Owner          | Status |
|-------|-------------------|----------------|--------|
| 09:00 | Flip DB clusters  | [Database Eng] | [ ]    |
| 10:15 | Roll instances    | [DevOps]       | [ ]    |

### Post-Flight Verification
| System / Tool | Verifier Role | Verification Status |
|---------------|---------------|---------------------|
| Payment API   | [QA Lead]     | Pending...          |
| Telemetry     | [SRE]         | Pending...          |
```

## Anti-Patterns Avoided
- **Bystander Effect Generation:** Generative blobs of best-practice text ("The system should be monitored during deployment") where no individual human knows if they are actually the one supposed to perform the action.
- **Narrative Over-Explanation:** Producing dense readable paragraphs describing an operational workflow instead of providing a stark, checklist-oriented orchestration manifest.


## See Also

- [[multi-actor-operational-coordination-manifest]]
- [[multi-actor-operational-coordination-manifest]]
- [[multi-actor-operational-coordination-manifest]]
- [[multi-actor-operational-coordination-manifest]]
- [[multi-actor-operational-coordination-manifest]]
- [[multi-actor-operational-coordination-manifest]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/multi-actor-operational-coordination-manifest.md`
- **Indexed:** 2026-04-17T06:42:10.010976+00:00
