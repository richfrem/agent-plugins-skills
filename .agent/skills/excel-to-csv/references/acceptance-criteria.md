# Acceptance Criteria: Excel To CSV Converter

The `excel-to-csv` workflow MUST satisfy the following success metrics:

1. **Successful Binary Extraction**: Given a multi-sheet `.xlsx` file, the command successfully triggers `convert.py` to extract designated sheets into separate `.csv` files inside an output directory.
2. **Delegated Constraint Pass**: The output `.csv` must pass entirely through `verify_csv.py` returning `"status": "success"` with 0 jagged rows or empty bounds.
3. **Context Window Safety**: The agent must NEVER attempt to print or `cat` massive generated `.csv` files into the context window, strictly obeying the `head` truncation rule for files > 50 lines.
