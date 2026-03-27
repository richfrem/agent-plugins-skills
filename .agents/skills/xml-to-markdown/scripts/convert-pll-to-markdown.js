#!/usr/bin/env node
/**
 * convert-pll-to-markdown.js (CLI)
 * =====================================
 *
 * Purpose:
 *     Converts PL/SQL Library text dumps to Markdown. Supports --file or --batch modes.
 *
 * Layer: Curate / Cli_Entry_Points
 *
 * Prerequisites:
 *     You MUST run `npm install` inside this directory to satisfy dependencies:
 *     cd "plugins/legacy system/xml-to-markdown" && npm install
 *
 * Usage Examples:
 *     # Single file
 *     node "plugins/legacy system/xml-to-markdown/scripts/convert-pll-to-markdown.js" --file "legacy-system/oracle-forms/pll/example.txt" --out "legacy-system/oracle-forms-markdown/pll"
 *
 *     # Batch process all PLLs 
 *     node "plugins/legacy system/xml-to-markdown/scripts/convert-pll-to-markdown.js" --batch "legacy-system/oracle-forms/pll" --out "legacy-system/oracle-forms-markdown/pll" --verbose
 *
 * CLI Arguments:
 *     (Process.argv usage) Use --help to print options or see main()
 *
 * Key Functions:
 *     - parseArgs()
    - extractProceduresAndFunctions()
    - processPLLFile()
    - processAllPLLFiles()
    - main()
 *
 * Consumed by:
 *     (Unknown)
 */


import fs from 'fs';
import path from 'path';
import { formatPLSQL, cleanCode } from './utils/codeUtils.js';
import { fileURLToPath } from 'url';

// Define __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Default output directory
const DEFAULT_OUTPUT_DIR = path.resolve(__dirname, '../outputs/pll');

// Parse command line arguments
const args = process.argv.slice(2);

function parseArgs() {
    const options = {
        file: null,
        batch: null,  // Takes directory path directly
        out: null,
        verbose: false
    };

    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--file':
                options.file = args[++i];
                break;
            case '--batch':
                options.batch = args[++i];
                break;
            case '--out':
                options.out = args[++i];
                break;
            case '--verbose':
                options.verbose = true;
                break;
        }
    }

    return options;
}

const OPTIONS = parseArgs();
const VERBOSE = OPTIONS.verbose;
const OUTPUT_DIR = OPTIONS.out ? path.resolve(OPTIONS.out) : DEFAULT_OUTPUT_DIR;

/**
 * Extracts all procedure and function names from PL/SQL code.
 * @param {string} code
 * @returns {Array<{type: string, name: string, start: number, end: number}>}
 */
function extractProceduresAndFunctions(code) {
    const regex = /(?:\bPROCEDURE\b|\bFUNCTION\b)\s+([a-zA-Z0-9_]+)/gi;
    const matches = [];
    let match;
    while ((match = regex.exec(code)) !== null) {
        matches.push({
            type: match[0].toUpperCase().includes('PROCEDURE') ? 'PROCEDURE' : 'FUNCTION',
            name: match[1],
            start: match.index
        });
    }
    // Add end positions for each block
    for (let i = 0; i < matches.length; i++) {
        matches[i].end = i < matches.length - 1 ? matches[i + 1].start : code.length;
    }
    return matches;
}

/**
 * Processes a single PLL file and writes the markdown output.
 * @param {string} filePath - Path to the PLL text file
 * @param {string} outputDir - Output directory
 * @param {Function} log - Logging function
 */
