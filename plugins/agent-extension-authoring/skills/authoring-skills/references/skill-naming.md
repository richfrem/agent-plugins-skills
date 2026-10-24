# Skill naming

How to name a skill and write the description that routes to it. The name and description are the only parts of a skill loaded into the system prompt at startup, so they decide whether Claude finds and invokes the skill.

## Contents

- [The name field](#the-name-field)
- [Style: gerund first](#style-gerund-first)
- [Words to avoid](#words-to-avoid)
- [The description field](#the-description-field)
- [Quick reference](#quick-reference)
- [Renaming or merging skills](#renaming-or-merging-skills)

## The name field

| Rule | Detail |
| --- | --- |
| Characters | Lowercase letters, numbers and hyphens only (kebab-case) |
| Length | 64 characters or fewer |
| Directory | The skill folder name equals the `name` value exactly |
| Reserved words | The name must not contain `claude` or `anthropic` (the platform rejects them) |
| Markup | No XML tags, spaces, underscores or capitals |

Write `processing-pdfs`, never `processing_pdfs`, `Processing PDFs` or `processingPdfs`.

## Style: gerund first

Preferred: verb plus `-ing`, which signals an active capability: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`, `testing-code`.

Acceptable: a noun phrase (`pdf-processing`) or a direct action verb (`process-pdfs`).

Gerunds are a strong preference, not a hard rule. `audit_skill.py` reports non-gerund names as warnings so existing routing identities survive. Pick one pattern and use it across a plugin; renaming kept skills belongs in the same change.

## Words to avoid

Vague or generic words carry no routing signal: `helper`, `utils`, `tools`, `files`, `data`, `misc`. Name the job instead of the container.

Avoid a numbered or role-only suffix such as `-v2` or `-agent` unless the role is the point.

## The description field

The description is what Claude matches a request against.

- **Third person.** Write "Processes Excel files and generates reports", not "I can help you process Excel files" and not "Use this to...".
- **Say what and when.** Name the capability and the concrete contexts or phrases that should trigger it.
- **Add exclusions where a sibling skill is close.** For example: "Not for X (use `other-skill`)".
- **1024 characters or fewer.** Put trigger phrases early, because long descriptions are truncated in listings.
- **No XML tags.**

An intake gateway that must fire on every non-trivial task needs a description that opens with that broad condition. Do not dilute it by merging unrelated triggers into the same skill.

## Quick reference

| Category | Do | Do not |
| --- | --- | --- |
| Casing | kebab-case | camelCase, snake_case, spaces |
| Grammar | `processing-pdfs` | `helper`, `utils`, `data` |
| Brand words | Functional, descriptive names | Names containing `anthropic` or `claude` |
| Description tone | Third-person, objective | "I can help...", "Use this..." |
| Folder | Same as `name` | Folder and `name` that differ |

## Renaming or merging skills

A skill name is an identifier that other files hard-code. Before renaming, merging or retiring one:

1. Search the repository for the old name, including `AGENTS.md`, rules, hooks, agent definitions, YAML hints, tests and other plugins.
2. Record each hit in the migration inventory as `REFERENCE_UPDATED` or `HISTORICAL_LEFT`, and each retired name as `SKILL_RETIRED` with its replacement.
3. Update the registries: plugin manifests, `apm.yml`, the root `__init__.py` and the retention guide.
4. Re-run `scripts/audit_skill.py` on the new skill. It checks name format, folder match, reserved words and description voice.
5. Remove the retired skill folders from deployed targets by exact name after `apm install`.

Sources: Anthropic's Agent Skills best practices (see [anthropic-skill-authoring-best-practices.md](anthropic-skill-authoring-best-practices.md)) and this repository's [contract](skill-authoring-contract.json).
