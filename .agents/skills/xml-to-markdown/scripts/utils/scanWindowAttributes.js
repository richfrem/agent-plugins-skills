/**
 * tools/standalone/xml-to-markdown/src/utils/scanWindowAttributes.js
 * ====================================================================
 * 
 * Purpose:
 *   Utility script to scan XML files for Window element attributes.
 *   Generates a report of all attributes used across Window elements.
 * 
 * Usage:
 *   node src/utils/scanWindowAttributes.js
 * 
 * @module scanWindowAttributes
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

async function scanWindowAttributes() {
    try {
        // First, find all Window elements
        const { stdout: windowElements } = await execAsync(
            'grep -r "<Window" inputs/ | sort | uniq'
        );

        console.log('Found Window elements in:');
        console.log(windowElements);

        // Now, find all attributes used in Window elements
        const { stdout: windowAttributes } = await execAsync(
            'grep -r "<Window" inputs/ | grep -o \'\\w*="[^"]*"\' | cut -d"=" -f1 | sort | uniq'
        );

        console.log('\nAll attributes found in Window elements:');
        console.log(windowAttributes);

        // Create a detailed report
        const report = [];
        report.push('# Window Element Attribute Scan Report');
        report.push('\n## Files containing Window elements:');
        report.push(windowElements.split('\n').map(line => `- ${line}`).join('\n'));

        report.push('\n## All attributes found:');
        report.push(windowAttributes.split('\n').map(attr => `- ${attr}`).join('\n'));

        // Write the report to a file
        const reportPath = path.join(process.cwd(), 'WindowAttributeScan.md');
        fs.writeFileSync(reportPath, report.join('\n'));
        console.log(`\nReport written to ${reportPath}`);

    } catch (error) {
        console.error('Error scanning Window attributes:', error);
    }
}

// Run the scan
scanWindowAttributes(); 