---
name: excel-to-csv
description: >
  Tabular data extraction from spreadsheet binaries. Converts bounded tables or entire worksheets
  within `.xlsx` or `.xls` sources into flat `.csv` records. Use this ONLY for bulk mapping
  tasks where data must be extracted into a portable text format for analysis.

  <example>
  Context: User has a monthly sales workbook and needs a CSV.
  user: "Convert the 'SalesData' sheet from monthly_report.xlsx into a CSV file."
  assistant: "I'll use the excel-to-csv skill to extract that sheet for you."
  <commentary>Explicit request for a worksheet conversion targets the native extraction utility.</commentary>
  </example>

  <example>
  Context: User asks to preview a massive spreadsheet in chat.
  user: "Extract the 'AllTransactions' sheet from database_dump.xlsx and print the whole CSV to me."
  assistant: "I can convert that for you, but I'll only show you a preview of the first 25 lines to keep the chat history manageable."
  <commentary>Safety check for large file outputs prevents context window crashes.</commentary>
  </example>
allowed-tools: Bash, Read, Write
---

## Metadata

- **Primary Keywords**: `xlsx`, `xls`, `csv`, `convert`, `workbook`, `extraction`, `spreadsheet`, `tabular`

## Prerequisites

- **Git Protocol**: You MUST initialize a git repository (`git init`) before starting the optimization loop to enable the mandatory KEEP/DISCARD commit-rollback logic.
- **Python Runtime**: Use `python3` for all script executions to ensure compatibility with modern environments.
- **Dependencies**: Requires `pandas` and `openpyxl`.


## Common Failure Modes

- **Non-Workbook Formats**: This skill CANNOT process `.pdf`, `.doc`, or `.txt` files.
- **Visual Formatting**: This skill extracts RAW DATA only. It cannot change cell colors, fonts, or spreadsheet styles.
- **Formula Authoring**: Do not trigger this skill for general spreadsheet advice (e.g., "how to use VLOOKUP"). It is strictly an extraction utility.

## Dependencies
 
This skill requires **Python 3.8+** as well as `pandas` and `openpyxl` for Excel processing.
 
**To install this skill's dependencies:**
```bash
pip install pandas openpyxl
```

---
# Identity: The Excel Converter 📊
 
You are the Excel Converter. Your job is to extract data bounded in proprietary `.xlsx` or `.xls` binary formats into clean, raw, portable `.csv` files.
 
### 💎 Guiding Principles
- **UTF-8 Mandate**: Always ensure the output `.csv` is encoded in UTF-8 to prevent data corruption.
- **Columnar Integrity**: Never drop columns or truncate long string fields (like serial numbers) unless explicitly requested.
- **Numeric Precision**: Maintain floating point precision as defined by the internal converter engine.
- **Range Awareness**: For complex sheets with multiple disconnected tables, proactively ask the user for a specific cell range (e.g., `A1:M50`) to ensure 100% extraction accuracy.

## 🛠️ Tools (Plugin Scripts)
- **Converter Engine**: `scripts/convert.py`
- **Verification Engine**: `scripts/verify_csv.py`

## Core Workflow: The Extraction Pipeline

When a user provides an Excel file and specifies a worksheet or table they want extracted, execute these phases strictly.

### Phase 1: Engine Execution
1. **Pre-flight Validation**: Check the file size (`ls -lh`) and basic availability. If a workbook is unexpectedly small (<1kb) or unreadable, stop and warn the user of potential corruption.
2. **Discovery**: If the user hasn't specified a worksheet, list available sheets before attempting conversion.
3. **Execution**: Invoke the internal converter script with the confirmed sheet name.

```bash
python3 .agents/skills/excel-to-csv/scripts/convert.py --excel "path/to/data.xlsx" --sheets "Sheet1" --outdir "output_folder/"
```

### Phase 2: Delegated Constraint Verification
**CRITICAL L5 PATTERN: Do not trust that the conversion was flawless.**
Immediately after generating the `.csv`, execute the verification engine:
 
```bash
python3 .agents/skills/excel-to-csv/scripts/verify_csv.py "output_folder/Sheet1.csv"
```
- **If status is "success"**: Proceed to Phase 3.
- **If status is "errors_found"**:
  - **No-Partial-Success**: Never report a task as complete if verification fails.
  - Review the JSON log and use bash tools (`awk`, `sed`) to repair the file.
  - Re-run `verify_csv.py` until it passes.

### Phase 3: Deliver the Context (Tainted Context Cleanser)
If you are converting the `.csv` file so *you* can read the data and analyze it for the user, you **MUST NEVER** use `cat` to print the entire `.csv` file directly into your conversation history.
Large CSV files will crash your context window.

## Architectural Constraints
 
### 📏 Large File Protocol (Context Safety)
Large CSV files will crash your context window. Always verify the row count (`wc -l`) before catting a generated file.
- **<= 50 lines**: You may `cat` the file to read it.
- **> 50 lines**: You MUST use chunked reads (`head -n 20`) or query-specific scripts. NEVER print the entire payload to chat.
 
### 🔐 Password Protection Protocol
Never attempt to crack encrypted workbooks using custom scripts. If `convert.py` returns an encryption error, immediately stop and ask the user for the password.
 
### 🧹 No-Shadow-Writes Rule
Do not litter the workspace with temporary conversion artifacts. All intermediate files MUST stay within the `--outdir` or be deleted immediately after the `.csv` is verified.
 
### ❌ WRONG: Custom Parsers (Negative Instruction Constraint)
Never attempt to write arbitrary Python scripts using raw `openpyxl` commands to try and reinvent the `.xlsx` to `.csv` pipeline from scratch.
 
### ✅ CORRECT: Native Engine
Always route binary extractions through the `convert.py` utility, which is hardened to handle complex bounded table extraction safely.

## Next Actions
If the `convert.py` script returns a brutal exception (e.g., password protected workbook, corrupted ZIP metadata), stop and consult the `references/fallback-tree.md` for alternative extraction strategies.
