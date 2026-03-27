#!/usr/bin/env node
/**
 * convert-report-xml-to-markdown.js (CLI)
 * =====================================
 *
 * Purpose:
 *     Converts Oracle Reports XML to Markdown. Extracts parameters, SQL queries, data sources.
 *
 * Layer: Curate / Cli_Entry_Points
 *
 * Usage Examples:
 *     node tools/standalone/xml-to-markdown/src/convert-report-xml-to-markdown.js --help
 *
 * CLI Arguments:
 *     (Process.argv usage detected)
 *
 * Key Functions:
 *     - createReportParser()
    - parseReportXml()
    - parseArgs()
    - processReportFile()
    - recursiveGenerateMarkdown()
    - main()
 *
 * Consumed by:
 *     (Unknown)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import xml2js from 'xml2js';

// Create parser optimized for Oracle Reports XML
// (different from Forms parser which uses explicitChildren:true)
function createReportParser() {
    return new xml2js.Parser({
        explicitArray: true,      // Keep arrays
        mergeAttrs: false,        // Keep attributes in $
        attrkey: '$',             // Attributes in $
        charkey: '_',             // Text content in _
        explicitChildren: false,  // DON'T put children in $$ (key difference!)
        preserveChildrenOrder: true,
        normalizeTags: false,
        normalize: true,
        trim: true
    });
}

async function parseReportXml(xmlData) {
    const parser = createReportParser();
    return new Promise((resolve, reject) => {
        parser.parseString(xmlData, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });
}

// Define __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Default output directory - matches legacy-system structure
const DEFAULT_OUTPUT_DIR = path.join(__dirname, '../../../legacy-system/oracle-forms-markdown/reports');

// Parse command line arguments
const args = process.argv.slice(2);

function parseArgs() {
    const options = {
        file: null,
        batch: null,
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

const options = parseArgs();
const VERBOSE = options.verbose;

/**
 * Process a report XML file and generate markdown
 * @param {string} filePath - Path to the report XML file
 * @param {string} outputDir - Output directory
 * @param {Function} log - Logging function
 */
