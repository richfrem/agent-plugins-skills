# Procedural Fallback Tree: JSON Hygiene Audit

If the primary scanning engine (`./././find_json_duplicates.py`) exits with an error status, execute the following triage steps exactly in order:

## 1. Syntax Error Rejection (Exit Code 2)
If `./././find_json_duplicates.py` exits with `2`, the file is not valid JSON. This usually means missing or trailing commas, unescaped quotes, or mismatched braces.
- **Action**: The AST scanner requires valid JSON to build the dictionary tree. Inform the user the file is fundamentally broken and cannot be audited for duplicate keys until the syntax is fixed. Suggest running standard `.json` formatters to isolate the syntax error.

## 2. Validation Rejection (Exit Code 1)
If `./././find_json_duplicates.py` exits with `1`, duplicate keys definitively exist in the file.
- **Action**: Do not attempt to fix the duplicates yourself via Bash (`sed`/`awk`). Return the exact error string (e.g. `Duplicate keys detected in JSON AST layer: url, theme`) to the user so they can manually intervene, as automatic resolution of "which duplicate key is the correct one to keep" is highly destructive.
