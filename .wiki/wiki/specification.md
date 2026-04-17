---
concept: specification
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/link-checker-agent/references/specification.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.109092+00:00
cluster: field
content_hash: 02e60dbc8c1493ed
---

# Specification

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

Source: [agentskills.io](https://agentskills.io/specification.md)
Built with [Mintlify](https://mintlify.com)

---

# Specification

The complete format specification for Agent Skills.

## Directory structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## `SKILL.md` format

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Frontmatter

| Field           | Required | Constraints                                                                                                       |
| --------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `name`          | Yes      | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen.             |
| `description`   | Yes      | Max 1024 characters. Non-empty. Describes what the skill does and when to use it.                                 |
| `license`       | No       | License name or reference to a bundled license file.                                                              |
| `compatibility` | No       | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata`      | No       | Arbitrary key-value mapping for additional metadata.                                                              |
| `allowed-tools` | No       | Space-delimited list of pre-approved tools the skill may use. (Experimental)                                      |

#### `name` field

The required `name` field:

* Must be 1-64 characters
* May only contain unicode lowercase alphanumeric characters (`a-z`) and hyphens (`-`)
* Must not start or end with a hyphen (`-`)
* Must not contain consecutive hyphens (`--`)
* Must match the parent directory name

#### `description` field

The required `description` field:

* Must be 1-1024 characters
* Should describe both what the skill does and when to use it
* Should include specific keywords that help agents identify relevant tasks

#### `license` field

The optional `license` field:

* Specifies the license applied to the skill
* We recommend keeping it short (either the name of a license or the name of a bundled license file)

#### `compatibility` field

The optional `compatibility` field:

* Must be 1-500 characters if provided
* Should only be included if your skill has specific environment requirements
* Can indicate intended product, required system packages, network access needs, etc.

#### `metadata` field

The optional `metadata` field:

* A map from string keys to string values
* Clients can use this to store additional properties not defined by the Agent Skills spec
* We recommend making your key names reasonably unique to avoid accidental conflicts

#### `allowed-tools` field

The optional `allowed-tools` field:

* A space-delimited list of tools that are pre-approved to run
* Experimental. Support for this field may vary between agent implementations

### Body content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

### `scripts/`
Contains executable code that agents can run. Scripts should:
* Be self-contained or clearly document dependencies
* Include helpful error messages
* Handle edge cases gracefully

### `references/`
Contains additional documentation that agents can read when needed:
* `REFERENCE.md` - Detailed technical reference
* `FORMS.md` - Form templates or structured data formats
* Domain-specific files (`finance.md`, `legal.md`, etc.)

### `assets/`
Contains static resource

*(content truncated)*

## See Also

- [[improvement-ledger-specification]]
- [[context-status-specification-contextstatusmd]]
- [[dynamic-specification-fetching]]
- [[dynamic-specification-fetching]]
- [[dynamic-specification-fetching]]
- [[dynamic-specification-fetching]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/link-checker-agent/references/specification.md`
- **Indexed:** 2026-04-17T06:42:10.109092+00:00
