# Acceptance Criteria: Excel to CSV Converter

The excel-to-csv skill must meet the following criteria to be considered operational:

## 1. Sheet Specificity
- [ ] The agent correctly targets a specific sheet for conversion when asked, rather than blindly converting the entire workbook.
- [ ] The output CSV is named consistently with the sanitized sheet name.

## 2. Empty Data Handling
- [ ] The script gracefully skips empty sheets by default and accurately reports them in the CLI `Summary` block.
- [ ] Completely empty rows and columns in otherwise populated sheets are stripped before writing to CSV.

## 3. Dependency Management
- [ ] The skill gracefully handles execution errors when `pandas` or `openpyxl` are missing, presenting the user with a readable error instead of a raw traceback.
