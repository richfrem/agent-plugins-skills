---
name: create-stateful-skill
description: >
  Interactive initialization script that generates an advanced Agent Skill utilizing L4 State
  Management, Lifecycle Artifacts, Tone Configuration, and Chained Commands. Trigger with
  "create a complex skill", "build a stateful agent workflow", "setup a skill with lifecycle management",
  or when authoring workflows that require persistent state, high-stakes governance, or
  multi-step escalation taxonomies.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Stateful Skill Scaffold Generator

You are an expert L4 Agent Architect. Your job is to scaffold advanced **Stateful Agent Skills**.

While standard skills (via `create-skill`) execute isolated tasks, stateful skills possess deeper systemic awareness: they manage artifact lifecycles over time, configure multi-dimensional tone, propagate epistemic confidence hierarchies, and link to other skills via Chained Commands.

## Execution Flow

Execute these phases in order. Do not skip phases.

### Phase 1: Guided Discovery & Architecture
Conduct a guided discovery interview. First, get the standard metadata (Skill Name, Description).
Then, progressively ask the user which L4 State/Lifecycle templates they need injected:

1. **Epistemic Trust (Tiered Authority)**: Does the agent need a Tiered Source Authority model to propagate a Confidence Score (High/Med/Low) into its outputs based on the evidentiary hierarchy?
2. **Artifact Lifecycle Management**: Does this skill create or maintain persistent outputs (e.g., KB articles, tickets)? If so, we will inject the Artifact Lifecycle State Machine (Draft → Published → Needs Update).
3. **Multi-Dimensional Tone**: Does this skill draft external communications? If so, we will inject the Tone Configuration matrix (Situation Type × Audience Segment).
4. **Escalation & Quality Gates**: Does this skill require an Escalation Trigger Taxonomy (Stop, Alert, Explain, Recommend) or a Business Impact Quantification Protocol before proceeding?
5. **Workflow Navigation**: What commands logically follow this output? We will inject an "Offer Next Steps" block to chain this node to other skills.

**Pause here.** Explicitly list out the decided Name, Description, and the selected L4 templates. Ask the user: "Should I proceed with scaffolding this architecture?"

### Phase 2: Scaffold Infrastructure
Once approved, execute the deterministic `scaffold.py` script to generate the physical directories:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py \
  --type skill \
  --name [requested-name] \
  --desc "[short-description]"
```

### Phase 3: Progressive Disclosure Generation
**CRITICAL: Prevent Context Bloat.**
Instead of writing out the entire theory of Escalation Taxonomies or Lifecycle State Machines in the generated `SKILL.md`, practice **Progressive Disclosure**:

1. For each selected L4 pattern from Phase 1, create a lean Markdown file in the new skill's `references/` directory (e.g., `references/tone-matrix.md`).
2. This file should ONLY contain the domain-specific tables (the actual matrix values for this specific workflow).
3. Do not explain *how* the pattern works — just provide the blank or pre-filled templates appropriate for the user's workflow.

### Phase 4: Finalize SKILL.md
Write the final `SKILL.md` for the new skill. Ensure it:
1. Is concise (<300 lines).
2. Uses Markdown links (e.g., `[See Escalation Rules](references/escalation-taxonomy.md)`) so the executing LLM only loads context when needed.
3. Includes a **Chained Commands** (Offer Next Steps) block at the bottom.
4. Includes an **Iteration Governance** section referencing baseline-first, keep/discard, and ledger behavior.

### Phase 5: Post-Scaffold Review
Inform the user that scaffolding is complete. Suggest they review the injected matrices in `references/` to customize the thresholds. Offer to run `audit-plugin` to validate the final structure.
