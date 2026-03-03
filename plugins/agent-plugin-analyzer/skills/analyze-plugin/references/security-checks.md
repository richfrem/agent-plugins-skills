# Security Analysis Checks

Reference file for Phase 5 security analysis. These checks run FIRST (P0) before structural anti-pattern checks.

## Structural Anti-Patterns

| Anti-Pattern | Check | Severity |
|-------------|-------|----------|
| SKILL.md > 500 lines | Line count from Phase 1 | Error |
| Missing acceptance criteria | No `references/acceptance-criteria.md` | Warning |
| Missing progressive disclosure | No `references/` directory | Warning |
| Bash/PowerShell scripts | `.sh` or `.ps1` files in `scripts/` | Error |
| Hardcoded paths | Absolute paths instead of relative | Error |
| Missing README file tree | No `├──` / `└──` in README | Warning |
| Unqualified tool names | MCP tools without `ServerName:` namespace | Error |
| Silent error handling | Scripts that swallow errors | Warning |
| Nested references | Reference files that link to other reference files | Warning |
| Skill scope creep | Single SKILL.md with >3 distinct workflows | Warning |
| Missing CONNECTORS.md | Plugin uses MCP tools but no connector abstraction | Warning |

## Security Checks (P0 — Check These First)

| Security Check | What to Look For | Severity |
|---------------|-------------------|----------|
| Unauthorized network calls | `curl`, `requests`, `urllib`, `fetch` in scripts | Critical |
| Prompt injection surfaces | User-controlled content injected into prompts without sanitization | Critical |
| Overly permissive tool lists | Sub-agents with unrestricted tool access | Critical |
| Hardcoded credentials | API keys, tokens, passwords in any file | Critical |
| Data exfiltration risk | Discovery phases that gather sensitive data without boundaries | Error |
| Undeclared side effects | Hooks or scripts that modify files outside their scope | Error |
| Undeclared dependencies | Plugin relies on other plugins/MCP servers not documented | Warning |

## LLM-Native Attack Vectors

| Vector | Description | Severity |
|--------|-------------|----------|
| Skill impersonation | A skill with a `description` designed to shadow/override a legitimate skill | Critical |
| Context window poisoning | Enormous reference files designed to crowd out other skills | Error |
| Instruction injection via references | Hidden instructions in HTML comments or zero-width characters in .md files | Critical |
| Dependency confusion | Declaring a dependency on a non-existent plugin to trigger malicious fetch | Error |
| Write-then-read attacks | Catalog/reference content that alters agent behavior when re-read | Error |
| Pattern catalog poisoning | Malicious plugin analysis injecting harmful patterns into the living catalog | Critical |

## Contextual Severity Rules

Severity is **contextual** — adjust based on plugin complexity:

| Plugin Type | Example Adjustments |
|------------|-------------------|
| Simple utility (L1-L2) | Missing CONNECTORS.md → Info (not needed) |
| Integration plugin (L3-L4) | Missing CONNECTORS.md → Error (required for portability) |
| Meta-plugin (L5) | Any security finding → escalate one severity level |
| User-facing guided skill | Missing confirmation gates → Warning |
| Autonomous batch skill | Missing confirmation gates → Info (not applicable) |

## Anti-Gaming Safeguards

> **Goodhart's Warning**: When a measure becomes a target, it ceases to be a good measure.

To prevent analyzer-shaped plugins (optimized for scoring rather than quality):
- Do NOT reward pattern density. A plugin that uses 15 patterns is not inherently better than one using 5.
- Flag "checklist-stuffing" — empty acceptance criteria files, placeholder CONNECTORS.md with no real mappings.
- Consider qualitative override: if the LLM detects a high-scoring plugin that "feels wrong," flag it for human review.
- Include a "justified deviation" allowance — plugins that deliberately break a pattern for good reason should be rewarded, not penalized. Specifically, if a plugin orchestrator requires `subprocess` or `urllib/requests.get` to download fundamental tool assets or trigger CI environments, check if the plugin includes a `security_override.json` stating this boundary case. If the override exists and matches the code logically, do NOT fail the plugin on P0 Network/Subprocess violations.