async function processReportFile(filePath, outputDir, log = console.log) {
    try {
        if (VERBOSE) log(`\n=== Processing report: ${filePath} ===`);

        const fileName = path.basename(filePath, '.xml');
        const xmlContent = fs.readFileSync(filePath, 'utf8');
        const parsedXml = await parseReportXml(xmlContent);

        // Get report root element
        // xml2js with explicitArray: true returns root as array
        const reportArray = parsedXml.report;
        if (!reportArray || reportArray.length === 0) {
            throw new Error('No <report> element found in XML. This may not be a valid Oracle Reports file.');
        }
        const report = Array.isArray(reportArray) ? reportArray[0] : reportArray;

        const reportAttrs = report.$ || {};
        const reportName = reportAttrs.name || fileName;

        // Initialize Registry Context
        // Dynamic import to avoid circular dependency issues if any
        const { reportProcessorRegistry } = await import('./processors/ReportProcessorRegistry.js');

        const context = {
            registry: reportProcessorRegistry,
            log: VERBOSE ? log : () => { },
            stats: {
                elements: new Set(),
                attributeCount: 0
            }
        };

        // --- PROCESSING ---
        // Process root report using Registry
        // Treating root as 'report' element
        const processor = await reportProcessorRegistry.getProcessor('report');
        const processedData = await processor.process(report, context);

        // --- STATS HEADER ---
        const uniqueElements = context.stats.elements.size;
        const totalAttributes = context.stats.attributeCount;

        // Build markdown output
        const md = [];

        // Manual Header
        md.push(`<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;">`);
        md.push(`<h3 style="color: #2c3e50; margin: 0;">Report: ${reportName}</h3>`);
        md.push(`</div>\n`);

        // Stats
        md.push(`> **Stats**: ${uniqueElements} Unique Element Types | ${totalAttributes} Total Attributes\n`);

        // Report Metadata
        md.push(`## Report Metadata\n`);
        md.push(`| Attribute | Value |`);
        md.push(`|-----------|-------|`);
        for (const [key, val] of Object.entries(reportAttrs)) {
            md.push(`| ${key} | ${val} |`);
        }
        md.push('');

        // --- GENERATION ---
        // Recursively generate markdown using registry logic
        // We skip the root 'report' generation call here because we just manually created the header.
        // Instead, we iterate children.

        if (processedData && processedData.children) {
            for (const child of processedData.children) {
                await recursiveGenerateMarkdown(child, md, context);
            }
        }

        // Create output directory if needed
        if (!fs.existsSync(outputDir)) {
            if (VERBOSE) log(`Creating output directory: ${outputDir}`);
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // Write output
        const outputPath = path.join(outputDir, `${fileName}.md`);
        fs.writeFileSync(outputPath, md.join('\n'));

        log(`✓ ${reportName} -> ${outputPath}`);
        log(`  Stats: ${uniqueElements} elements, ${totalAttributes} attributes`);

    } catch (error) {
        log(`✗ Error processing ${filePath}: ${error.message}`);
        if (VERBOSE) log('Error details:', error);
        throw error;
    }
}

/**
 * Recursive markdown generator
 * @param {Object} data - Processed data node
 * @param {Array} mdOutput - Output lines
 * @param {Object} context - Registry context
 */
async function recursiveGenerateMarkdown(data, mdOutput, context) {
    if (!data) return;

    // Get processor to handle generation for this type
    const processor = await context.registry.getProcessor(data.type);

    // Processor generates its own markdown
    if (processor && typeof processor.generateMarkdown === 'function') {
        processor.generateMarkdown(data, mdOutput, (child, output) => recursiveGenerateMarkdown(child, output || mdOutput, context));
    }

    // Recurse children
    // Note: Some processors might handle children generation internally (like GroupProcessor),
    // but the pattern is to support recursion if not fully handled.
    // For now, let's recurse if the processor didn't stop it (we assume processor.generateMarkdown appends, logic flow continues).

    // DECISION: We rely on the processor to render children if it wants to control layout (like tables),
    // OR we assume recursive rendering for everything.
    // GroupProcessor currently renders Data Items explicitly.
    // So if we ALSO recurse here, we get duplicates.

    // FIX strategy: 
    // 1. If processor returns true/something from generateMarkdown, maybe it signals "I handled everything"? 
    // No, standard interface doesn't return anything.

    // 2. We can check if the processor handled children? 
    // Hard to know.

    // 3. We can just NOT recurse here and trust the processor.
    // GenericReportElementProcessor needs to iterate children though.
    // Most specific processors (Group, ProgramUnit) handle their own children formatting.
    // ParameterProcessor is a leaf (or handles itself).

    // So if I trust the processor, Generic must be updated to output recursive children.

    // Let's UPDATE GenericReportElementProcessor to iterate children.
    // And in THIS loop, we rely on processor.generateMarkdown.

    // But wait, BaseReportElementProcessor has a generic generateMarkdown?
    // It prints Attributes. It does NOT print children.

    // So I need a mechanism.
    // Let's let the recursive function handle children ONLY if the processor is Generic/Base?

    // Or better: Let's pass the 'recursiveGenerateMarkdown' function TO the generateMarkdown method!
    // processor.generateMarkdown(data, mdOutput, recursiveGenerateMarkdown)
    // Then GroupProcessor can call it for children it DOESN'T handle explicitly.
    // And BaseProcessor can call it for ALL children.

    // This is the visitor pattern.
    // I cannot easily change the signature of generateMarkdown in all files now (Phase 4 completed).

    // COMPROMISE:
    // Iterate children here.
    // If GroupProcessor already rendered them, we get duplicates.
    // GroupProcessor.js:
    // It filters children 'dataItem', 'formula' and renders tables.
    // It does NOT iterate other children (like 'filter', 'displayInfo').

    // If I iterate here, 'dataItem' wil appear twice (once in table, once as child).
    // EXCEPT DataItemProcessor generates a table row string `| ... |`. 
    // If I recurse here, that row gets appended to the main array.
    // If GroupProcessor ALSO appends it, we explicitly get duplicates.

    // Solution:
    // Modify GroupProcessor to consume/mark children as handled?
    // Or just let GroupProcessor handle only the *Summary* table, and let recursion handle details?

    // Let's assume for now that if I recurse, I might get duplicates.
    // But DataItemProcessor markdown output is just a table line.
    // If GroupProcessor generates a table header, then calls children...
    // GroupProcessor:
    //   mdOutput.push(`| Name ... |`);
    //   for (item) ... mdOutput.push(`| ${item.name} ... |`);

    // So GroupProcessor IS doing the generation.
    // Use `visited` set? No.

    // I will use a simple heuristic:
    // If the processor has a specific `generateMarkdown` implementation (not Base), assume it handles children or intends to skip them.
    // If it relies on Base, Base does NOT handle children, so we must recurse.

    // How to detect if it's Base? 
    // `processor instanceof BaseReportElementProcessor` is always true.
    // Check constructor name?

    // Better: GenericReportElementProcessor should handle recursion.
    // GroupProcessor should handle recursion.
    // I will leave this loop to NOT recurse automatically.
    // I will Update GenericReportElementProcessor to iterate children.
    // AND I will update BaseReportElementProcessor to iterate children.

    // If I do that, then GroupProcessor (extends Base) will iterate children?
    // No, GroupProcessor overrides generateMarkdown.

    // So:
    // 1. Update BaseReportElementProcessor to `generateMarkdown` -> Recurse.
    // 2. Update GroupProcessor -> Render specific tables, then maybe recurse remaining? 
    //    Or just render tables. (User request: Data Dictionary).

    // I will update this function to pass `recursiveGenerateMarkdown` callback to the processor?
    // `processor.generateMarkdown(data, mdOutput, generateChildCallback)`

    // Let's try to update BaseReportElementProcessor to accept the callback.
    // It's safer.
}

async function main() {
    try {
        if (options.file) {
            // Process single file
            const outputDir = options.out || DEFAULT_OUTPUT_DIR;
            await processReportFile(options.file, outputDir);
        } else if (options.batch) {
            // Batch process directory
            const inputDir = options.batch;
            const outputDir = options.out || DEFAULT_OUTPUT_DIR;

            if (!fs.existsSync(inputDir)) {
                console.error(`Error: Input directory not found: ${inputDir}`);
                process.exit(1);
            }

            const files = fs.readdirSync(inputDir).filter(f => f.toLowerCase().endsWith('.xml'));
            console.log(`Found ${files.length} XML files in ${inputDir}`);

            for (const file of files) {
                const filePath = path.join(inputDir, file);
                await processReportFile(filePath, outputDir);
            }
        } else {
            // Show help
            console.log('Usage: node convert-report-xml-to-markdown.js --file <path> | --batch <dir> [--out <path>]');
            process.exit(1);
        }
    } catch (error) {
        console.error('Fatal error:', error);
        process.exit(1);
    }
}

// Run main if script is executed directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
    main();
}

export { processReportFile };
