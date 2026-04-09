## 0018-cherry-pick-skill-structure-cleanups.md

**Status:** Complete  
**Priority:** High (Pre-requisite for `0017`)  
**Context:** This task outlines specific YAML frontmatter and structural cleanups proposed by an external PR that successfully improved the `quality_score` of five local skills by an average of 70%. It represents the "gold" to cherry-pick, ignoring external GitHub CI actions. 

---

## The Core Issue Addressed
Historically, `SKILL.md` files placed `<example>` blocks or non-YAML comments directly inside the `description:` YAML block or above the opening `---` line. 
- XML-style tags inside YAML definitions confuse parsers and inflate the token payload sent directly to orchestrator routing agents. 
- Large instructional/troubleshooting text inside the `SKILL.md` body obscures the tactical "how-to-execute" rules.

---

## 🎯 Implementation Priority & Prioritization Matrix

The 5 skills are ranked by **Implementation Order** based on their Criticality (impact on system stability/routing) and Feasibility (ease of implementation).

### 1. `subagent-driven-prototyping` (Syntax Failure) **[✓ COMPLETE]**
* **Criticality:** **HIGH** (Currently causes strict YAML parsers to fail entirely, hiding the skill from orchestrators)
* **Feasibility:** **VERY HIGH** (< 1 minute)
* **Issue:** A comment (`# Architectural patterns adapted from obra/superpowers...`) was placed *above* the opening `---` line. 
* **Recommendation:** **Fix immediately.** Move the attribution comment below the `---` into the main Markdown body as a blockquote. Minor polish of the trigger phrases in the description.

### 2. `os-eval-runner` (Task `0017` Blocker) **[✓ COMPLETE]**
* **Criticality:** **HIGH** (Required foundational cleanup before injecting the massive V2 "Drill Sergeant" redesign) 
* **Feasibility:** **MEDIUM** (Requires creating two new files and moving text limits)
* **Issue:** Token bloat. Too much non-actionable setup and troubleshooting text burying the core execution logic.
* **Recommendation:** **Implement as step 1 of Task `0017`.** 
  - Move `<example>` tags below the frontmatter `---`. 
  - Extract the `## The Lab-Space Protocol` section into a new `references/lab-space-protocol.md` file. 
  - Extract the `## Troubleshooting` section into a new `references/troubleshooting.md` file.

### 3. `create-skill` (Routing Conflict Risk) **[✓ COMPLETE]**
* **Criticality:** **MEDIUM** (Semantic ambiguity can cause the orchestrator to route here instead of `os-skill-improvement`)
* **Feasibility:** **HIGH** (Fast edit)
* **Issue:** Bloated frontmatter and misleading trigger assumptions.
* **Recommendation:** 
  - Move `<example>` blocks into the main Markdown body.
  - ~~Remove `argument-hint:` and `allowed-tools:`.~~ *(Rejecting this PR proposal: these are critical binding keys for Antigravity/Claude Code)*
  - Rewrite the description to explicitly differentiate its behavior from the `os-skill-improvement` skill so agents don't route incorrectly.

### 4. `os-clean-locks` (Explicit Keyword Visibility) **[✓ COMPLETE]**
* **Criticality:** **MEDIUM** (Lack of full context in description forces reliance on heuristics)
* **Feasibility:** **HIGH** (Fast edit)
* **Issue:** Bloated frontmatter and lack of dense description words.
* **Recommendation:** 
  - Extract `<example>` and `<commentary>` tags to the Markdown body.
  - Embed explicit trigger keywords naturally into the `description:` paragraph (`"/os-clean-locks"`, `"clear all locks"`, `"reset agent locks"`).

### 5. `os-eval-lab-setup` (General Hygiene) **[✓ COMPLETE]**
* **Criticality:** **LOW** (No active conflicts, just bloated)
* **Feasibility:** **HIGH** (Fast edit)
* **Issue:** Bloated frontmatter.
* **Recommendation:** 
  - Relocate `<example>` blocks into the main Markdown body.
  - ~~Remove unnecessary `argument-hint:` and `allowed-tools:` tags from the YAML block~~ *(Rejecting this: `allowed-tools:` is required)*, ensuring the orchestrator relies purely on semantic triggers in the `description:`.

---

## Action Plan
1. Fix the syntax error in `subagent-driven-prototyping` immediately to unbreak parsers.
2. Knock out the fast frontmatter cleanups for `#3`, `#4`, and `#5` in a single pass.
3. Keep `#2` (`os-eval-runner`) paired with the start of **Task `0017`**.
4. Evaluate the frontmatter `<example>` strategy repository-wide. If moving them into the Markdown body universally yields better routing accuracy, write an anti-pattern architectural rule to prevent storing XML examples inside YAML fields going forward.
