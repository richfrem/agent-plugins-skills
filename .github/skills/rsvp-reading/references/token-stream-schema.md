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
