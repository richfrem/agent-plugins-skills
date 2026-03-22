# Category-Calibrated Benchmark Anchoring

**Status:** Draft
**Pattern Type:** Structural Constraint
**Applicable Domain:** Growth, Marketing, Data Science, Sales, FinOps

## Executive Summary
External industry-standard benchmarks are embedded directly into the skill as **evaluation reference constants**. When the agent classifies a metric's status, it does not exercise subjective judgment—it compares the user-supplied value against the embedded reference value for that category. The benchmark table acts as a lookup table that anchors all status classifications to external, category-specific norms rather than the agent's internal assessment.

## The Abstract Problem
When asked to evaluate metrics (e.g., "Is a 20% open rate good?"), an agent will draw on its general training knowledge. This knowledge may be outdated, generalized across all industries, or context-inappropriate. This leads to subjective, non-deterministic performance evaluations that fluctuate between "excellent" and "needs improvement" depending on the LLM's mood or internal priors.

## The Target
Any workflow that evaluates, audits, or critiques numeric metrics and assigns a qualitative status (On Track, At Risk, High Performer) to those metrics.

## The Core Mechanic
Instead of asking the LLM to interpret a number, the skill provides a hardcoded tabular lookup matrix of industry benchmarks. The agent's task shifts from *subjective evaluation* to *matrix lookup and comparison*.
Example: "22% open rate for a lead nurture sequence falls within the 20-30% benchmark range in the reference table → status: On Track."

## Distinction from Similar Patterns
- **Embedded Deterministic Scoring Formula**: EDSF hardcodes a *mathematical formula* to rank items the *agent itself generates*. CCBA embeds *external industry reference values* to classify *user-supplied metrics*. One is internal scoring; the other is external calibration.
- **Population-Normative Distribution Constraint**: PNDC constrains statistical distributions of an *organization's own outputs* at macro scale (like a budget curve). CCBA embeds *external industry baselines* as per-category reference points for evaluating individual metric values.
- **Quantification Enforcement**: QE forces the agent to cite numbers instead of prose. CCBA pre-loads the reference numbers the agent compares *against*—it operates one layer upstream of QE.

## Implementation Standard

```markdown
## Reference Benchmarks

> Used by the agent to anchor all status classifications. Do not generate status labels
> from subjective judgment—compare the user-supplied value against the appropriate 
> category column below.

| Metric | [Category A] | [Category B] | [Category C] |
|--------|-------------|-------------|-------------|
| [Metric 1] | [Range] | [Range] | [Range] |
| [Metric 2] | [Range] | [Range] | [Range] |

**Adjustment rule:** If the user has provided industry- or audience-specific context, 
note when benchmarks may not apply and state the adjustment rationale.

**Status classification rule:** Only three labels are permitted: `On Track`, `At Risk`, 
`Off Track`. The label is determined by the metric's position relative to the benchmark 
range—not by the agent's assessment of what "good" means.
```

## Anti-Patterns
1. **The Generative Evaluator:** Allowing the agent to decide what makes a "high" or "low" score without providing the reference matrix.
2. **The Uncalibrated Benchmark:** Providing a single average metric without segmenting by Category (e.g., providing one "Email Open Rate" benchmark instead of segmenting by "Onboarding", "Nurture", "Win-back").
3. **The Silent Judgment:** Emitting the Status label without explicitly stating the Benchmark value it was anchored against in the output.
