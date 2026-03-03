---
name: markdown-to-msword-converter
description: Converts Markdown files to one MS Word document per file using plugin-local scripts and a folder-allowlist JSON.
disable-model-invocation: false
---

# Markdown to MS Word Converter

Use this skill when the user wants `.md` files converted into `.docx` across the project, either as single-file conversion or bulk conversion.

## Execution

Run the plugin wrapper script:

```powershell
python plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py --dry-run
python plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py --overwrite
```

## Behavior

- One `.docx` output per `.md` file
- Uses plugin-local scripts under `plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts`
- Scope is controlled by `folders_to_convert.json` (configured folders + optional root `.md` files)
- Bulk mode calls `md_to_docx.py` once per file
- Single-file mode calls `md_to_docx.py` directly

## Link handling

- `md_to_docx.py` writes clickable hyperlinks into the Word document
- `md_to_docx.py` resolves internal `.md` targets to file-based `.docx` URI targets

## Optional flags

- `--root <path>` project root to scan
- `--overwrite` overwrite existing `.docx`
- `--dry-run` preview conversions only
- `--config <path>` path to folder allowlist JSON

## Dependency workflow

- Declare in `plugins/markdown-to-msword-converter/requirements.in`
- Compile with pip-tools to `plugins/markdown-to-msword-converter/requirements.txt`
- Install with `pip install -r plugins/markdown-to-msword-converter/requirements.txt`
