import fs from 'fs';
import path from 'path';
import { expect } from 'chai';
import { parseTestXml } from '../utils/testXmlParser.js';
import { dataSourceColumnProcessor } from '../../src/processors/elements/DataSourceColumnProcessor.js';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Test suite for the DataSourceColumn Processor
 * Tests the processing of Oracle Forms DataSourceColumn elements using all XML files 
 * found in test-data/DataSourceColumn/ directory
 */
describe('DataSourceColumn Processor', () => {
    const outputDir = path.join(__dirname, '../../test-output/elements/DataSourceColumn');
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

    // Helper function to process DataSourceColumn files
    const processDataSourceColumnFile = async (filename) => {
        const xmlPath = path.join(__dirname, '../../test-data/DataSourceColumn', filename);
        const xmlContent = fs.readFileSync(xmlPath, 'utf-8');
        const parsedXml = await parseTestXml(xmlContent);
        
        // Process each DataSourceColumn element
        if (Array.isArray(parsedXml.DataSourceColumn)) {
            for (const element of parsedXml.DataSourceColumn) {
                const processed = await dataSourceColumnProcessor.processRootElement(element);
                const output = [];
                await dataSourceColumnProcessor.formatResults(processed, () => {}, output);
                allOutput.push(...output);
            }
        } else if (parsedXml.DataSourceColumn) {
            const processed = await dataSourceColumnProcessor.processRootElement(parsedXml.DataSourceColumn);
            const output = [];
            await dataSourceColumnProcessor.formatResults(processed, () => {}, output);
            allOutput.push(...output);
        }
    };

    // Write output to file after all tests
    afterAll(() => {
        fs.appendFileSync(outputFile, allOutput.join('\n'));
    });

    // Get all XML files from the test data directory
    const testFiles = fs.readdirSync(path.join(__dirname, '../../test-data/DataSourceColumn'))
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

            await processDataSourceColumnFile(file.name);
            
            // Write all results to output file
            fs.appendFileSync(outputFile, allOutput.join('\n'));
            
            // Basic validation
            expect(allOutput.length).to.be.greaterThan(0);
            expect(allOutput.join('')).to.include('###');
            
            // Verify mandatory attributes are present
            const outputText = allOutput.join('');
            expect(outputText).to.include('| DSCLength |');
            expect(outputText).to.include('| DSCMandatory |');
            expect(outputText).to.include('| DSCPrecision |');
            expect(outputText).to.include('| DSCName |');
            expect(outputText).to.include('| DSCScale |');
            expect(outputText).to.include('| DSCType |');
            expect(outputText).to.include('| Type |');
        });
    });
});
