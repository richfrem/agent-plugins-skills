# Memory Management Plugin 🧠

Tiered memory system for cognitive continuity in consumer frameworks. Manages hot cache (`cognitive_primer.md`, `agent_boot_digest.md`) and deep storage (`LEARNING/`, `ADRs/`, protocols). 

## Use Cases
Use this plugin when:
1. Starting a session and loading context
2. Deciding what to remember vs forget
3. Promoting/demoting knowledge between tiers
4. The user says "remember this" or asks about project history
5. Managing the `learning_package_snapshot.md` hologram

## Core Capabilities
| Skill | Purpose |
| :--- | :--- |
| **memory-management** | The primary skill for ingesting and retrieving long-term context. |

## Structure
- `skills/`: Contains the agent skills instructions (`SKILL.md`) and executable scripts.
- `.claude-plugin/`: Plugin manifest and configuration.
