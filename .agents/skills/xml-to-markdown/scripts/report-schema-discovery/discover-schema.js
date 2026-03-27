/**
 * tools/standalone/xml-to-markdown/report-schema-discovery/discover-schema.js
 * =============================================================================
 * 
 * Purpose:
 *   Analyzes all Oracle Reports XML files and discovers the complete schema
 *   of elements and attributes used across all reports.
 * 
 * Usage:
 *   node discover-schema.js [--dir <path>] [--out <path>] [--verbose]
 * 
 * Output:
 *   report_schema.json - Complete schema of all elements and their attributes
 * 
 * @module discover-schema
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import xml2js from 'xml2js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Parse arguments
const args = process.argv.slice(2);
const OPTIONS = {
    dir: null,
    out: null,
    verbose: false
};

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--dir') OPTIONS.dir = args[++i];
    else if (args[i] === '--out') OPTIONS.out = args[++i];
    else if (args[i] === '--verbose') OPTIONS.verbose = true;
}

// Defaults
const INPUT_DIR = OPTIONS.dir
    ? path.resolve(OPTIONS.dir)
    : path.join(__dirname, '../../../../legacy-system/oracle-forms/Reports');
const OUTPUT_FILE = OPTIONS.out
    ? path.resolve(OPTIONS.out)
    : path.join(__dirname, 'report_schema.json');

/**
 * Schema Collection - tracks all unique elements and their attributes
 */
class SchemaCollection {
    constructor() {
        // Map of element name -> { attributes: Set, count: number, sampleFiles: [] }
        this.elements = new Map();
        this.globalAttributes = new Set();
        this.filesProcessed = 0;
        this.totalElements = 0;
    }

    /**
     * Check if element exists in collection
     * @param {string} name - Element name
     * @returns {boolean}
     */
    hasElement(name) {
        return this.elements.has(name);
    }

    /**
     * Add element to collection (if not exists)
     * @param {string} name - Element name
     * @param {string} fileName - Source file for sample tracking
     * @returns {boolean} True if newly added
     */
    addElement(name, fileName = null) {
        if (!this.elements.has(name)) {
            this.elements.set(name, {
                attributes: new Set(),
                count: 1,
                sampleFiles: fileName ? [fileName] : []
            });
            return true;
        }
        const el = this.elements.get(name);
        el.count++;
        if (fileName && el.sampleFiles.length < 3 && !el.sampleFiles.includes(fileName)) {
            el.sampleFiles.push(fileName);
        }
        return false;
    }

    /**
     * Check if attribute exists for an element
     * @param {string} elementName - Element name
     * @param {string} attrName - Attribute name
     * @returns {boolean}
     */
    hasAttribute(elementName, attrName) {
        const el = this.elements.get(elementName);
        return el ? el.attributes.has(attrName) : false;
    }

    /**
     * Add attribute to element and global set
     * @param {string} elementName - Element name
     * @param {string} attrName - Attribute name
     * @returns {boolean} True if newly added to element
     */
    addAttribute(elementName, attrName) {
        this.globalAttributes.add(attrName);

        if (!this.elements.has(elementName)) {
            this.addElement(elementName);
        }
        const el = this.elements.get(elementName);
        if (!el.attributes.has(attrName)) {
            el.attributes.add(attrName);
            return true;
        }
        return false;
    }

    /**
     * Convert to JSON-serializable object
     * @returns {Object}
     */
    toJSON() {
        const result = {
            meta: {
                filesProcessed: this.filesProcessed,
                totalElementsFound: this.totalElements,
                uniqueElementTypes: this.elements.size,
                uniqueAttributeCount: this.globalAttributes.size,
                uniqueAttributes: [...this.globalAttributes].sort(),
                generatedAt: new Date().toISOString()
            },
            elements: {}
        };

        // Sort elements alphabetically
        const sortedNames = [...this.elements.keys()].sort();
        for (const name of sortedNames) {
            const el = this.elements.get(name);
            result.elements[name] = {
                count: el.count,
                attributes: [...el.attributes].sort(),
                sampleFiles: el.sampleFiles
            };
        }

        return result;
    }
}

