#!/usr/bin/env python
"""
parse_document.py
=================
Parses an input document (.txt, .md, .pdf, .docx) into a flat list of words
and outputs a JSON file for consumption by orp_engine.py.

Usage:
    python parse_document.py --input <file_path> --output <output_json>
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- File type handlers ---

def parse_text(file_path: Path) -> list[dict]:
    """Parse plain text or markdown files into a list of raw word tokens."""
    text = file_path.read_text(encoding="utf-8")
    return _tokenize(text)


def parse_pdf(file_path: Path) -> list[dict]:
    """Parse a PDF file into a list of raw word tokens using pdfminer.six."""
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        print("Error: pdfminer.six not installed. Run: pip install pdfminer.six", file=sys.stderr)
        sys.exit(1)

    text = extract_text(str(file_path))
    return _tokenize(text)


def parse_docx(file_path: Path) -> list[dict]:
    """Parse a .docx file into a list of raw word tokens using python-docx."""
    try:
        from docx import Document
    except ImportError:
        print("Error: python-docx not installed. Run: pip install python-docx", file=sys.stderr)
        sys.exit(1)

    doc = Document(str(file_path))
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text)
        else:
            # Blank paragraph = paragraph break sentinel
            paragraphs.append("\n\n")

    text = "\n".join(paragraphs)
    return _tokenize(text)


def _tokenize(text: str) -> list[dict]:
    """
    Split text into word-level tokens, preserving paragraph break sentinels.
    Returns: list of {"word": str, "is_para_end": bool}
    """
    tokens = []
    paragraphs = re.split(r"\n\s*\n", text)

    for i, para in enumerate(paragraphs):
        words = para.split()
        for j, word in enumerate(words):
            is_last_in_para = (j == len(words) - 1)
            tokens.append({
                "word": word,
                "is_para_end": is_last_in_para and (i < len(paragraphs) - 1)
            })

    return tokens


# --- Main ---

PARSERS = {
    ".txt": parse_text,
    ".md": parse_text,
    ".pdf": parse_pdf,
    ".docx": parse_docx,
}


def main() -> None:
    """Entry point: routes to correct parser based on file extension."""
    parser = argparse.ArgumentParser(description="Parse document to word token list.")
    parser.add_argument("--input", required=True, help="Path to input document")
    parser.add_argument("--output", required=True, help="Path for output JSON word list")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = input_path.suffix.lower()
    if ext not in PARSERS:
        print(f"Error: Unsupported file type '{ext}'. Supported: {list(PARSERS.keys())}", file=sys.stderr)
        sys.exit(1)

    tokens = PARSERS[ext](input_path)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Parsed {len(tokens)} words from '{input_path}' -> '{output_path}'")


if __name__ == "__main__":
    main()
