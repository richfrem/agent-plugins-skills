---
concept: add-the-parent-directory-to-syspath-so-we-can-import-parserpy
source: plugin-code
source_file: obsidian-wiki-engine/scripts/obsidian-parser/tests/test_parser.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.014883+00:00
cluster: self
content_hash: 56b72b047a74ea76
---

# Add the parent directory to sys.path so we can import parser.py

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
test_parser.py (Tests)
=====================================

Purpose:
    Unit tests for ObsidianParser extracting links, embeds, and callout generation.

Layer: Tests

Usage Examples:
    python -m unittest plugins/obsidian-integration/scripts/obsidian-parser/tests/test_parser.py

Supported Object Types:
    - None

CLI Arguments:
    Standard unittest arguments.

Input Files:
    - None

Output:
    - Test results.

Key Functions:
    test_standard_wikilink(): Test standard wikilink extraction.
    test_link_with_heading(): Test link with heading.
    test_link_with_block(): Test link with block.
    test_aliased_link(): Test aliased link.
    test_embed_transclusion(): Test embed transclusion.
    test_callout_generation(): Test callout generation.

Script Dependencies:
    unittest, sys, os, parser

Consumed by:
    - None
"""
import unittest
import sys
import os

# Add the parent directory to sys.path so we can import parser.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parser import ObsidianParser

class TestObsidianParser(unittest.TestCase):
    
    def test_standard_wikilink(self) -> None:
        text = "Here is a [[Standard Link]] to a note."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Standard Link")
        self.assertIsNone(links[0]['heading'])
        self.assertIsNone(links[0]['block'])
        self.assertIsNone(links[0]['alias'])

    def test_link_with_heading(self) -> None:
        text = "Check this [[Note#My Heading]] for details."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Note")
        self.assertEqual(links[0]['heading'], "My Heading")
        self.assertIsNone(links[0]['block'])

    def test_link_with_block(self) -> None:
        text = "This is a block transclusion [[Note#^block-123]] reference."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Note")
        self.assertEqual(links[0]['block'], "block-123")
        self.assertIsNone(links[0]['heading'])

    def test_aliased_link(self) -> None:
        text = "Read the [[Note Name|Display Text]] here."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Note Name")
        self.assertEqual(links[0]['alias'], "Display Text")

    def test_embed_transclusion(self) -> None:
        # Embeds should NOT be matched by extract_links, but should be by extract_embeds
        text = "Here is an image: ![[image.png]] and a normal [[Link]]."
        links = ObsidianParser.extract_links(text)
        embeds = ObsidianParser.extract_embeds(text)
        
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Link")
        
        self.assertEqual(len(embeds), 1)
        self.assertEqual(embeds[0]['target'], "image.png")

    def test_callout_generation(self) -> None:
        result = ObsidianParser.create_callout('warning', 'Important Note', 'This is a warning.\nPlease read.')
        expected = "> [!warning] Important Note\n> This is a warning.\n> Please read.\n"
        self.assertEqual(result, expected)
        
    def test_invalid_callout_type_fallback(self) -> None:
        result = ObsidianParser.create_callout('invalid_type', 'Title', 'Content')
        # Should fallback to a standard 'note'
        self.assertTrue(result.startswith("> [!note] Title"))

if __name__ == '__main__':
    unittest.main()


## See Also

- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-project-root-to-syspath]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[use-npx-to-lazily-execute-mermaid-cli-so-the-user-doesnt-need-to-globally-install-it]]
- [[fix-1-literal-n-chars-write-back-immediately-so-json-parse-can-proceed]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/obsidian-parser/tests/test_parser.py`
- **Indexed:** 2026-04-27T05:21:04.014883+00:00
