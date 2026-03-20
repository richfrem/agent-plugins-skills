import unittest
import sys
import os

# Add the parent directory to sys.path so we can import parser.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parser import ObsidianParser

class TestObsidianParser(unittest.TestCase):
    
    def test_standard_wikilink(self):
        text = "Here is a [[Standard Link]] to a note."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Standard Link")
        self.assertIsNone(links[0]['heading'])
        self.assertIsNone(links[0]['block'])
        self.assertIsNone(links[0]['alias'])

    def test_link_with_heading(self):
        text = "Check this [[Note#My Heading]] for details."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Note")
        self.assertEqual(links[0]['heading'], "My Heading")
        self.assertIsNone(links[0]['block'])

    def test_link_with_block(self):
        text = "This is a block transclusion [[Note#^block-123]] reference."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Note")
        self.assertEqual(links[0]['block'], "block-123")
        self.assertIsNone(links[0]['heading'])

    def test_aliased_link(self):
        text = "Read the [[Note Name|Display Text]] here."
        links = ObsidianParser.extract_links(text)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Note Name")
        self.assertEqual(links[0]['alias'], "Display Text")

    def test_embed_transclusion(self):
        # Embeds should NOT be matched by extract_links, but should be by extract_embeds
        text = "Here is an image: ![[image.png]] and a normal [[Link]]."
        links = ObsidianParser.extract_links(text)
        embeds = ObsidianParser.extract_embeds(text)
        
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['target'], "Link")
        
        self.assertEqual(len(embeds), 1)
        self.assertEqual(embeds[0]['target'], "image.png")

    def test_callout_generation(self):
        result = ObsidianParser.create_callout('warning', 'Important Note', 'This is a warning.\nPlease read.')
        expected = "> [!warning] Important Note\n> This is a warning.\n> Please read.\n"
        self.assertEqual(result, expected)
        
    def test_invalid_callout_type_fallback(self):
        result = ObsidianParser.create_callout('invalid_type', 'Title', 'Content')
        # Should fallback to a standard 'note'
        self.assertTrue(result.startswith("> [!note] Title"))

if __name__ == '__main__':
    unittest.main()
