#!/usr/bin/env python3
"""
test_orp_engine.py
==================
Quantitative benchmark for the calculate_orp function in orp_engine.py.

Imports calculate_orp from the lab copy of the skill and scores it against
a golden dataset of 50 edge-case words covering:
  - Hyphenated compounds
  - Words with leading/trailing quotes and parentheses
  - Extremely long words (>13 chars)
  - Alphanumeric mixes (abbreviations, model names)
  - Symbol-heavy tokens (URLs, email-like, code fragments)
  - Single-char and two-char words
  - Mixed-case and all-caps acronyms
  - Numbers and numeric strings
  - Empty / punctuation-only tokens

The Spritz ORP formula: orp = ceil((len(clean_word) - 1) / 4)
  where clean_word = re.sub(r"[^a-zA-Z0-9]", "", word)
  and the result is clamped to [0, len(clean_word)-1].

Output: a single float on stdout in [0.0, 1.0] (accuracy over 50 cases).
Exit code 0 always (errors in individual cases count as wrong answers).
"""

import sys
import math
import re
from pathlib import Path

# Allow importing from the lab copy of the skill
SCRIPT_DIR = Path(__file__).parent
SKILL_SCRIPTS = SCRIPT_DIR / "rsvp-speed-reader" / "skills" / "rsvp-reading" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))

try:
    from orp_engine import calculate_orp
except ImportError as e:
    print(f"0.0", flush=True)
    sys.exit(0)


def expected_orp(word: str) -> int:
    """Reference implementation of the Spritz ORP formula."""
    clean = re.sub(r"[^a-zA-Z0-9]", "", word)
    if not clean:
        return 0
    length = len(clean)
    orp = math.ceil((length - 1) / 4)
    return min(orp, length - 1)


# Golden dataset: (word, expected_orp_index)
# Each expected value is pre-computed from the reference formula.
GOLDEN_DATASET = [
    # --- Basic short words ---
    ("a",          expected_orp("a")),           # len=1 → 0
    ("it",         expected_orp("it")),          # len=2 → 0
    ("the",        expected_orp("the")),         # len=3 → 0
    ("word",       expected_orp("word")),        # len=4 → 0
    ("hello",      expected_orp("hello")),       # len=5 → 1
    ("simple",     expected_orp("simple")),      # len=6 → 1
    ("reading",    expected_orp("reading")),     # len=7 → 1
    ("sentence",   expected_orp("sentence")),    # len=8 → 1
    ("beautiful",  expected_orp("beautiful")),   # len=9 → 2
    ("algorithms", expected_orp("algorithms")), # len=10 → 2

    # --- Long words (>10 chars) ---
    ("understanding",      expected_orp("understanding")),       # len=13 → 3
    ("communication",      expected_orp("communication")),       # len=13 → 3
    ("extraordinarily",    expected_orp("extraordinarily")),     # len=16 → 3
    ("internationalization", expected_orp("internationalization")), # len=20 → 4
    ("pneumonoultramicroscopicsilicovolcanoconiosis",
     expected_orp("pneumonoultramicroscopicsilicovolcanoconiosis")),  # very long

    # --- Hyphenated compounds (hyphens stripped) ---
    ("state-of-the-art",   expected_orp("state-of-the-art")),   # clean=stateoftheart (12)
    ("well-known",         expected_orp("well-known")),         # clean=wellknown (9)
    ("high-performance",   expected_orp("high-performance")),   # clean=highperformance (15)
    ("twenty-first",       expected_orp("twenty-first")),       # clean=twentyfirst (11)
    ("up-to-date",         expected_orp("up-to-date")),         # clean=uptodate (8)

    # --- Leading/trailing punctuation (quotes, parentheses) ---
    ('"hello"',            expected_orp('"hello"')),            # clean=hello
    ("'world'",            expected_orp("'world'")),            # clean=world
    ("(example)",          expected_orp("(example)")),          # clean=example
    ('"extraordinary"',    expected_orp('"extraordinary"')),    # clean=extraordinary
    ("'it'",               expected_orp("'it'")),               # clean=it

    # --- Sentence-end punctuation ---
    ("done.",              expected_orp("done.")),              # clean=done
    ("really!",            expected_orp("really!")),            # clean=really
    ("right?",             expected_orp("right?")),             # clean=right
    ("wait...",            expected_orp("wait...")),            # clean=wait
    ("excellent!!!",       expected_orp("excellent!!!")),       # clean=excellent

    # --- Alphanumeric mixes ---
    ("COVID19",            expected_orp("COVID19")),            # clean=COVID19 (7)
    ("GPT4",               expected_orp("GPT4")),               # clean=GPT4 (4)
    ("R2D2",               expected_orp("R2D2")),               # clean=R2D2 (4)
    ("C3PO",               expected_orp("C3PO")),               # clean=C3PO (4)
    ("mp3",                expected_orp("mp3")),                # clean=mp3 (3)
    ("v2.0",               expected_orp("v2.0")),               # clean=v20 (3)
    ("H2O",                expected_orp("H2O")),                # clean=H2O (3)
    ("IPv6",               expected_orp("IPv6")),               # clean=IPv6 (4)

    # --- All-caps acronyms ---
    ("NASA",               expected_orp("NASA")),               # clean=NASA (4)
    ("UNESCO",             expected_orp("UNESCO")),             # clean=UNESCO (6)
    ("RSVP",               expected_orp("RSVP")),               # clean=RSVP (4)
    ("API",                expected_orp("API")),                # clean=API (3)

    # --- Symbol-heavy / URL-like tokens ---
    ("www.example.com",    expected_orp("www.example.com")),    # clean=wwwexamplecom (12)
    ("user@mail",          expected_orp("user@mail")),          # clean=usermail (8)

    # --- Numeric strings ---
    ("2024",               expected_orp("2024")),               # clean=2024 (4)
    ("100",                expected_orp("100")),                # clean=100 (3)

    # --- Punctuation-only / empty-ish tokens ---
    ("...",                expected_orp("...")),                # clean="" → 0
    ("---",                expected_orp("---")),                # clean="" → 0

    # --- Mixed case ---
    ("iPhone",             expected_orp("iPhone")),             # clean=iPhone (6)
    ("macOS",              expected_orp("macOS")),              # clean=macOS (5)
]

assert len(GOLDEN_DATASET) == 50, f"Expected 50 cases, got {len(GOLDEN_DATASET)}"


def run_benchmark() -> float:
    correct = 0
    for word, expected in GOLDEN_DATASET:
        try:
            result = calculate_orp(word)
            if result == expected:
                correct += 1
        except Exception:
            pass  # count as wrong

    accuracy = correct / len(GOLDEN_DATASET)
    return accuracy


if __name__ == "__main__":
    score = run_benchmark()
    print(f"{score:.4f}", flush=True)
