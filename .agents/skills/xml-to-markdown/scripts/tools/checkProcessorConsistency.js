/**
 * tools/standalone/xml-to-markdown/src/tools/checkProcessorConsistency.js
 * ========================================================================
 * 
 * Purpose:
 *   Quality assurance tool that scans all element processors for consistency
 *   with the "evolved approach" patterns (documentation, implementation).
 * 
 * Usage:
 *   node src/tools/checkProcessorConsistency.js
 * 
 * Output:
 *   - Console report of missing patterns per processor
 *   - JSON report file: processor-consistency-report.txt
 * 
 * Checks For:
 *   - Documentation: XML examples, common attributes, child elements
 *   - Implementation: processRootElement, processChildren, debug logging
 * 
 * @module checkProcessorConsistency
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define the evolved approach patterns to check for
const EVOLVED_PATTERNS = {
    documentation: {
        xmlExamples: /XML Structure Examples:/,
        commonAttributes: /Common Attributes:/,
        commonChildElements: /Common Child Elements:/,
        commonTypes: /Common .* Types:/,
        commonUseCases: /Common Use Cases:/
    },
    implementation: {
        processRootElement: /async processRootElement\(/,
        processChildren: /async processChildren\(/,
        debugLogging: /if \(this.debug\) console.log/,
        properIndentation: /const indent = '  '.repeat\(indentLevel\)/,
        errorHandling: /if \(typeof log === 'function'\)/
    }
};

/**
 * Check if a file matches our evolved approach
 * @param {string} filePath - Path to the processor file
 * @returns {Object} Results of the check
 */
function checkFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const results = {
        file: path.basename(filePath),
        missingPatterns: [],
        matchesEvolvedApproach: true
    };

    // Check documentation patterns
    for (const [category, patterns] of Object.entries(EVOLVED_PATTERNS)) {
        for (const [patternName, pattern] of Object.entries(patterns)) {
            if (!pattern.test(content)) {
                results.missingPatterns.push(`${category}.${patternName}`);
                results.matchesEvolvedApproach = false;
            }
        }
    }

    return results;
}

/**
 * Main function to check all processor files
 */
async function main() {
    const processorsDir = path.join(__dirname, '..', 'processors', 'elements');
    const files = fs.readdirSync(processorsDir)
        .filter(file => file.endsWith('Processor.js'));

    console.log('Checking processor files for consistency with evolved approach...\n');

    const results = files.map(file =>
        checkFile(path.join(processorsDir, file))
    );

    const needsUpdate = results.filter(r => !r.matchesEvolvedApproach);
    const upToDate = results.filter(r => r.matchesEvolvedApproach);

    console.log('Files that need updating:');
    needsUpdate.forEach(result => {
        console.log(`\n${result.file}:`);
        console.log('Missing patterns:');
        result.missingPatterns.forEach(pattern => console.log(`  - ${pattern}`));
    });

    console.log('\nFiles that are up to date:');
    upToDate.forEach(result => {
        console.log(`  - ${result.file}`);
    });

    // Write results to a file for reference
    const outputPath = path.join(__dirname, '..', '..', 'processor-consistency-report.txt');
    const report = {
        timestamp: new Date().toISOString(),
        needsUpdate: needsUpdate.map(r => ({
            file: r.file,
            missingPatterns: r.missingPatterns
        })),
        upToDate: upToDate.map(r => r.file)
    };

    fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
    console.log(`\nDetailed report written to: ${outputPath}`);
}

// Run the check
main().catch(console.error); 