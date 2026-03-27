import fs from 'fs';
import path from 'path';
import { expect } from 'chai';
import { parseTestXml } from '../utils/testXmlParser.js';
import { lovProcessor } from '../../src/processors/elements/LovProcessor.js';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Test suite for the Lov Processor
 * Tests the processing of Oracle Forms Lov elements using all XML files 
 * found in test-data/Lov/ directory
 */
describe('Lov Processor', () => {
    const outputDir = path.join(__dirname, '../../test-output/elements/Lov');
    const outputFile = path.join(outputDir, 'test_output.md');
    let allOutput = [];

    // Create output directory if it doesn't exist
    beforeAll(() => {
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        // Clear the output file
        fs.writeFileSync(outputFile, '');
    });

    // Clear output array before each test
    beforeEach(() => {
        allOutput = [];
    });

    // Helper function to process Lov files
    const processLovFile = async (filename) => {
        const xmlPath = path.join(__dirname, '../../test-data/Lov', filename);
        console.log(`Processing file: ${xmlPath}`);
        const xmlContent = fs.readFileSync(xmlPath, 'utf-8');
        console.log(`XML content: ${xmlContent}`);
        const parsedXml = await parseTestXml(xmlContent);
        console.log('Parsed XML:', parsedXml);
        
        // Process each Lov element
        if (Array.isArray(parsedXml.LOV)) {
            console.log('Found array of LOV elements');
            for (const element of parsedXml.LOV) {
                const processed = await lovProcessor.processRootElement(element);
                console.log('Processed element:', processed);
                const output = [];
                await lovProcessor.formatResults(processed, () => {}, output);
                console.log('Formatted output:', output);
                allOutput.push(...output);
            }
        } else if (parsedXml.LOV && parsedXml.LOV.$) {
            console.log('Found single LOV element');
            const processed = await lovProcessor.processRootElement(parsedXml.LOV);
            console.log('Processed element:', processed);
            const output = [];
            await lovProcessor.formatResults(processed, () => {}, output);
            console.log('Formatted output:', output);
            allOutput.push(...output);
        } else {
            console.log('No LOV elements found');
        }
        console.log('All output:', allOutput);
    };

    // Write output to file after all tests
    afterAll(() => {
        fs.appendFileSync(outputFile, allOutput.join('\n'));
    });

    // Get all XML files from the test data directory
    const testFiles = fs.readdirSync(path.join(__dirname, '../../test-data/Lov'))
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

            await processLovFile(file.name);
            
            // Write results to output file
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
