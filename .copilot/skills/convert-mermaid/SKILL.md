---
name: convert-mermaid
description: Convert mermaid diagrams mmd/mermaid to .png and have an option to pick/increase resolution level
disable-model-invocation: false
---

# Convert Mermaid

## Overview
This skill converts Mermaid Diagram text files (`.mmd` or `.mermaid`) into high-resolution PNG images.

## Instructions
When a user asks you to convert a mermaid file to an image, you must use the deterministic Python script provided in this skill's `scripts/` directory. 

Do not attempt to write your own javascript or bash script to do this.

**Usage:**
```bash
python3 plugins/skills/convert-mermaid/scripts/convert.py -i <input-file.mmd> -o <output-file.png> -s <scale-number>
```

**Parameters:**
- `-i` The input file path.
- `-o` The destination file path.
- `-s` The resolution scale (default is 1). If the user asks for "high resolution", "retina", or "HQ", set `-s` to 3 or 4.
- `-t` The theme (default, dark, forest, neutral).

**Example:**
If the user says: *"Convert architecture.mmd to a high res PNG"*
You run:
`python3 plugins/skills/convert-mermaid/scripts/convert.py -i architecture.mmd -o architecture.png -s 3`

## Reference Links
Place any supplemental context or heavy documentation inside `reference.md` and link it here using relative paths.
