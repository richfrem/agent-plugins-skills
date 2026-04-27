---
concept: complex-regex-to-capture-wikilinks-while-avoiding-transclusions
source: plugin-code
source_file: obsidian-wiki-engine/scripts/obsidian-parser/parser.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.268255+00:00
cluster: target
content_hash: cd595c9a7c55eb7a
---

# Complex regex to capture wikilinks while avoiding transclusions.

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/obsidian-wiki-engine/scripts/obsidian-parser/parser.py -->
"""
parser.py (CLI)
=====================================

Purpose:
    Core parser for Obsidian-flavored Markdown syntax.
    Extracts links, embeds, and facilitates creating callouts.

Layer: Core Operations

Usage Examples:
    python.py analyze --file example.md
    python.py callout --type info --title "Note" --text "Content"

Supported Object Types:
    - .md (Markdown notes with Obsidian syntax)

CLI Arguments:
    Subcommands: analyze, callout. Run with --help for details.

Input Files:
    - .md files.

Output:
    - JSON analysis or formatted callout block.

Key Functions:
    extract_links(): Extracts standard Obsidian links.
    extract_embeds(): Extracts Obsidian transclusions.
    create_callout(): Wraps content in a callout.

Script Dependencies:
    re, argparse, sys, json, typing

Consumed by:
    - obsidian-markdown-mastery skill
"""
import re
import argparse
import sys
import json
from typing import List, Dict, Optional

class ObsidianParser:
    """Core parser for Obsidian-flavored Markdown syntax."""

    @staticmethod
    def extract_links(text: str) -> List[Dict[str, str]]:
        """
        Extracts all standard Obsidian links (wikilinks) from the text.
        This explicitly avoids matching embeds (which start with !).
        """
        results = []
        # Complex regex to capture wikilinks while avoiding transclusions.
        # Logic: look behind for whitespace or beginning of string (or anything NOT a '!').
        # Using a negative lookbehind `(?<!\!)` ensures we don't grab `![[embed]]`.
        pattern = re.compile(r'(?<!\!)\[\[(.*?)\]\]')
        
        for match in pattern.finditer(text):
            inner_content = match.group(1)
            
            target = inner_content
            alias = None
            heading = None
            block = None
            
            # 1. Split Alias (if present)
            if '|' in inner_content:
                parts = inner_content.split('|', 1)
                target = parts[0]
                alias = parts[1]
                
            # 2. Split Heading or Block (if present)
            if '#' in target:
                parts = target.split('#', 1)
                target = parts[0]
                anchor = parts[1]
                
                if anchor.startswith('^'):
                    block = anchor[1:]
                else:
                    heading = anchor
                    
            results.append({
                'type': 'wikilink',
                'target': target.strip() if target else "",
                'heading': heading.strip() if heading else None,
                'block': block.strip() if block else None,
                'alias': alias.strip() if alias else None
            })
            
        return results

    @staticmethod
    def extract_embeds(text: str) -> List[Dict[str, str]]:
        """
        Extracts Obsidian transclusions/embeds (![[Note Name]]).
        """
        results = []
        pattern = re.compile(r'!\[\[(.*?)\]\]')
        
        for match in pattern.finditer(text):
            inner_content = match.group(1)
            
            target = inner_content
            heading = None
            block = None
            
            # Embeds don't technically support aliases in standard markdown rendering,
            # but sometimes people use them for image dimensions (e.g., ![[image.png|100]])
            if '|' in inner_content:
                target = inner_content.split('|', 1)[0]
                
            if '#' in target:
                parts = target.split('#', 1)
                target = parts[0]
                anchor = parts[1]
                
                if anchor.startswith('^'):
                    block = anchor[1:]
                else:
                    heading = anchor
                    
            results.append({
                'type': 'embed',
                'target': target.strip() if target else "",
                'heading': headin

*(content truncated)*

<!-- Source: plugin-code/obsidian-wiki-engine/scripts/parser.py -->
"""
parser.py (CLI)
=====================================

Purpose:
    Core parser for Obsidian-flavored Markdown syntax.
    Extracts links, embeds, and facilitates creating callouts.

Layer: Core Operations

Usage Examples:
    pythonparser.py analyze --file example.md
    pythonparser.py callout --type info --title "Note" --text "Content"

Supported Object Types:
    - .md (Markdown notes with Obsidian syntax)

CLI Arguments:
    Subcommands: analyze, callout. Run with --help for details.

Input Files:
    - .md files.

Output:
    - JSON analysis or formatted callout block.

Key Functions:
    extract_links(): Extracts standard Obsidian links.
    extract_embeds(): Extracts Obsidian transclusions.
    create_callout(): Wraps content in a callout.

Script Dependencies:
    re, argparse, sys, json, typing

Co

*(combined content truncated)*

## See Also

- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-project-root-to-syspath]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/obsidian-parser/parser.py`
- **Indexed:** 2026-04-27T05:21:04.268255+00:00
