# markdown-to-msword-converter

Plugin wrapper that exposes Markdown-to-MS Word conversion as a single nested skill using plugin-local scripts.

## Nested Skill

- `skills/markdown-to-msword-converter`

## Scripts

- Bulk wrapper: `plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py`
- Per-file converter: `plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts/md_to_docx.py`
- Folder scope config: `plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts/folders_to_convert.json`

The per-file converter resolves internal markdown links to `.docx` targets directly so generated Word docs keep clickable references.

## Dependencies

- Intent file: `plugins/markdown-to-msword-converter/requirements.in`
- Lockfile: `plugins/markdown-to-msword-converter/requirements.txt`

Compile lockfile:

```powershell
python -m piptools compile "plugins/markdown-to-msword-converter/requirements.in" --output-file "plugins/markdown-to-msword-converter/requirements.txt"
```

Install from lockfile:

```powershell
python -m pip install -r "plugins/markdown-to-msword-converter/requirements.txt"
```

## Typical usage

```powershell
python plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py --dry-run
python plugins/markdown-to-msword-converter/skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py --overwrite
```
