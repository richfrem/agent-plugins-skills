---
concept: token-stream-schema
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/rsvp-reading/references/token-stream-schema.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.215790+00:00
cluster: word
content_hash: 86376e7b73a8f02e
---

# Token Stream Schema

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Token Stream Schema

Each entry in the RSVP token stream JSON array represents one word to display.

## Schema

```json
{
  "w": "string",
  "orp": 0,
  "delay_ms": 200,
  "is_sentence_end": false,
  "is_para_end": false
}
```

## Fields

| Field | Type | Description |
|---|---|---|
| `w` | `string` | The raw word token (may include punctuation) |
| `orp` | `integer` | 0-based character index of the Optimal Recognition Point |
| `delay_ms` | `integer` | Milliseconds to display this word before advancing |
| `is_sentence_end` | `boolean` | True if this word ends a sentence (.?!) |
| `is_para_end` | `boolean` | True if this is the last word before a paragraph break |

## ORP Formula

```
orp = ceil((len(clean_word) - 1) / 4)
```

Where `clean_word` is the word stripped of non-alphanumeric characters.

## Delay Multipliers

| Condition | Multiplier |
|---|---|
| Default | 1.0x |
| Ends sentence (.?!) | 2.0x |
| Clause pause (,;:) | 1.5x |
| Word > 10 chars | 1.2x |
| Paragraph break | 3.0x |

Base delay: `round(60000 / wpm)` ms


## See Also

- [[severity-stratified-output-schema-with-emoji-triage]]
- [[marketplace-schema-reference]]
- [[severity-stratified-output-schema-with-emoji-triage]]
- [[severity-stratified-output-schema-with-emoji-triage]]
- [[claude-code-settingsjson-schema-reference]]
- [[severity-stratified-output-schema-with-emoji-triage]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/rsvp-reading/references/token-stream-schema.md`
- **Indexed:** 2026-04-17T06:42:10.215790+00:00
