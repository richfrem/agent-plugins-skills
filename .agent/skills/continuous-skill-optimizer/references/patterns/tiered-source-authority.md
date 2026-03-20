# Tiered Source Authority with Propagated Confidence

**Use Case:** Research, analysis, or synthesis skills where the agent must evaluate the trustworthiness of evidence before presenting an answer.

## The Core Mechanic

This is an evolution of Priority-Ordered Source Scanning. It doesn't just dictate search order; it mathematically links the **quality of the source** to the **confidence of the final answer**.

### Implementation Standard

1. **Define the Tiers in SKILL.md:**
   ```markdown
   | Tier | Source Category | Output Confidence Celing |
   |------|----------------|--------------------------|
   | T1   | Official internal docs, product specs | High |
   | T2   | CRM records, support tickets | Medium-High |
   | T3   | Chat history, email | Medium |
   | T4   | Web search, forums | Low-Medium |
   | T5   | Inferred reasoning | Low |
   ```

2. **Enforce the Constraint:**
   Instruct the agent: "Your final answer's confidence level can NEVER be higher than the Tier of the primary source you used to derive it. If you only have T3 sources, your maximum confidence is Medium."

3. **Output Schema:**
   ```markdown
   **Answer:** [Direct answer]
   **Confidence:** [High/Medium/Low]
   **Primary Source Tier:** [T1/T2/T3/T4/T5]
   ```
