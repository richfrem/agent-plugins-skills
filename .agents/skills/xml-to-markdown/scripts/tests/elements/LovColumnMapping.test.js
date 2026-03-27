import fs from 'fs';
import path from 'path';
import { expect } from 'chai';
import { parseTestXml } from '../utils/testXmlParser.js';
import { lovColumnMappingProcessor } from '../../src/processors/elements/LovColumnMappingProcessor.js';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Test suite for the LovColumnMapping Processor
 * Tests the processing of Oracle Forms LovColumnMapping elements using all XML files 
 * found in test-data/LovColumnMapping/ directory
 */
describe('LovColumnMapping Processor', () => {
    const outputDir = path.join(__dirname, '../../test-output/elements/LovColumnMapping');
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

    // Helper function to process LovColumnMapping files
    const processLovColumnMappingFile = async (filename) => {
        const xmlPath = path.join(__dirname, '../../test-data/LovColumnMapping', filename);
        console.log(`Processing file: ${xmlPath}`);
        const xmlContent = fs.readFileSync(xmlPath, 'utf-8');
        console.log(`XML content: ${xmlContent}`);
        const parsedXml = await parseTestXml(xmlContent);
        console.log('Parsed XML:', parsedXml);
        
        // Process each LovColumnMapping element
        if (Array.isArray(parsedXml.LOVColumnMapping)) {
            console.log('Found array of LOVColumnMapping elements');
            for (const element of parsedXml.LOVColumnMapping) {
                const processed = await lovColumnMappingProcessor.processRootElement(element);
                console.log('Processed element:', processed);
                const output = [];
                await lovColumnMappingProcessor.formatResults(processed, () => {}, output);
                console.log('Formatted output:', output);
                allOutput.push(...output);
            }
        } else if (parsedXml.LOVColumnMapping && parsedXml.LOVColumnMapping.$) {
            console.log('Found single LOVColumnMapping element');
            const processed = await lovColumnMappingProcessor.processRootElement(parsedXml.LOVColumnMapping);
            console.log('Processed element:', processed);
            const output = [];
            await lovColumnMappingProcessor.formatResults(processed, () => {}, output);
            console.log('Formatted output:', output);
            allOutput.push(...output);
        } else {
            console.log('No LOVColumnMapping elements found');
        }
        console.log('All output:', allOutput);
    };

    // Write output to file after all tests
    afterAll(() => {
        fs.appendFileSync(outputFile, allOutput.join('\n'));
    });

    // Get all XML files from the test data directory
    const testFiles = fs.readdirSync(path.join(__dirname, '../../test-data/LovColumnMapping'))
        .filter(file => file.endsWith('.xml'))
        .map(file => ({ name: file, path: file }));

    // Process each test file
    testFiles.forEach(file => {
        test(`processes ${file.name}`, async () => {
            await processLovColumnMappingFile(file.name);
            
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