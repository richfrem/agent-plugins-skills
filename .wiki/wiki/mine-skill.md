---
concept: mine-skill
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-plugin-analyzer_mine-skill.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.316417+00:00
cluster: analysis
content_hash: 3cbdd86a6b0d4a40
---

# Mine Skill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
user-invocable: true
argument-hint: "[path-to-skill-directory]"
---

# Mine Skill

Run the targeted analysis pipeline on a single Agent Skill. This allows for focused extraction and synthesis from isolated directories without processing an entire plugin.

## What This Command Does

1. **Inventory** — Enumerate the files within the specific skill directory.
2. **Analyze** — Run the `analyze-plugin` skill, focused purely on this component.
3. **Extract** — Pull design patterns and architecture choices from the skill.
4. **Synthesize** — Generate improvement recommendations using `synthesize-learnings`.

## Usage

```
/mine-skill <path-to-skill-directory>
```

### Examples

```
# Analyze a specific skill within a knowledge plugin
/mine-skill claude-knowledgework-plugins/sales/skills/call-prep

# Analyze one of our own core skills
/mine-skill plugins\ reference/agent-scaffolders/skills/create-plugin
```

## Execution Flow

1. **Invoke Analysis**: The system triggers `analyze-plugin` operating in Single Skill Mode on the provided `$ARGUMENTS`.
2. **Execute Inventory**: `scripts/inventory_plugin.py` runs against the skill path.
3. **Pattern Matching**: Checks against `references/pattern-catalog.md` and detects anti-patterns.
4. **Knowledge Synthesis**: `synthesize-learnings` is invoked to map discovered patterns back to our core `agent-scaffolders` and `agent-skill-open-specifications`.
5. **Output**: Renders the analysis inline, highlighting the novel techniques implemented in the isolated skill.


## See Also

- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-optimization-guide-karpathy-loop]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-continuous-improvement-red-green-refactor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-plugin-analyzer_mine-skill.md`
- **Indexed:** 2026-04-17T06:42:10.316417+00:00
