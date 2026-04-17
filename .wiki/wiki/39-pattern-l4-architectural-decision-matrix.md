---
concept: 39-pattern-l4-architectural-decision-matrix
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/l5-red-team-auditor/pattern-decision-matrix.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.103036+00:00
cluster: file
content_hash: 7b5f7d5037c3fec7
---

# 39-Pattern L4 Architectural Decision Matrix

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# 39-Pattern L4 Architectural Decision Matrix
> **Standard Last Validated:** 2026-03-03

A reference for deciding when and how to incorporate advanced L4 architectural and state management patterns into skills. Used by `create-skill` and `create-plugin` during the design phase to selectively load deep context only when needed.

---

## Pattern Decision Tree

Not every skill needs complex architectural patterns. Use this tree during the discovery phase to determine which patterns to inject.

**CRITICAL RULE**: Do not explain the theory of these patterns to the user. Ask the diagnostic question. If the user answers YES, **MUST** load the corresponding markdown definition from `~~l4-pattern-catalog` (see ./CONNECTORS.md).

### Category 1: Input and Routing
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Does the skill interact with external systems (Jira, Figma, etc.)? | **Connector Placeholders** | `connector-placeholders.md` |
| Should the skill work with limited functionality without tools connected? | **Dual-Mode Degradation** | `dual-mode-degradation.md` |
| Does the skill take complex text, URLs, or files as input context? | **Multi-Modal Routing** | `multi-modal-routing.md` |
| Does the user report surface symptoms that need root-cause diagnosis? | **Anti-Symptom Triage** | `anti-symptom-triage.md` |
| Does the command group several sub-operations that have different outputs? | **Sub-Action Multiplexing** | `sub-action-multiplexing.md` |
| Does the command require user input upstream where asking questions mid-flight hurts UX? | **Pre-Execution Input Manifest** | `pre-execution-input-manifest.md` |
| Does the skill share overlapping keywords with generic tools, potentially causing discoverability issues? | **Multi-Variant Trigger Optimizer** | `multi-variant-trigger-optimizer.md` |
| Does the skill inherently struggle with undertriggering due to generic namespace intent vs actual semantic queries? | **Trigger Description Optimization Loop** | `../scripts/improve_description.py` (Source: Anthropic `skill-creator`) |

### Category 2: Execution and Safety
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Is there a mix of low-risk and high-risk actions in this domain? | **Graduated Autonomy** | `graduated-autonomy.md` |
| Can the workflow trigger potentially dangerous or unrecoverable actions? | **Escalation Taxonomy** | `escalation-taxonomy.md` |
| Are there multiple tools, where failure of one shouldn't crash the workflow? | **Conditional Step Inclusion** | `conditional-step-inclusion.md` |
| Does the agent query multiple systems of differing truthfulness? | **Priority-Ordered Scanning** | `priority-ordered-scanning.md` |
| Does the command analyze or synthesize data across multiple systems? | **Multi-Source Synthesis** | `multi-source-synthesis.md` |
| Is this a meta-skill designed to bootstrap or append to other skills? | **Dual-Mode Meta-Skill** | `dual-mode-meta-skill.md` |
| Are we executing an irreversible workflow where failure under stress is fatal? | **Pre-Committed Rollback Contract** | `pre-committed-rollback-contract.md` |
| Is the sequence of execution critical, but prone to human error? | **Pre-Execution Workflow Commitment Diagram** | `pre-execution-workflow-commitment-diagram.md` |
| Does the resulting artifact govern an ongoing workflow spanning multiple organizational roles? | **Multi-Actor Operational Coordination Manifest** | `multi-actor-operational-coordination-manifest.md` |
| Will the agent's natural sycophancy (agreeableness) ruin the analysis? | **Adversarial Objectivity Constraint** | `adversarial-objectivity-constraint.md` |
| Is the command modifying constrained additive resources (dashboards, capacity)? | **Zero-Sum Addition Gate** | `zero-sum-addition-gate.md` |
| Is there a minimum compliance safety standard that must never be bypassed regardless of the execution path or tool availability

*(content truncated)*

## See Also

- [[pattern-decision-matrix]]
- [[memory-promotion-decision-guide]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[agent-loops-pattern-guide]]
- [[pattern-catalog]]
- [[pattern-action-forcing-output-with-deadline-attribution]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/l5-red-team-auditor/pattern-decision-matrix.md`
- **Indexed:** 2026-04-17T06:42:10.103036+00:00
