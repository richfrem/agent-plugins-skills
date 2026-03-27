import fs from 'fs';
import path from 'path';
import { expect } from 'chai';
import { parseTestXml } from '../utils/testXmlParser.js';
import { objectLibraryProcessor } from '../../src/processors/elements/ObjectLibraryProcessor.js';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Test suite for the ObjectLibrary Processor
 * Tests the processing of Oracle Forms ObjectLibrary elements using all XML files 
 * found in test-data/ObjectLibrary/ directory
 */
describe('ObjectLibrary Processor', () => {
    const outputDir = path.join(__dirname, '../../test-output/elements/ObjectLibrary');
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

    // Helper function to process ObjectLibrary files
    const processObjectLibraryFile = async (filename) => {
        const xmlPath = path.join(__dirname, '../../test-data/ObjectLibrary', filename);
        const xmlContent = fs.readFileSync(xmlPath, 'utf-8');
        const parsedXml = await parseTestXml(xmlContent);
        
        // Process each ObjectLibrary element
        if (Array.isArray(parsedXml.ObjectLibrary)) {
            for (const element of parsedXml.ObjectLibrary) {
                const processed = await objectLibraryProcessor.processRootElement(element);
                const output = [];
                await objectLibraryProcessor.formatResults(processed, () => {}, output);
                allOutput.push(...output);
            }
        } else if (parsedXml.ObjectLibrary) {
            const processed = await objectLibraryProcessor.processRootElement(parsedXml.ObjectLibrary);
            const output = [];
            await objectLibraryProcessor.formatResults(processed, () => {}, output);
            allOutput.push(...output);
        }
    };

    // Write output to file after all tests
    afterAll(() => {
        fs.appendFileSync(outputFile, allOutput.join('\n'));
    });

    // Get all XML files from the test data directory
    const testFiles = fs.readdirSync(path.join(__dirname, '../../test-data/ObjectLibrary'))
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

            await processObjectLibraryFile(file.name);
            
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
