/**
 * tools/standalone/xml-to-markdown/src/utils/scanWindowElements.js
 * ==================================================================
 * 
 * Purpose:
 *   Scans XML files for Window elements and generates analysis reports.
 *   Creates test data examples for Window processing validation.
 * 
 * Usage:
 *   node src/utils/scanWindowElements.js
 * 
 * @module scanWindowElements
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

async function scanWindowElements() {
    try {
        // First, find all Window elements with their attributes
        const { stdout: windowElements } = await execAsync(
            'grep -r "<Window" inputs/ | grep -o \'<Window[^>]*>\' | sort | uniq'
        );

        console.log('Found Window elements:');
        console.log(windowElements);

        // Now, find all unique attributes used in Window elements
        const { stdout: windowAttributes } = await execAsync(
            'grep -r "<Window" inputs/ | grep -o \'\\w*="[^"]*"\' | cut -d"=" -f1 | sort | uniq'
        );

        console.log('\nAll attributes found in Window elements:');
        console.log(windowAttributes);

        // Create a detailed report
        const report = [];
        report.push('# Window Element Analysis Report');
        report.push('\n## All Window Elements Found:');
        report.push(windowElements.split('\n').map(line => `- ${line}`).join('\n'));

        report.push('\n## All Attributes Found:');
        report.push(windowAttributes.split('\n').map(attr => `- ${attr}`).join('\n'));

        // Write the report to a file
        const reportPath = path.join(process.cwd(), 'WindowElementAnalysis.md');
        fs.writeFileSync(reportPath, report.join('\n'));
        console.log(`\nReport written to ${reportPath}`);

        // Create test data examples
        const testDataDir = path.join(process.cwd(), 'test-data', 'Window');
        if (!fs.existsSync(testDataDir)) {
            fs.mkdirSync(testDataDir, { recursive: true });
        }

        // Create example test files based on common patterns
        const examples = [
            {
                name: 'test_1.xml',
                content: `<Window Name="WINDOW0" Title="Main Window" Width="20960" Height="11940" ResizeAllowed="true" ShowHorizontalScrollbar="false" ShowVerticalScrollbar="false"/>`
            },
            {
                name: 'test_2.xml',
                content: `<Window Name="WINDOW1" Title="Modal Dialog" Width="14000" Height="9000" Modal="true" ResizeAllowed="false" HideOnExit="true"/>`
            },
            {
                name: 'test_3.xml',
                content: `<Window Name="WINDOW2" Title="Document Window" Width="20960" Height="11940" WindowStyle="Document" InheritMenu="true" PrimaryCanvas="CMAIN"/>`
            },
            {
                name: 'test_4.xml',
                content: `<Window Name="WINDOW3" Title="Dialog Window" Width="12000" Height="8000" WindowStyle="Dialog" MinimizeAllowed="false" MaximizeAllowed="false" MoveAllowed="true"/>`
            },
            {
                name: 'test_5.xml',
                content: `<Window Name="WINDOW4" Title="Parent Window" Width="20960" Height="11940" ParentModule="MODULE1" ParentModuleType="12" ParentName="CLSDOCUMENTWINDOW" ParentType="29"/>`
            }
        ];

        // Write example files
        examples.forEach(example => {
            const filePath = path.join(testDataDir, example.name);
            fs.writeFileSync(filePath, example.content);
            console.log(`Created test file: ${filePath}`);
        });

    } catch (error) {
        console.error('Error scanning Window elements:', error);
    }
}

// Run the scan
scanWindowElements(); 