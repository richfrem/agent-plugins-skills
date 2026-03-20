# Acceptance Criteria

## AC-01: Correct ORP Positioning

**Given** a word of any length,
**When** `calculate_orp()` is called,
**Then** the returned index must equal `ceil((len(clean_word) - 1) / 4)`, clamped to `[0, len-1]`.

**Test cases:**
| Word | Clean | ORP |
|---|---|---|
| "Hello" | "Hello" | 1 |
| "speed" | "speed" | 1 |
| "reading" | "reading" | 2 |
| "extraordinary" | "extraordinary" | 3 |
| "a" | "a" | 0 |

---

## AC-02: WPM Delay Accuracy

**Given** WPM=300,
**When** a plain word (no punctuation) is processed,
**Then** `delay_ms` must equal `round(60000 / 300)` = 200ms.

**Given** a sentence-ending word (e.g., "done."),
**Then** `delay_ms` must equal 200 * 2.0 = 400ms.

---

## AC-03: File Format Support

**Given** an input file with extension `.txt`, `.md`, `.pdf`, or `.docx`,
**When** `./parse_document.py` is called,
**Then** it must return a non-empty word list without crashing.

---

## AC-04: Output Schema Compliance

**Given** any valid input and WPM setting,
**When** `././orp_engine.py` produces output,
**Then** every entry in the JSON array must contain exactly the fields: `w`, `orp`, `delay_ms`, `is_sentence_end`, `is_para_end`.

---

## AC-05: WPM Range Enforcement

**Given** WPM value outside 100-1000,
**When** `././orp_engine.py` is invoked,
**Then** it must exit with a non-zero status and an informative error message.