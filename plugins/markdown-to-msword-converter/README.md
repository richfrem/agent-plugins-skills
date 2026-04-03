# markdown-to-msword-converter (V2)

Plugin wrapper that exposes Markdown-to-MS Word conversion as a single nested skill using plugin-local scripts. Upgraded to V2 with L5 Delegated Constraint Verification.

## Nested Skill

- `skills/markdown-to-msword-converter`

## Scripts

- Bulk wrapper: `./skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py`
- Per-file converter: `./skills/markdown-to-msword-converter/scripts/md_to_docx.py`
- Verification engine: `./skills/markdown-to-msword-converter/scripts/verify_docx.py`
- Folder scope config: `./skills/markdown-to-msword-converter/scripts/folders_to_convert.json`

The per-file converter resolves internal markdown links to `.docx` targets directly so generated Word docs keep clickable references.

## Dependencies

This plugin requires `python-docx`:

```bash
pip install -r requirements.txt
# or: pip install python-docx
```

Lockfile workflow:
```bash
pip-compile requirements.in
pip install -r requirements.txt
```

## Typical usage

```powershell
python ./scripts/run_bulk_md_to_docx.py --dry-run
python ./scripts/run_bulk_md_to_docx.py --overwrite
```
