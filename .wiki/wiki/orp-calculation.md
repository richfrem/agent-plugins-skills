---
concept: orp-calculation
source: plugin-code
source_file: rsvp-speed-reader/scripts/orp_engine.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.344034+00:00
cluster: word
content_hash: a03354d5ec69637b
---

# --- ORP Calculation ---

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/rsvp-speed-reader/scripts/orp_engine.py -->
#!/usr/bin/env python
"""
orp_engine.py
=============
Generates an RSVP token stream from a parsed word list.

Applies:
- ORP (Optimal Recognition Point): position index within the word where
  the eye naturally fixates. Formula from Spritz: ceil((len - 1) / 4)
- Delay calculation per word with punctuation multipliers
- Sentence-end and paragraph-end flags

Usage:
    python orp_engine.py --input <word_list.json> --wpm 300 --output <stream.json>
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path


# --- ORP Calculation ---

def calculate_orp(word: str) -> int:
    """
    Calculate the ORP index for a word using the Spritz formula.
    ORP = ceil((len(clean_word) - 1) / 4)
    Falls back leftward if the character at that index is non-alphanumeric.

    Args:
        word: Raw word token (may include punctuation)

    Returns:
        Integer index (0-based) of the ORP character position
    """
    clean = re.sub(r"[^a-zA-Z0-9]", "", word)
    if not clean:
        return 0

    length = len(clean)
    orp = math.ceil((length - 1) / 4)

    # Safety clamp
    orp = min(orp, length - 1)
    return orp


# --- Delay Calculation ---

SENTENCE_ENDS = frozenset(".?!")
CLAUSE_PAUSES = frozenset(",;:")

# Delay multipliers
MUL_SENTENCE_END = 2.0
MUL_CLAUSE_PAUSE = 1.5
MUL_LONG_WORD = 1.2   # for words > 10 chars
MUL_PARA_BREAK = 3.0


def calculate_delay(word: str, wpm: int, is_para_end: bool) -> int:
    """
    Calculate reading delay in milliseconds for a given word.

    Args:
        word: The raw word token
        wpm: Words per minute speed setting
        is_para_end: Whether this is the last word before a paragraph break

    Returns:
        Delay in milliseconds (integer)
    """
    base_ms = round(60000 / wpm)
    multiplier = 1.0

    if is_para_end:
        multiplier = MUL_PARA_BREAK
    elif word and word[-1] in SENTENCE_ENDS:
        multiplier = MUL_SENTENCE_END
    elif word and word[-1] in CLAUSE_PAUSES:
        multiplier = MUL_CLAUSE_PAUSE

    # Long word penalty (applied on top, capped so we don't stack with para break)
    clean = re.sub(r"[^a-zA-Z0-9]", "", word)
    if len(clean) > 10 and multiplier < MUL_LONG_WORD:
        multiplier = max(multiplier, MUL_LONG_WORD)

    return round(base_ms * multiplier)


# --- Sentence end detection ---

def is_sentence_end(word: str) -> bool:
    """Returns True if the word ends a sentence (ends with .  ?  !)."""
    stripped = word.rstrip('"\')')
    return bool(stripped) and stripped[-1] in SENTENCE_ENDS


# --- Stream Generator ---

def generate_stream(tokens: list[dict], wpm: int) -> list[dict]:
    """
    Generate the complete RSVP token stream.

    Args:
        tokens: List of {"word": str, "is_para_end": bool} dicts
        wpm: Target reading speed in words per minute

    Returns:
        List of RSVP token dicts matching the token-stream-schema
    """
    stream = []
    for token in tokens:
        word = token["word"]
        is_para_end = token.get("is_para_end", False)

        orp = calculate_orp(word)
        delay = calculate_delay(word, wpm, is_para_end)
        sent_end = is_sentence_end(word)

        stream.append({
            "w": word,
            "orp": orp,
            "delay_ms": delay,
            "is_sentence_end": sent_end,
            "is_para_end": is_para_end
        })

    return stream


# --- Main ---

def main() -> None:
    """Entry point: generates RSVP token stream from parsed word list."""
    parser = argparse.ArgumentParser(description="Generate RSVP token stream with ORP alignment.")
    parser.add_argument("--input", required=True, help="Path to parsed word list JSON (from parse_document.py)")
    parser.add_argument("--wpm", type=int, default=300, help="Words per minute (default: 300)")
    parser.add_argument("--output", required=True, help="Path for output token stream JSON")
    args = parser.parse_args()

    if args.wpm < 100 or args.wpm > 1000:
        print(f"Error: WPM 

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rsvp-reading/scripts/orp_engine.py -->
#!/usr/bin/env python3
"""
orp_engine.py
=============
Generates an RSVP token stream from a parsed word list.

Applies:
- ORP (Optimal Recognition Point): position index within the word where
  the eye naturally fixates. Formula from Spritz: ceil((len - 1) / 4)
- Delay calculation per word with punctuation multipliers
- Sentence-end and paragraph-end flags

Usage:
    python3 orp_engine.py --input <word_list.json> --wpm 300 --output <stream.json>
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path


# --- ORP Calculation ---

def calculate_orp(word: str) -> int:
    """
    Calculate the ORP index for a word using the Spritz formula.
    ORP = ceil((len(clean_word) - 1) / 4)
    Falls back leftward if the character at that index is non-alphanumeric.

    Args

*(combined content truncated)*

## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `rsvp-speed-reader/scripts/orp_engine.py`
- **Indexed:** 2026-04-27T05:21:04.344034+00:00
