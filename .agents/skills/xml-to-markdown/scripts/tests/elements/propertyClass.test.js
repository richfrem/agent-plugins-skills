import fs from 'fs';
import path from 'path';
import { expect } from 'chai';
import { parseTestXml } from '../utils/testXmlParser.js';
import { propertyClassProcessor } from '../../src/processors/elements/PropertyClassProcessor.js';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Test suite for the PropertyClass Processor
 * Tests the processing of Oracle Forms PropertyClass elements using all XML files 
 * found in test-data/PropertyClass/ directory
 */
describe('PropertyClass Processor', () => {
    const outputDir = path.join(__dirname, '../../test-output/elements/PropertyClass');
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

    // Helper function to process PropertyClass files
    const processPropertyClassFile = async (filename) => {
        const xmlPath = path.join(__dirname, '../../test-data/PropertyClass', filename);
        const xmlContent = fs.readFileSync(xmlPath, 'utf-8');
        const parsedXml = await parseTestXml(xmlContent);
        
        // Process each PropertyClass element
        if (Array.isArray(parsedXml.PropertyClass)) {
            for (const element of parsedXml.PropertyClass) {
                const processed = await propertyClassProcessor.processRootElement(element);
                const output = [];
                await propertyClassProcessor.formatResults(processed, () => {}, output);
                allOutput.push(...output);
            }
        } else if (parsedXml.PropertyClass) {
            const processed = await propertyClassProcessor.processRootElement(parsedXml.PropertyClass);
            const output = [];
            await propertyClassProcessor.formatResults(processed, () => {}, output);
            allOutput.push(...output);
        }
    };

    // Write output to file after all tests
    afterAll(() => {
        fs.appendFileSync(outputFile, allOutput.join('\n'));
    });

    // Get all XML files from the test data directory
    const testFiles = fs.readdirSync(path.join(__dirname, '../../test-data/PropertyClass'))
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

            await processPropertyClassFile(file.name);
            
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
