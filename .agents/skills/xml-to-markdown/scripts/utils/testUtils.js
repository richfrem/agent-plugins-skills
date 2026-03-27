/**
 * tools/standalone/xml-to-markdown/src/utils/testUtils.js
 * =========================================================
 * 
 * Purpose:
 *   Testing utilities for processor validation. Provides helpers for
 *   loading test XML data and running element processor tests.
 * 
 * Exports:
 *   - loadTestData(): Load XML from file
 *   - runElementTest(): Execute processor test with XML data
 * 
 * @module testUtils
 */

import fs from 'fs';
import xml2js from 'xml2js';

/**
 * Loads test data from an XML file
 * @param {string} filePath - Path to the XML file
 * @returns {Promise<string>} XML data as string
 */
export async function loadTestData(filePath) {
    return fs.promises.readFile(filePath, 'utf8');
}

/**
 * Creates a parser specifically for test data XML files
 * @returns {Object} Configured XML parser for test data
 */
function createTestDataParser() {
    return new xml2js.Parser({
        explicitArray: true,
        mergeAttrs: false,
        attrkey: '$',
        normalizeTags: false,
        trim: true
    });
}

/**
 * Runs a test for a specific element type
 * @param {string} testDataPath - Path to the test data XML file
 * @param {Object} processor - The processor instance to use
 * @param {Function} getAttributes - Function to get attributes from an element
 * @param {Function} log - Logging function
 * @returns {Promise<void>}
 */
export async function runElementTest(testDataPath, processor, getAttributes, log) {
    try {
        // Read and parse the XML file
        const xmlData = await loadTestData(testDataPath);
        const parser = createTestDataParser();
        const parsedXml = await parser.parseStringPromise(xmlData);

        // Create output array
        const output = [];

        // Process the element using the provided processor
        await processor.processElement(parsedXml, log, output, 0);

        // Log the output
        console.log('\nOutput:');
        console.log(output.join(''));
    } catch (error) {
        console.error(`Error running test: ${error.message}`);
        throw error;
    }
} 