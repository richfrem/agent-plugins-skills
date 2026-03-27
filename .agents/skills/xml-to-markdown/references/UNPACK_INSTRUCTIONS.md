# Unpack Instructions

This tool is distributed as a text-based bundle. Follow these steps to hydrate it into a functional Node.js application:

1.  **Create Directory**:
    ```bash
    mkdir -p tools/standalone/xml-to-markdown
    ```

2.  **Extract Files**:
    - Place `package.json` in the root of the directory.
    - Place the `src/` folder and its contents (including subdirectories like `processors/`) preserving the structure.
    - Place `README.md` and `prompt.md` in the root.

3.  **Install Dependencies**:
    Run the following command in the directory:
    ```bash
    npm install
    ```

4.  **Verify Integrity**:
    Run a test conversion to ensure all modules are linked:
    ```bash
    node src/convert-forms-xml-to-markdown.js --help
    node src/convert-report-xml-to-markdown.js --help
    ```
