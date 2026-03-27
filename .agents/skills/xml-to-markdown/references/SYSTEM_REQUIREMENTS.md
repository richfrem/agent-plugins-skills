# System Requirements

## Runtime Environment
- **Node.js**: Version 18.x or higher (Required for ES Module support).
- **OS**: Windows, Linux (WSL), or macOS.

## Dependencies
The tool is self-contained but relies on the following NPM packages (install via `npm install`):

- **fast-xml-parser**: High-performance XML parsing.
- **glob**: File pattern matching.
- **prettier**: Markdown formatting.
- **xmldom**: DOM implementation for specific XML operations.
- **commander**: CLI argument parsing.

## Hardware
- **RAM**: Minimum 4GB recommended for large XML dumps (>50MB).
- **Disk**: Source XML files can be large; ensure sufficient space for both Source XML and Output Markdown.

## Input Constraints
- **Encoding**: Source files must be UTF-8 or Latin1 (ISO-8859-1).
- **Format**:
    - Forms/Menus: Must be exported via `frmf2xml`.
    - Reports: Must be exported via `rwconverter` (XML format).
    - Libraries: Must be exported via `frmcmp_batch` (Script/Text format).
