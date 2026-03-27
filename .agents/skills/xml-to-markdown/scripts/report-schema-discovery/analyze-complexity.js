/**
 * tools/standalone/xml-to-markdown/report-schema-discovery/analyze-complexity.js
 * ==============================================================================
 * 
 * Purpose:
 *   Analyzes Report XMLs to build a dependency graph of elements.
 *   Determines complexity order for processor implementation (Leaf nodes -> Complex nodes).
 * 
 * Usage:
 *   node analyze-complexity.js
 * 
 * Output:
 *   report_element_complexity.json
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import xml2js from 'xml2js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const INPUT_DIR = path.join(__dirname, '../../../../legacy-system/oracle-forms/Reports');
const OUTPUT_FILE = path.join(__dirname, 'report_element_complexity.json');

// Parser config - same as report converter
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

function parseXml(filePath) {
    const parser = createParser();
    const content = fs.readFileSync(filePath, 'utf8');
    return new Promise((resolve, reject) => {
        parser.parseString(content, (err, result) => {
            if (err) resolve(null); // soft fail
            else resolve(result);
        });
    });
}

/**
 * Tracks element relationships
 */
const elements = new Map(); // name -> { children: Set, attributes: Set, count: 0 }

function registerElement(name) {
    if (!elements.has(name)) {
        elements.set(name, {
            children: new Set(),
            attributes: new Set(),
            count: 0
        });
    }
    return elements.get(name);
}

function traverse(obj, parentName = null) {
    if (!obj || typeof obj !== 'object') return;

    // Handle array roots from xml2js
    if (Array.isArray(obj)) {
        obj.forEach(item => traverse(item, parentName));
        return;
    }

    // Iterate keys
    for (const key of Object.keys(obj)) {
        if (key === '$') {
            // Attributes of parent
            if (parentName) {
                const parent = elements.get(parentName);
                Object.keys(obj['$']).forEach(attr => parent.attributes.add(attr));
            }
            continue;
        }
        if (key === '_') continue; // Text content

        // This key is a child element
        const childName = key;
        const child = registerElement(childName);
        child.count++;

        if (parentName) {
            const parent = elements.get(parentName);
            parent.children.add(childName);
        }

        traverse(obj[key], childName);
    }
}

async function analyze() {
    console.log('Analyzing Element Complexity...');

    if (!fs.existsSync(INPUT_DIR)) {
        console.error(`Dir not found: ${INPUT_DIR}`);
        return;
    }

    const files = fs.readdirSync(INPUT_DIR).filter(f => f.endsWith('.xml'));
    console.log(`Processing ${files.length} files...`);

    for (const file of files) {
        const result = await parseXml(path.join(INPUT_DIR, file));
        if (result) {
            // Root is typically 'report'
            traverse(result, null);
        }
    }

    // Calculate Complexity Depth
    // Level 0 = Leaf nodes (no children)
    // Level 1 = Containers of Level 0
    // ...

    const complexityLevels = new Map(); // name -> level

    function getLevel(name, stack = []) {
        if (complexityLevels.has(name)) return complexityLevels.get(name);
        if (stack.includes(name)) return 999; // Cycle detection

        const el = elements.get(name);
        if (el.children.size === 0) {
            complexityLevels.set(name, 0);
            return 0;
        }

        let maxChildLevel = -1;
        for (const child of el.children) {
            maxChildLevel = Math.max(maxChildLevel, getLevel(child, [...stack, name]));
        }

        const level = maxChildLevel + 1;
        complexityLevels.set(name, level);
        return level;
    }

    // Process all elements
    for (const name of elements.keys()) {
        getLevel(name);
    }

    // Output JSON
    const output = {
        meta: {
            totalElements: elements.size,
            generatedAt: new Date().toISOString()
        },
        complexity: []
    };

    // Group by level
    const sortedDetails = [...elements.entries()]
        .map(([name, data]) => ({
            name,
            level: complexityLevels.get(name),
            count: data.count,
            children: [...data.children].sort(),
            attributes: [...data.attributes].sort()
        }))
        .sort((a, b) => a.level - b.level || a.name.localeCompare(b.name));

    output.complexity = sortedDetails;

    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));

    // Print Summary
    console.log('\n=== Complexity Analysis ===');
    console.log(`Leaf Nodes (Level 0): ${sortedDetails.filter(d => d.level === 0).length}`);
    console.log(`Complex Nodes: ${sortedDetails.filter(d => d.level > 0).length}`);
    console.log(`Max Depth: ${Math.max(...sortedDetails.map(d => d.level))}`);
    console.log(`\nResults saved to: ${OUTPUT_FILE}`);
}

analyze();
