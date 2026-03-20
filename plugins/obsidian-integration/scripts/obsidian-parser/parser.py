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
                'heading': heading.strip() if heading else None,
                'block': block.strip() if block else None
            })
            
        return results

    @staticmethod
    def create_callout(callout_type: str, title: str, content: str) -> str:
        """
        Wraps content in an Obsidian-flavored callout.
        """
        valid_types = ['info', 'warning', 'error', 'success', 'note', 'tip', 'important']
        callout_type = callout_type.lower()
        if callout_type not in valid_types:
            callout_type = 'note'
            
        lines = content.strip().split('\n')
        callout_lines = [f"> [!{callout_type}] {title}"]
        for line in lines:
            callout_lines.append(f"> {line}")
            
        return '\n'.join(callout_lines) + '\n'

def main():
    parser = argparse.ArgumentParser(description="Obsidian Markdown Parser")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a markdown file for Obsidian syntax')
    analyze_parser.add_argument('--file', required=True, help='Path to markdown file')

    # Callout command
    callout_parser = subparsers.add_parser('callout', help='Generate an Obsidian callout')
    callout_parser.add_argument('--type', required=True, help='Callout type (info, warning, etc.)')
    callout_parser.add_argument('--title', required=True, help='Callout title')
    callout_parser.add_argument('--text', required=True, help='Callout content text')

    args = parser.parse_args()

    if args.command == 'analyze':
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = ObsidianParser.extract_links(content)
            embeds = ObsidianParser.extract_embeds(content)
            
            result = {
                'file': args.file,
                'wikilinks': links,
                'embeds': embeds,
                'metrics': {
                    'total_links': len(links),
                    'total_embeds': len(embeds)
                }
            }
            print(json.dumps(result, indent=2))
        except FileNotFoundError:
            print(json.dumps({"error": f"File not found: {args.file}"}))
            sys.exit(1)
            
    elif args.command == 'callout':
        # Handle literal \n if passed from CLI
        text = args.text.replace('\\n', '\n')
        print(ObsidianParser.create_callout(args.type, args.title, text))

if __name__ == '__main__':
    main()
