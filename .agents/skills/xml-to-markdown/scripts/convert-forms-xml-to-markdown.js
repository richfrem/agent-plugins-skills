#!/usr/bin/env node
/**
 * convert-forms-xml-to-markdown.js (CLI)
 * =====================================
 *
 * Purpose:
 *     Converts Oracle Forms XML (FMB/MMB/OLB) to Markdown. Supports --file or --batch modes.
 *
 * Layer: Curate / Cli_Entry_Points
 *
 * Prerequisites:
 *     You MUST run `npm install` inside this directory to satisfy dependencies:
 *     cd "plugins/legacy system/xml-to-markdown" && npm install
 *
 * Usage Examples:
 *     # Single file
 *     node "plugins/legacy system/xml-to-markdown/scripts/convert-forms-xml-to-markdown.js" --file "legacy-system/oracle-forms/XML/agobjects_olb.xml" --out "legacy-system/oracle-forms-markdown/XML"
 *
 *     # Batch process all XMLs 
 *     node "plugins/legacy system/xml-to-markdown/scripts/convert-forms-xml-to-markdown.js" --batch "legacy-system/oracle-forms/XML" --out "legacy-system/oracle-forms-markdown/XML" --verbose
 *
 * CLI Arguments:
 *     (Process.argv usage) Use --help to print options or see main()
 *
 * Key Functions:
 *     - parseArgs()
    - processXmlFile()
    - processAllXmlFiles()
    - main()
 *
 * Consumed by:
 *     (Unknown)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseXml } from './utils/xmlUtils.js';
import { moduleProcessor } from './processors/elements/ModuleProcessor.js';

// Define __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Default output directory
const DEFAULT_OUTPUT_DIR = path.join(__dirname, '../../../legacy-system/oracle-forms-overviews/forms');

// Parse command line arguments
const args = process.argv.slice(2);

function parseArgs() {
    const options = {
        file: null,
        batch: null,  // Now takes directory path directly
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
 * Processes an XML file and extracts module information
 * @param {string} filePath - Path to the XML file
 * @param {string} outputDir - Output directory for markdown files
 * @param {Function} log - Logging function
 * @returns {Promise<void>}
 */
async function processXmlFile(filePath, outputDir, log = console.log) {
    try {
        if (VERBOSE) log(`\n=== Processing file: ${filePath} ===`);

        // Get module name (first part before _) and type from filename
        const fileName = path.basename(filePath, '.xml');
        const moduleName = fileName.split('_')[0];

        // Determine module type from filename
        let moduleType = 'Unknown';
        if (fileName.includes('_fmb')) {
            moduleType = 'FormModule';
        } else if (fileName.includes('_mmb')) {
            moduleType = 'MenuModule';
        } else if (fileName.includes('_olb')) {
            moduleType = 'ObjectLibrary';
        }

        if (VERBOSE) {
            log(`Module details:
            - File: ${fileName}
            - Module Name: ${moduleName}
            - Module Type: ${moduleType}`);
        }

        // Read and parse XML
        const xmlContent = fs.readFileSync(filePath, 'utf8');
        const parsedXml = await parseXml(xmlContent);

        // Process the Module element
        let processed;
        if (Array.isArray(parsedXml.Module)) {
            processed = await moduleProcessor.processRootElement(parsedXml.Module[0]);
        } else if (parsedXml.Module) {
            processed = await moduleProcessor.processRootElement(parsedXml.Module);
        } else {
            throw new Error('No Module element found in XML');
        }

        if (VERBOSE) {
            console.log('Processed element structure:', JSON.stringify(processed, null, 2));
        }

        // Create output array and format results
        const output = [];
        await moduleProcessor.formatResults(processed, () => { }, output);

        // Create output directory if it doesn't exist
        if (!fs.existsSync(outputDir)) {
            if (VERBOSE) log(`Creating output directory: ${outputDir}`);
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Write output with naming pattern: {moduleName}-{ModuleType}.md
        const outputPath = path.join(outputDir, `${moduleName}-${moduleType}.md`);
        if (VERBOSE) log(`Writing output to: ${outputPath}`);

        // Write styled header and processed content
        const header = [
            '<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;">',
            `<h3 style="color: #2c3e50; margin: 0;">Module: ${moduleName} (${moduleType})</h3>`,
            '</div>\n\n'
        ].join('\n');

        // Write all results to output file
        fs.writeFileSync(outputPath, header + output.join('\n'));

        log(`✓ ${moduleName} (${moduleType}) -> ${outputPath}`);
    } catch (error) {
        log(`✗ Error processing ${filePath}: ${error.message}`);
        if (VERBOSE) log('Error details:', error);
        throw error;
    }
}

/**
 * Processes all XML files in the input directory
 * @param {string} inputDir - Directory containing XML files
 * @param {string} outputDir - Output directory for markdown files
 * @param {Function} log - Logging function
 * @returns {Promise<void>}
 */
async function processAllXmlFiles(inputDir, outputDir, log = console.log) {
    try {
        if (VERBOSE) log('\n=== Starting batch processing ===');
        log(`Input:  ${inputDir}`);
        log(`Output: ${outputDir}\n`);

        const files = fs.readdirSync(inputDir)
            .filter(file => file.endsWith('.xml'))
            .map(file => path.join(inputDir, file));

        log(`Found ${files.length} XML files to process\n`);
        if (VERBOSE) log('Files to process:', files);

        // Process each file
        let successCount = 0;
        let errorCount = 0;

        for (const file of files) {
            try {
                await processXmlFile(file, outputDir, log);
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
export { processXmlFile, processAllXmlFiles };

// Main execution
async function main() {
    console.log('XML to Markdown Converter');
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
        await processXmlFile(filePath, OUTPUT_DIR);
    } else if (OPTIONS.batch) {
        // Batch mode
        const inputDir = path.resolve(OPTIONS.batch);
        if (!fs.existsSync(inputDir)) {
            console.error(`Error: Directory not found: ${inputDir}`);
            process.exit(1);
        }
        await processAllXmlFiles(inputDir, OUTPUT_DIR);
    } else {
        // No arguments - show help
        console.log('Usage:');
        console.log('  node convert-xml-to-markdown.js --file <path>       Convert single file');
        console.log('  node convert-xml-to-markdown.js --batch <dir>       Convert all files in directory');
        console.log('  node convert-xml-to-markdown.js --out <path>        Custom output directory');
        console.log('  node convert-xml-to-markdown.js --verbose           Enable detailed logging');
        console.log('\nExamples:');
        console.log('  node convert-xml-to-markdown.js --file FORM0000_fmb.xml');
        console.log('  node convert-xml-to-markdown.js --batch ./xml-files --out ./output');
        console.log('  node convert-xml-to-markdown.js --file test.xml --out ./my-output --verbose');
        process.exit(0);
    }
}

main().catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
});
