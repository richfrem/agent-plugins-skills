# Procedural Fallback Tree: Excel Conversion

If the primary Conversion Engine (`convert.py`) fails, execute the following triage steps exactly in order:

## 1. Engine Execution Failure (ImportError / Env Issues)
If `convert.py` crashes due to missing dependencies (`pandas` or `openpyxl`):
- **Action**: Inform the user that the Python environment is missing dependencies. Offer to run `pip install pandas openpyxl` to resolve the issue. Do NOT attempt to rewrite the converter in bash.

## 2. Parsing Error (Corrupt File / Password)
If `openpyxl` or `pandas` throws an exception reading the `.xlsx`:
- **Password Check**: Ask the user if the worksheet is password protected. The script currently cannot handle encrypted files.
- **Format Check**: If it is an `.xls` (older 97-2003 binary), `openpyxl` will fail. Attempt to switch the pandas engine from `openpyxl` to `xlrd` (if installed) or advise the user to save it as `.xlsx`.

## 3. Empty Extraction / Empty File Warning
If `verify_csv.py` returns `EmptyFile` or the conversion summary says `Skipped (empty)`:
- **Action**: Verify the `--sheets` name exactly matches the workbook tab. Excel sheet names often have trailing spaces (e.g., `'Sheet1 '`). If uncertain, remove the `--sheets` argument to extract all sheets and see what names are generated.

## 4. Verification Loop Rejection (Jagged Rows)
If `verify_csv.py` returns `JaggedRow`:
- **Action**: This indicates Excel formatting (merged cells, floating tables) corrupted the standard 1D CSV output. Instruct the user that the Excel file is too unstructured for a clean CLI extraction, and suggest they use a targeted pandas script instead to slice the exact `[min_row:max_row, min_col:max_col]` coordinates of the data.
