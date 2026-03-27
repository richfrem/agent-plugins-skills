/**
 * tools/standalone/xml-to-markdown/src/utils/attributeUtils.js
 * =============================================================
 * 
 * Purpose:
 *   XML attribute extraction and normalization utilities. Handles
 *   multiple parser formats and provides case-insensitive attribute access.
 * 
 * Exports:
 *   - getAttributes(): Extract attributes from element
 *   - getAttribute(): Get single attribute by name
 *   - normalizeAttributes(): Convert to camelCase
 *   - processElementAttributes(): Format as markdown
 * 
 * @module attributeUtils
 */

/**
 * Retrieves attributes from an XML element, handling multiple XML parser formats
 * @param {Object} element - The XML element
 * @returns {Object} The attributes object
 * @example
 * const element = { $: { name: 'test', value: 123 } };
 * const attrs = getAttributes(element); // Returns { name: 'test', value: 123 }
 */
export function getAttributes(element) {
    if (!element) return {};

    // Handle direct attributes
    if (element.$) {
        return element.$;
    }

    // Handle attributes stored directly on the element
    const attributes = {};
    for (const [key, value] of Object.entries(element)) {
        if (key !== '_' && key !== '$' && typeof value !== 'object') {
            attributes[key] = value;
        }
    }

    return attributes;
}

/**
 * Converts attribute names to a consistent camelCase format
 * @param {Object} attributes - The attributes object
 * @returns {Object} The normalized attributes object
 * @example
 * const attrs = { 'CHARACTER_CELL_WIDTH': 10, 'REAL_UNIT': 'points' };
 * const normalized = normalizeAttributes(attrs); // Returns { characterCellWidth: 10, realUnit: 'points' }
 */
export function normalizeAttributes(attributes) {
    if (!attributes) {
        return {};
    }

    const normalized = {};
    for (const [key, value] of Object.entries(attributes)) {
        // Convert to camelCase
        const normalizedKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
        normalized[normalizedKey] = value;
    }
    return normalized;
}

/**
 * Gets a specific attribute value with case-insensitive matching
 * @param {Object} element - The XML element
 * @param {string} attributeName - The name of the attribute to get
 * @returns {string|undefined} The attribute value or undefined if not found
 * @example
 * const element = { $: { 'CharacterCellWidth': 10 } };
 * const width = getAttribute(element, 'characterCellWidth'); // Returns 10
 */
export function getAttribute(element, attributeName) {
    const attributes = getAttributes(element);
    const normalizedAttributes = normalizeAttributes(attributes);

    // Try exact match first
    if (attributeName in normalizedAttributes) {
        return normalizedAttributes[attributeName];
    }

    // Try case-insensitive match
    const lowerAttributeName = attributeName.toLowerCase();
    for (const [key, value] of Object.entries(normalizedAttributes)) {
        if (key.toLowerCase() === lowerAttributeName) {
            return value;
        }
    }

    return undefined;
}

/**
 * Extracts and normalizes all attributes from an element
 * @param {Object} element - The XML element
 * @returns {Object} Normalized attributes object
 * @example
 * const element = { $: { 'CHARACTER_CELL_WIDTH': 10 } };
 * const attrs = extractAttributes(element); // Returns { characterCellWidth: 10 }
 */
export function extractAttributes(element) {
    const attributes = getAttributes(element);
    return normalizeAttributes(attributes);
}

/**
 * Processes element attributes, handling both mandatory and optional attributes
 * 
 * @param {Object} element - The element to process
 * @param {Function} getAttributes - Function to get attributes from an element
 * @param {Function} log - Logging function
 * @param {Array} output - Output array to store results
 * @param {number} indentLevel - Current indentation level
 * @param {Array} mandatoryAttributes - Array of mandatory attribute names
 * @param {Array} optionalAttributes - Array of optional attribute names
 * @returns {Object} The processed attributes
 */
export function processElementAttributes(element, getAttributes, log, output, indentLevel = 0, mandatoryAttributes = [], optionalAttributes = []) {
    try {
        const indent = '  '.repeat(indentLevel);
        const attributes = getAttributes(element);

        // Process mandatory attributes
        if (mandatoryAttributes.length > 0) {
            output.push(`${indent}### Required Attributes\n`);
            for (const attr of mandatoryAttributes) {
                if (!attributes[attr]) {
                    log(`Warning: Missing mandatory attribute '${attr}'`);
                }
                output.push(`${indent}- **${attr}:** ${attributes[attr] || 'Not Set'}\n`);
            }
            output.push('\n');
        }

        // Process optional attributes
        if (optionalAttributes.length > 0) {
            output.push(`${indent}### Optional Attributes\n`);
            for (const attr of optionalAttributes) {
                if (attributes[attr]) {
                    output.push(`${indent}- **${attr}:** ${attributes[attr]}\n`);
                }
            }
            output.push('\n');
        }

        return attributes;
    } catch (error) {
        log(`Error processing attributes: ${error.message}`);
        throw error;
    }
} 