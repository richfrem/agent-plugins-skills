# XML-to-Markdown Converter

Converts Oracle Forms binary exports (XML/TXT) to LLM-readable Markdown documentation. The tool includes utilities to convert:

1. Oracle Forms XML exports (FMB, MMB, OLB) to Markdown (`convert-forms-xml-to-markdown.js`)
2. Oracle Forms PL/SQL libraries (PLL) to Markdown (`convert-pll-to-markdown.js`)
3. Oracle Reports XML exports to Markdown (`convert-report-xml-to-markdown.js`)

## Prerequisites

> ⚠️ **Critical**: This tool requires pre-exported XML/TXT files from Oracle WebLogic utilities.
> The tool cannot read `.fmb`, `.mmb`, `.olb`, `.pll`, or `.rdf` binary files directly.

### Oracle Utility Reference

| Binary Format | Utility | Command Example | Documentation |
|---------------|---------|-----------------|---------------|
| `.fmb` (Forms) | `frmf2xml` | `frmf2xml FORM0000.fmb FORM0000_fmb.xml` | [Oracle Docs](https://docs.oracle.com/database/apex-18.1/AEMIG/Converting_FormModules_ObjectLibraries_MenuModules_to_XML.htm) |
| `.mmb` (Menus) | `frmf2xml` | `frmf2xml FORM0000.mmb FORM0000_mmb.xml` | Same as above |
| `.olb` (OLBs) | `frmf2xml` | `frmf2xml app1.olb app1_olb.xml` | Same as above |
| `.pll` (PLLs) | `frmcmp_batch` | `frmcmp_batch module=EXAMPLE_LIB.pll` | [Oracle KnowHow](https://www.oracleknowhow.com/compile-custom-oracle-forms-and-pll/) |
| `.rdf` (Reports) | `rwconverter` | `rwconverter source=RPT001.rdf destype=xmlfile` | [Oracle Report Builder](https://docs.oracle.com/html/B10314_01/pbr_cla.htm#634712) |

### Expected Input Structure

```
OracleFormsSourceFiles/
├── XML/
│   ├── FORM0000_fmb.xml    # FormModule exports
│   ├── FORM0000_mmb.xml    # MenuModule exports
│   └── PROJECT_olb.xml      # ObjectLibrary exports
├── pll/
│   ├── EXAMPLE_LIB.txt          # PLL text dumps
│   └── AGLIB.txt
└── Reports/
    └── RPT001.xml          # Report XML (not fully supported)
```

## Installation

```bash
cd "plugins/legacy system/xml-to-markdown"
npm install
```

## Usage

### Convert Forms/Menus/OLBs (XML → Markdown)

```bash
# Single file
node scripts/convert-forms-xml-to-markdown.js --file path/to/FORM0000_fmb.xml

# Batch process a directory
node scripts/convert-forms-xml-to-markdown.js --batch ./OracleFormsSourceFiles/XML

# Custom output directory
node scripts/convert-forms-xml-to-markdown.js --batch ./xml-files --out ./output

# Verbose mode
node scripts/convert-forms-xml-to-markdown.js --file test.xml --verbose
```

**Output:** `{output-dir}/{ModuleName}-{ModuleType}.md` (default: `outputs/XML/`)

### Convert Oracle Reports (XML → Markdown)

```bash
# Single file
node scripts/convert-report-xml-to-markdown.js --file path/to/RPT0030.xml

# Batch process a directory
node scripts/convert-report-xml-to-markdown.js --batch ./OracleFormsSourceFiles/Reports

# Custom output directory
node scripts/convert-report-xml-to-markdown.js --batch ./reports --out ./output
```

**Output:** `{output-dir}/{ReportName}.md` (default: `outputs/reports/`)

### Convert PL/SQL Libraries (TXT → Markdown)

```bash
# Single file
node scripts/convert-pll-to-markdown.js --file path/to/EXAMPLE_LIB.txt

# Batch process a directory
node scripts/convert-pll-to-markdown.js --batch ./OracleFormsSourceFiles/pll

# Custom output directory
node scripts/convert-pll-to-markdown.js --batch ./pll-files --out ./output
```

**Output:** `{output-dir}/{LibraryName}.md` (default: `outputs/pll/`)

## Architecture

```
scripts/
├── convert-forms-xml-to-markdown.js    # Entry point for Forms/Menu/OLB (--file | --batch)
├── convert-report-xml-to-markdown.js   # Entry point for Reports (--file | --batch)
├── convert-pll-to-markdown.js          # Entry point for PLL files (--file | --batch)
├── processors/
│   ├── BaseProcessor.js            # Abstract base class
│   ├── elementProcessor.js         # Central dispatcher
│   ├── elementTypes.js             # 42-element processor registry
│   └── elements/                   # Element-specific processors
│       ├── BlockProcessor.js
│       ├── TriggerProcessor.js
│       ├── AttachedLibraryProcessor.js
│       └── ... (42 total)
└── utils/
    ├── xmlUtils.js                 # XML parsing (xml2js)
    ├── codeUtils.js                # PL/SQL formatting
    └── attributeUtils.js           # Attribute extraction
```

## Testing

```bash
npm test                    # Run all tests
npm test -- --verbose       # Verbose output
npm test Block.test.js      # Run specific element test
```

## Known Limitations

- **Reports**: XML from `rwconverter` is not fully processed
- **Path Configuration**: Input/output paths are relative to script location

## Related Tools

- **Upstream**: Oracle WebLogic utilities (`frmf2xml`, `frmcmp_batch`, `rwconverter`)
- **Downstream**: RLM Distiller, Vector DB, Form Miners