/**
 * Recursively traverse XML object and collect schema
 * @param {Object} obj - Current XML node
 * @param {SchemaCollection} schema - Schema collection
 * @param {string} fileName - Source file name
 * @param {boolean} verbose - Enable verbose logging
 */
function traverseXml(obj, schema, fileName, verbose = false) {
    if (!obj || typeof obj !== 'object') return;

    for (const key of Object.keys(obj)) {
        // Skip xml2js metadata keys
        if (key === '$' || key === '_' || key === '$$') continue;

        // This is an element
        schema.totalElements++;
        const isNew = schema.addElement(key, fileName);
        if (isNew && verbose) {
            console.log(`  + New element: ${key}`);
        }

        const value = obj[key];
        const items = Array.isArray(value) ? value : [value];

        for (const item of items) {
            if (!item || typeof item !== 'object') continue;

            // Process attributes (in $ property)
            if (item.$ && typeof item.$ === 'object') {
                for (const attrName of Object.keys(item.$)) {
                    const isNewAttr = schema.addAttribute(key, attrName);
                    if (isNewAttr && verbose) {
                        console.log(`    + New attribute: ${key}.${attrName}`);
                    }
                }
            }

            // Recurse into children
            traverseXml(item, schema, fileName, verbose);
        }
    }
}

/**
 * Create XML parser optimized for schema discovery
 */
function createParser() {
    return new xml2js.Parser({
        explicitArray: true,
        mergeAttrs: false,
        attrkey: '$',
        charkey: '_',
        explicitChildren: false,
        normalizeTags: false,
        normalize: true,
        trim: true
    });
}

/**
 * Parse XML file
 * @param {string} filePath - Path to XML file
 * @returns {Promise<Object>}
 */
async function parseXml(filePath) {
    const parser = createParser();
    const content = fs.readFileSync(filePath, 'utf8');
    return new Promise((resolve, reject) => {
        parser.parseString(content, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });
}

/**
 * Main discovery function
 */
async function discoverSchema() {
    console.log('Oracle Reports Schema Discovery Tool');
    console.log('=====================================\n');

    // Verify input directory
    if (!fs.existsSync(INPUT_DIR)) {
        console.error(`Error: Directory not found: ${INPUT_DIR}`);
        process.exit(1);
    }

    // Get all XML files
    const files = fs.readdirSync(INPUT_DIR)
        .filter(f => f.endsWith('.xml'))
        .map(f => path.join(INPUT_DIR, f));

    console.log(`Input:  ${INPUT_DIR}`);
    console.log(`Output: ${OUTPUT_FILE}`);
    console.log(`Files:  ${files.length} XML files\n`);

    const schema = new SchemaCollection();
    let errorCount = 0;

    for (const file of files) {
        const fileName = path.basename(file);
        try {
            if (OPTIONS.verbose) console.log(`Processing: ${fileName}`);

            const parsed = await parseXml(file);
            traverseXml(parsed, schema, fileName, OPTIONS.verbose);
            schema.filesProcessed++;

        } catch (error) {
            console.log(`✗ Error: ${fileName} - ${error.message}`);
            errorCount++;
        }
    }

    // Write output
    const output = schema.toJSON();
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));

    // Summary
    console.log('\n=== Summary ===');
    console.log(`Files processed: ${schema.filesProcessed}/${files.length}`);
    console.log(`Unique elements: ${output.meta.uniqueElementTypes}`);
    console.log(`Total elements:  ${output.meta.totalElementsFound}`);
    console.log(`Errors:          ${errorCount}`);
    console.log(`\nSchema written to: ${OUTPUT_FILE}`);

    // Show top elements
    const sortedByCount = Object.entries(output.elements)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 15);

    console.log('\n=== Top 15 Elements by Count ===');
    console.log('| Element | Count | Attributes |');
    console.log('|---------|-------|------------|');
    for (const [name, data] of sortedByCount) {
        console.log(`| ${name} | ${data.count} | ${data.attributes.length} |`);
    }
}

discoverSchema().catch(error => {
    console.error('Script failed:', error);
    process.exit(1);
});
