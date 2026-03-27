import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import xml2js from 'xml2js';
import { getAttributes } from '../../src/utils/attributeUtils.js';
import { getElementCodeAndType } from '../../src/utils/codeUtils.js';
import { formatCode } from '../../src/utils/codeUtils.js';
import { log } from '../../src/utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Loads and parses the test data XML file for a specific element type
 * @param {string} elementType - The type of element to load test data for
 * @returns {Promise<Object>} The parsed XML data
 */
export async function loadTestData(elementType) {
    const xmlPath = path.join(__dirname, '../../test-data', elementType, `${elementType.toLowerCase()}.xml`);
    console.log(`Loading test data from: ${xmlPath}`);
    const xml = await fs.promises.readFile(xmlPath, 'utf8');
    const parser = new xml2js.Parser();
    return parser.parseStringPromise(xml);
}

/**
 * Creates a processor function with all required dependencies
 * @param {Function} processor - The processor function to wrap
 * @returns {Function} A function that takes input and returns processed output
 */
export function createProcessor(processor) {
    return (input) => {
        const output = [];
        processor(input, getAttributes, getElementCodeAndType, formatCode, log, output);
        return output.join('');
    };
}

/**
 * Runs a test for an element processor
 * @param {string} elementType - The type of element being tested
 * @param {Function} processor - The processor function to test
 * @param {Function} getAttributes - Function to get element attributes
 * @param {Function} log - Logging function
 */
export async function runElementTest(elementType, processor, getAttributes, log) {
    try {
        const testData = await loadTestData(elementType);
        console.log('Test data loaded:', JSON.stringify(testData, null, 2));
        
        // Extract elements from the XML structure
        const elements = testData.Module.FormModule[0][elementType] || [];
        console.log(`Found ${elements.length} ${elementType} elements to test`);
        
        for (const element of elements) {
            const output = [];
            processor(element, getAttributes, log, output);
            const result = output.join('\n');
            
            // Log the result for manual verification
            console.log(`\n${elementType} Test Result:`);
            console.log(result);
        }
    } catch (error) {
        console.error(`Error running ${elementType} test:`, error);
        throw error;
    }
}

export { getAttributes, getElementCodeAndType, formatCode, log }; 