---
concept: markdown-to-msword-converter-v2
source: plugin-code
source_file: markdown-to-msword-converter/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.627585+00:00
cluster: plugin-code
content_hash: ad3f3dbdf0267b36
---

# markdown-to-msword-converter (V2)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[identity-the-markdown-to-ms-word-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]
- [[identity-the-markdown-to-ms-word-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]
- [[acceptance-criteria-markdown-to-word-converter]]
- [[identity-the-markdown-to-ms-word-converter]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `markdown-to-msword-converter/README.md`
- **Indexed:** 2026-04-17T06:42:09.627585+00:00
