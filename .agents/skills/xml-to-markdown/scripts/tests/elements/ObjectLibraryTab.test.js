import fs from 'fs';
import path from 'path';
import { expect } from 'chai';
import { parseTestXml } from '../utils/testXmlParser.js';
import { objectLibraryTabProcessor } from '../../src/processors/elements/ObjectLibraryTabProcessor.js';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Test suite for the ObjectLibraryTab Processor
 * Tests the processing of Oracle Forms ObjectLibraryTab elements using all XML files 
 * found in test-data/ObjectLibraryTab/ directory
 */
describe('ObjectLibraryTab Processor', () => {
    const outputDir = path.join(__dirname, '../../test-output/elements/ObjectLibraryTab');
    const outputFile = path.join(outputDir, 'test_output.md');
    const allOutput = [];

    // Create output directory if it doesn't exist
    beforeAll(() => {
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        // Clear the output file
        fs.writeFileSync(outputFile, '');
    });

    // Helper function to process ObjectLibraryTab files
    const processObjectLibraryTabFile = async (filename) => {
        const xmlPath = path.join(__dirname, '../../test-data/ObjectLibraryTab', filename);
        const xmlContent = fs.readFileSync(xmlPath, 'utf-8');
        const parsedXml = await parseTestXml(xmlContent);
        
        // Process each ObjectLibraryTab element
        if (Array.isArray(parsedXml.ObjectLibraryTab)) {
            for (const element of parsedXml.ObjectLibraryTab) {
                const processed = await objectLibraryTabProcessor.processRootElement(element);
                const output = [];
                await objectLibraryTabProcessor.formatResults(processed, () => {}, output);
                allOutput.push(...output);
            }
        } else if (parsedXml.ObjectLibraryTab) {
            const processed = await objectLibraryTabProcessor.processRootElement(parsedXml.ObjectLibraryTab);
            const output = [];
            await objectLibraryTabProcessor.formatResults(processed, () => {}, output);
            allOutput.push(...output);
        }
    };

    // Write output to file after all tests
    afterAll(() => {
        fs.appendFileSync(outputFile, allOutput.join('\n'));
    });

    // Get all XML files from the test data directory
    const testFiles = fs.readdirSync(path.join(__dirname, '../../test-data/ObjectLibraryTab'))
        .filter(file => file.endsWith('.xml'))
        .map(file => ({ name: file, path: file }));

    // Process each test file
    testFiles.forEach(file => {
        test(`processes ${file.name}`, async () => {
            // Add file header to output with background color
            allOutput.push('\n');
            allOutput.push('<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;">');
            allOutput.push(`<h3 style="color: #2c3e50; margin: 0;">Input File: ${file.name}</h3>`);
            allOutput.push('</div>');
            allOutput.push('\n');

            await processObjectLibraryTabFile(file.name);
            
            // Write all results to output file
            fs.appendFileSync(outputFile, allOutput.join('\n'));
            
            // Basic validation
            expect(allOutput.length).to.be.greaterThan(0);
            expect(allOutput.join('')).to.include('###');
            
            // Verify mandatory attributes are present
            const outputText = allOutput.join('');
            expect(outputText).to.include('| Name |');
        });
    });
});
