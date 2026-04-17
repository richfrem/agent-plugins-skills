---
concept: command-template-spec-kittyreview-documentation-mission
source: plugin-code
source_file: spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/review.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.331698+00:00
cluster: review
content_hash: c45a668b889f6f84
---

# Command Template: /spec-kitty.review (Documentation Mission)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Review documentation work packages for Divio compliance and quality.
---

# Command Template: /spec-kitty.review (Documentation Mission)

**Phase**: Validate
**Purpose**: Review documentation for Divio compliance, accessibility, completeness, and quality.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Review Philosophy

Documentation review is NOT code review:
- **Not about correctness** (code is about bugs) but **usability** (can readers accomplish their goals?)
- **Not about style** but **accessibility** (can everyone use these docs?)
- **Not about completeness** (covering every edge case) but **usefulness** (solving real problems)
- **Not pass/fail** but **continuous improvement**

---

## Review Checklist

### 1. Divio Type Compliance

For each documentation file, verify it follows principles for its declared type:

**Tutorial Review**:
- [ ] Learning-oriented (teaches by doing, not explaining)?
- [ ] Step-by-step progression with clear sequence?
- [ ] Each step shows immediate, visible result?
- [ ] Minimal explanations (links to explanation docs instead)?
- [ ] Assumes beginner level (no unexplained prerequisites)?
- [ ] Reliable (will work for all users following instructions)?
- [ ] Achieves concrete outcome (learner can do something new)?

**How-To Review**:
- [ ] Goal-oriented (solves specific problem)?
- [ ] Assumes experienced user (not teaching basics)?
- [ ] Practical steps, minimal explanation?
- [ ] Flexible (readers can adapt to their situation)?
- [ ] Includes common variations?
- [ ] Links to reference for details, explanation for "why"?
- [ ] Title starts with "How to..."?

**Reference Review**:
- [ ] Information-oriented (describes what exists)?
- [ ] Complete (all APIs/options/commands documented)?
- [ ] Consistent format (same structure for similar items)?
- [ ] Accurate (matches actual behavior)?
- [ ] Includes usage examples (not just descriptions)?
- [ ] Structured around code organization?
- [ ] Factual tone (no opinions or recommendations)?

**Explanation Review**:
- [ ] Understanding-oriented (clarifies concepts)?
- [ ] Not instructional (not teaching how-to-do)?
- [ ] Discusses concepts, design decisions, trade-offs?
- [ ] Compares with alternatives fairly?
- [ ] Makes connections between ideas?
- [ ] Provides context and background?
- [ ] Identifies limitations and when (not) to use?

**If type is wrong or mixed**:
- Return with feedback: "This is classified as {type} but reads like {actual_type}. Either reclassify or rewrite to match {type} principles."

---

### 2. Accessibility Review

**Heading Hierarchy**:
- [ ] One H1 per document (the title)
- [ ] H2s for major sections
- [ ] H3s for subsections under H2s
- [ ] No skipped levels (H1 → H3 is wrong)
- [ ] Headings are descriptive (not "Introduction", "Section 2")

**Images**:
- [ ] All images have alt text
- [ ] Alt text describes what image shows (not "image" or "screenshot")
- [ ] Decorative images have empty alt text (`![]()`)
- [ ] Complex diagrams have longer descriptions

**Language**:
- [ ] Clear, plain language (technical terms defined)
- [ ] Active voice ("run the command" not "the command should be run")
- [ ] Present tense ("returns" not "will return")
- [ ] Short sentences (15-20 words max)
- [ ] Short paragraphs (3-5 sentences)

**Links**:
- [ ] Link text is descriptive ("see the installation guide" not "click here")
- [ ] Links are not bare URLs (use markdown links)
- [ ] No broken links (test all links)

**Code Blocks**:
- [ ] All code blocks have language tags for syntax highlighting
- [ ] Expected output is shown (not just commands)
- [ ] Code examples actually work (tested)

**Tables**:
- [ ] Tables have headers
- [ ] Headers use `|---|` syntax
- [ ] Tables are not too wide (wrap if needed)

**Lists**:
- [ ] Proper markdown lists (not paragraphs with commas)
- [ ] Consistent bullet style
- [ ] Items are parallel in structure

**If accessibi

*(content truncated)*

## See Also

- [[command-template-spec-kittyimplement-documentation-mission]]
- [[command-template-spec-kittyplan-documentation-mission]]
- [[command-template-spec-kittyspecify-documentation-mission]]
- [[command-template-spec-kittytasks-documentation-mission]]
- [[command-template-spec-kittytasks-research-mission]]
- [[command-template-spec-kittytasks-research-mission]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/assets/templates/.kittify/missions/documentation/command-templates/review.md`
- **Indexed:** 2026-04-17T06:42:10.331698+00:00
