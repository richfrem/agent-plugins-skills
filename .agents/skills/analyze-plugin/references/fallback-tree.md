# Procedural Fallback Tree: Plugin Analyzer

## 1. inventory_plugin.py Fails or is Missing
If `skills/analyze-plugin/scripts/inventory_plugin.py` throws an error, returns empty, or is not executable:
- **Action**: Do not abort the analysis. Fall back to the manual directory walk described in Phase 1. Use standard file reading capabilities (`ls`, `find`, or tool-specific equivalents) to build the structured inventory checklist.

## 2. Plugin Contains No SKILL.md Files
If the target directory is just code scripts with no defined Agent Skills:
- **Action**: Adapt the framework. Note the lack of skills in Phase 2 (Structure Analysis). Skip the SKILL.md checks in Phase 3, and focus entirely on Script evaluation and Security Checks. Score the plugin heavily down on the Progressive Disclosure metric.

## 3. Ambiguous Anti-Pattern Detection
If code looks suspicious but doesn't perfectly match the definitions in `references/security-checks.md`:
- **Action**: Do not auto-fail the security check. Flag it as an "Unclassified Risk" in Phase 5 and explicitly recommend that the user manually review the code snippet, or route the file to the `audit-plugin-l5` Red Team subagent for deeper analysis.

## 4. Output Token Limit Reached
If analyzing a massive plugin causes the LLM to approach context/output limits before Phase 6:
- **Action**: Pause the generation. Issue a "Part 1 Complete" status, summarize findings so far, and instruct the user to type "Continue" to execute the remaining phases (Anti-Pattern & Scoring).
