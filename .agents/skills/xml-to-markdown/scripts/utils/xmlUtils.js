/**
 * tools/standalone/xml-to-markdown/src/utils/xmlUtils.js
 * =======================================================
 * 
 * Purpose:
 *   XML parsing utilities for Oracle Forms XML files. Configures xml2js parser
 *   with optimal settings for processing FMB/MMB/OLB exported XML.
 * 
 * Exports:
 *   - createTestParser(): Parser for test XML files
 *   - parseXML(): Parse XML string to JS object
 *   - getElementName(): Extract element tag name
 * 
 * @module xmlUtils
 */

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
export async function parseXml(xmlData) {
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

/**
 * Extracts PL/SQL code from a node
 * @param {Object} node - The node containing PL/SQL code
 * @returns {string} Extracted and cleaned PL/SQL code
 */
/*
export function extractPLSQL(node) {
    if (!node || !node.ProgramUnit) return '';
    
    const programUnit = Array.isArray(node.ProgramUnit) ? node.ProgramUnit[0] : node.ProgramUnit;
    if (!programUnit || !programUnit.Text) return '';
    
    const text = Array.isArray(programUnit.Text) ? programUnit.Text[0] : programUnit.Text;
    return text.trim();
}
*/

/**
 * Extracts form properties from parsed XML
 * @param {Object} parsedXML - The parsed XML object
 * @returns {Object} Form properties
 */
/*
export function extractFormProperties(parsedXML) {
    if (!parsedXML.module || !parsedXML.module.FormModule) return {};
    
    const formModule = parsedXML.module.FormModule[0];
    const attrs = getAttributes(formModule);
    return {
        name: attrs.Name || '',
        title: attrs.Title || '',
        coordinate: formModule.Coordinate ? formModule.Coordinate[0] : null
    };
}
*/
/**
 * Extracts blocks from parsed XML
 * @param {Object} parsedXML - The parsed XML object
 * @returns {Array} Array of blocks
 */
/**
export function extractBlocks(parsedXML) {
    if (!parsedXML.module || !parsedXML.module.FormModule) return [];
    
    const formModule = parsedXML.module.FormModule[0];
    return formModule.Block || [];
}
 */

/**
 * Extracts items from a block
 * @param {Object} block - The block containing items
 * @returns {Array} Array of items
 */
/*
export function extractItems(block) {
    return block.Item || [];
}

/**
 * Extracts triggers from a node
 * @param {Object} node - The node containing triggers
 * @returns {Array} Array of triggers
 */
/*
export function extractTriggers(node) {
    return node.Trigger || [];
}
*/


/**
 * Determines the module type from XML content
 * @param {string} xmlContent - The XML content to analyze
 * @returns {string} The module type (FormModule, MenuModule, or ObjectLibrary)
 * @throws {Error} If the module type cannot be determined
 */
/*
export function determineModuleType(xmlContent) {
    if (xmlContent.includes('<FormModule')) return 'FormModule';
    if (xmlContent.includes('<MenuModule')) return 'MenuModule';
    if (xmlContent.includes('<ObjectLibrary')) return 'ObjectLibrary';
    throw new Error('Unknown module type: XML must contain FormModule, MenuModule, or ObjectLibrary as root element');
} 
    */
