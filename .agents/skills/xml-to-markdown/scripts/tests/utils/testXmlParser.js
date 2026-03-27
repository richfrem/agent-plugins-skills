import xml2js from 'xml2js';

/**
 * Creates a configured XML parser for test files
 * @returns {Object} Configured XML parser
 */
export function createTestParser() {
    return new xml2js.Parser({
        explicitArray: true, // Preserve arrays
        mergeAttrs: false, // Keep attributes separate
        attrkey: '$', // Store attributes in $ property
        normalizeTags: false, // Preserve tag case
        normalize: true, // Normalize whitespace
        trim: true, // Trim whitespace
        explicitChildren: true, // Preserve empty elements
        valuekey: 'value', // Store child elements in value property
        valueProcessors: [xml2js.processors.parseNumbers, xml2js.processors.parseBooleans],
        attrNameProcessors: [xml2js.processors.stripPrefix],
        tagNameProcessors: [xml2js.processors.stripPrefix],
        charkey: '_' // Store character data in _ property
    });
}

/**
 * Parses test XML data
 * @param {string} xmlData - XML content to parse
 * @returns {Promise<Object>} Parsed XML data
 */
export async function parseTestXml(xmlData) {
    const parser = createTestParser();
    
    return new Promise((resolve, reject) => {
        parser.parseString(xmlData, (err, result) => {
            if (err) {
                reject(err);
                return;
            }
            resolve(result);
        });
    });
} 