function processPLLFile(filePath, outputDir, log = console.log) {
    try {
        if (VERBOSE) log(`\n=== Processing file: ${filePath} ===`);

        const fileName = path.basename(filePath, '.txt');
        const rawCode = fs.readFileSync(filePath, 'utf8');
        const code = cleanCode(rawCode);
        const formattedCode = formatPLSQL(code);

        // Extract procedures/functions for markdown headers
        const blocks = extractProceduresAndFunctions(code);

        // Markdown output
        let md = `<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;">
<h3 style="color: #2c3e50; margin: 0;">Library: ${fileName}</h3>
</div>

`;

        if (blocks.length === 0) {
            // No procedures/functions found, output whole code
            md += '```sql\n' + formattedCode + '\n```\n';
        } else {
            for (const block of blocks) {
                md += `\n### ${block.type}: ${block.name}\n\n`;
                const blockCode = code.substring(block.start, block.end);
                md += '```sql\n' + formatPLSQL(blockCode) + '\n```\n';
            }
        }

        // Create output directory if it doesn't exist
        if (!fs.existsSync(outputDir)) {
            if (VERBOSE) log(`Creating output directory: ${outputDir}`);
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Write to output file
        const outPath = path.join(outputDir, `${fileName}.md`);
        fs.writeFileSync(outPath, md, 'utf8');

        log(`✓ ${fileName} (${blocks.length} units) -> ${outPath}`);
    } catch (error) {
        log(`✗ Error processing ${filePath}: ${error.message}`);
        if (VERBOSE) log('Error details:', error);
        throw error;
    }
}

/**
 * Processes all PLL text files in the input directory.
 * @param {string} inputDir - Directory containing PLL text files
 * @param {string} outputDir - Output directory
 * @param {Function} log - Logging function
 */
function processAllPLLFiles(inputDir, outputDir, log = console.log) {
    try {
        if (VERBOSE) log('\n=== Starting batch processing ===');
        log(`Input:  ${inputDir}`);
        log(`Output: ${outputDir}\n`);

        const files = fs.readdirSync(inputDir)
            .filter(f => f.endsWith('.txt'))
            .map(f => path.join(inputDir, f));

        log(`Found ${files.length} PLL text files to process\n`);

        let successCount = 0;
        let errorCount = 0;

        for (const file of files) {
            try {
                processPLLFile(file, outputDir, log);
                successCount++;
            } catch (error) {
                errorCount++;
            }
        }

        log(`\n=== Summary ===`);
        log(`Total:   ${files.length}`);
        log(`Success: ${successCount}`);
        log(`Failed:  ${errorCount}`);
    } catch (error) {
        log(`Error processing files: ${error.message}`);
        if (VERBOSE) log('Error details:', error);
        throw error;
    }
}

// Export the functions
export { processPLLFile, processAllPLLFiles, extractProceduresAndFunctions };

// Main execution
function main() {
    console.log('PLL to Markdown Converter');
    console.log('=========================\n');

    if (OPTIONS.file) {
        // Single file mode
        const filePath = path.resolve(OPTIONS.file);
        if (!fs.existsSync(filePath)) {
            console.error(`Error: File not found: ${filePath}`);
            process.exit(1);
        }
        console.log(`Input:  ${filePath}`);
        console.log(`Output: ${OUTPUT_DIR}\n`);
        processPLLFile(filePath, OUTPUT_DIR);
    } else if (OPTIONS.batch) {
        // Batch mode
        const inputDir = path.resolve(OPTIONS.batch);
        if (!fs.existsSync(inputDir)) {
            console.error(`Error: Directory not found: ${inputDir}`);
            process.exit(1);
        }
        processAllPLLFiles(inputDir, OUTPUT_DIR);
    } else {
        // No arguments - show help
        console.log('Usage:');
        console.log('  node convert-pll-to-markdown.js --file <path>       Convert single file');
        console.log('  node convert-pll-to-markdown.js --batch <dir>       Convert all files in directory');
        console.log('  node convert-pll-to-markdown.js --out <path>        Custom output directory');
        console.log('  node convert-pll-to-markdown.js --verbose           Enable detailed logging');
        console.log('\nExamples:');
        console.log('  node convert-pll-to-markdown.js --file EXAMPLE_LIB.txt');
        console.log('  node convert-pll-to-markdown.js --batch ./pll-files --out ./output');
        console.log('  node convert-pll-to-markdown.js --file AGLIB.txt --out ./my-output --verbose');
        process.exit(0);
    }
}

main();
