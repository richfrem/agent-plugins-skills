# Installation Guide

## standalone/xml-to-markdown

### 1. Requirements
- **Node.js**: v18+
- **NPM**: v9+

### 2. Setup
navigate to the tool directory:
```bash
cd tools/standalone/xml-to-markdown
```

Install dependencies:
```bash
npm install
```

### 3. Verification
Check if the main scripts are executable:

```bash
node src/convert-forms-xml-to-markdown.js --version
# Should output version or help

node src/convert-report-xml-to-markdown.js --version
# Should output version or help
```

### 4. Troubleshooting
- **Missing Modules**: If you see `Cannot find module`, delete `node_modules` and run `npm install` again.
- **Encoding Errors**: Ensure your XML inputs are UTF-8 or Latin1. The tool attempts auto-detection but explicit encoding conversion might be needed for very old dumps.
