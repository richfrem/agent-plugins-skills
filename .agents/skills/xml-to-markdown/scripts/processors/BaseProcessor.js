/**
 * tools/standalone/xml-to-markdown/src/processors/BaseProcessor.js
 * ==================================================================
 * 
 * Purpose:
 *   Abstract base class for all Oracle Forms XML element processors.
 *   Provides common functionality for parsing XML elements, extracting
 *   attributes, formatting PL/SQL code, and generating Markdown output.
 * 
 * Input:
 *   - Parsed XML element objects (from xml2js parser)
 *   - Element type configuration (mandatory/optional attributes)
 * 
 * Output:
 *   - Structured element data with attributes and children
 *   - Formatted Markdown strings via formatResults()
 * 
 * Assumptions:
 *   - XML has been parsed by xml2js with explicitArray: true
 *   - Attributes are stored in element.$ property
 *   - Text content is stored in element._ property
 *   - Child elements are stored in element.$$ property
 * 
 * Key Classes:
 *   - BaseProcessor: Abstract base with shared processing logic
 *   - ELEMENT_TYPE: Enum for XML structure classification
 * 
 * Key Methods:
 *   - processAttributes(element, log) - Extracts and validates attributes
 *   - processChildren(element) - Recursively processes nested elements
 *   - formatResults(element, log, output) - Generates Markdown output
 *   - formatCodeByType(code, type) - Formats SQL/PLSQL code blocks
 *   - getProcessorForType(type) - Dynamically loads element-specific processor
 * 
 * Usage:
 *   // Create a custom processor by extending BaseProcessor
 *   class BlockProcessor extends BaseProcessor {
 *     constructor() {
 *       super('Block', ['Name'], ['QueryDataSourceName', 'DMLDataName']);
 *     }
 *   }
 * 
 * Related:
 *   - elementProcessor.js (routing logic)
 *   - elementTypes.js (processor registry)
 *   - All element processors in ./elements/ directory
 * 
 * @module BaseProcessor
 */

// Cache for utility functions
const utilsCache = new Map();

/**
 * Element type constants
 */
export const ELEMENT_TYPE = {
    SIMPLE: 1,                    // <simple>test</simple>
    SELF_CLOSING_WITH_ATTRIBUTES: 2,  // <WithAttributes attribute='test'/>
    WITH_CHILD_ELEMENTS: 3,       // <WithNestedElements><nested>test</nested></WithNestedElements>
    WITH_ATTRIBUTES_AND_CHILDREN: 4,  // <WithAttributesAndNestedElements attrib='1'><nested2>more text</nested2></WithAttributesAndNestedElements>
    UNKNOWN: 0                    // Invalid/unknown type
};

/**
 * Base class for all element processors
 * Provides common functionality for processing elements and their attributes
 */
export class BaseProcessor {
    // Static arrays defining code-containing attributes and elements
    static codeAttributes = [
        'ProgramUnitText',
        'TriggerText',
        'MenuItemCode',
        'RecordGroupQuery',
        'LovQuery',
        'WhereClause',
        'OrderByClause',
        'DefaultValue',
        'InitialValue',
        'ValidateFromList',
        'GraphicsText',
        'ListValues',
        'DMLDataName',
        'StartupCode',
        'Text',
        'Prompt',
        'Comment',
        'UpdateProcedure',
        'InsertProcedure',
        'QueryDataSourceName',
        'DeleteProcedure',
        'QueryProcedure',
        'PostQuery',
        'PreQuery',
        'PostInsert',
        'PostUpdate',
        'PostDelete',
        'PreInsert',
        'PreUpdate',
        'PreDelete',
        'JoinCondition'
    ];

    static codeElements = [
        'Code',
        'Query'
    ];

    /**
     * Creates a new BaseProcessor
     * @param {string} elementType - The type of element this processor handles
     * @param {Array} mandatoryAttributes - Array of mandatory attribute names
     * @param {Array} optionalAttributes - Array of optional attribute names
     * @param {Object} options - Additional configuration options
     * @param {string} options.defaultCodeType - Default code type for formatting (e.g., 'SQL', 'PLSQL')
     */
    constructor(elementType, mandatoryAttributes = [], optionalAttributes = [], {
        defaultCodeType = 'PLSQL'
    } = {}) {
        this.elementType = elementType;
        this.mandatoryAttributes = mandatoryAttributes;
        this.optionalAttributes = optionalAttributes;
        this.defaultCodeType = defaultCodeType;
        this.debug = false;
    }

    /**
     * Gets utility functions from attributeUtils.js if not already imported
     * @returns {Promise<Object>} The utility functions
     */
    async getAttributeUtils() {
        if (utilsCache.has('attributeUtils')) {
            return utilsCache.get('attributeUtils');
        }
        try {
            const utils = await import('../utils/attributeUtils.js');
            utilsCache.set('attributeUtils', utils);
            return utils;
        } catch (error) {
            console.warn('Failed to import attributeUtils:', error);
            return {};
        }
    }

    /**
     * Gets utility functions from codeUtils.js if not already imported
     * @returns {Promise<Object>} The utility functions
     */
    async getCodeUtils() {
        if (utilsCache.has('codeUtils')) {
            return utilsCache.get('codeUtils');
        }
        try {
            const utils = await import('../utils/codeUtils.js');
            utilsCache.set('codeUtils', utils);
            return utils;
        } catch (error) {
            console.warn('Failed to import codeUtils:', error);
            return {};
        }
    }

    /**
     * Gets text content and formats it if needed
     * @param {string|number} textContent - The text content to format
     * @param {string} [elementTypeOrAttributeName] - Optional element type name or attribute name to check for code formatting
     * @returns {Promise<string|number>} The text content, formatted if needed
     * 
     * @example
     * // For element text content:
     * await getFormattedTextContent(element._)  // Checks if element type is in codeElements
     * 
     * // For attribute values:
     * await getFormattedTextContent(value, 'ProgramUnitText')  // Checks if attribute is in codeAttributes
     */
    async getFormattedTextContent(textContent, elementTypeOrAttributeName) {
        if (!textContent) return undefined;

        // Check if this is a code element type or a code attribute
        const isCodeElement = BaseProcessor.codeElements.includes(this.elementType);
        const isCodeAttribute = elementTypeOrAttributeName && BaseProcessor.codeAttributes.includes(elementTypeOrAttributeName);

        // If either the element type or attribute name indicates code, format it
        if (isCodeElement || isCodeAttribute) {
            return await this.formatCodeByType(textContent, this.defaultCodeType);
        }

        // Otherwise just return the text content
        return textContent;
    }

    /**
     * Gets attributes from an element
     * @param {Object} element - The element to get attributes from
     * @returns {Object} The attributes
     */
    getAttributes(element) {
        const attributes = {};

        // Helper function to process a single attribute
        const processAttribute = (name) => {
            if (element[name] && element[name][0]) {
                attributes[name] = this.getTextContent(element[name][0]);
            }
        };

        // Process mandatory attributes
        this.mandatoryAttributes.forEach(processAttribute);

        // Process optional attributes
        this.optionalAttributes.forEach(processAttribute);

        return attributes;
    }

    /**
     * Formats code based on its type
     * @param {string} code - The code to format
     * @param {string} [type] - The type of code (e.g., 'SQL', 'PLSQL')
     * @param {number} [indentLevel=0] - The indentation level
     * @returns {string} Formatted code
     */
    async formatCodeByType(code, type, indentLevel = 0) {
        if (!code) return '';

        const { formatSQL, formatPLSQL, formatCode } = await this.getCodeUtils();

        switch (type?.toUpperCase()) {
            case 'SQL':
                return formatSQL(code);
            case 'PLSQL':
                return formatPLSQL(code);
            default:
                return formatCode(code, indentLevel);
        }
    }

    /**
     * Handles code attributes and elements consistently
     * @param {Object} element - The element containing code
     * @param {string} codeAttribute - The name of the code attribute
     * @param {string} codeType - The type of code (e.g., 'SQL', 'PLSQL')
     * @param {number} indentLevel - The indentation level
     * @returns {Promise<string>} Formatted code
     */
    async handleCode(element, codeAttribute, codeType = 'PLSQL', indentLevel = 0) {
        if (!element) return '';

        // Get attributes
        const { getAttributes } = await this.getAttributeUtils();
        const attributes = getAttributes(element);

        // Check if code is in attributes
        if (attributes[codeAttribute]) {
            return await this.formatCodeByType(attributes[codeAttribute], codeType, indentLevel);
        }

        // Check if code is in child elements
        const children = await this.processChildren(element);
        for (const child of children) {
            if (child.type === codeAttribute) {
                return await this.formatCodeByType(child.value, codeType, indentLevel);
            }
        }

        return '';
    }

    /**
     * Checks if this element is of the type this processor handles
     * @param {Object} element - The element to check
     * @returns {boolean} True if this processor can handle the element
     * @throws {Error} If element is null or not of the expected type
     */
    isMyType(element) {
        if (!element) {
            throw new Error(`Cannot process null element for ${this.elementType}`);
        }

        // For now, just return true since we're getting the right element from the test
        return true;
    }

    /**
     * Process and validate element attributes
     * @param {Object} element - The element to process attributes from
     * @param {Function} log - Logger function for warnings
     * @returns {Object} Processed attributes
     */
    async processAttributes(element, log) {
        if (!element || !element.$) {
            return {};
        }

        const attributes = {};
        const missingMandatory = [];

        // Process mandatory attributes
        for (const attr of this.mandatoryAttributes) {
            if (element.$[attr] !== undefined) {
                attributes[attr] = element.$[attr];
            } else {
                missingMandatory.push(attr);
            }
        }

        // Log warnings for missing mandatory attributes
        if (missingMandatory.length > 0) {
            log('warning', `${this.elementType} is missing mandatory attributes: ${missingMandatory.join(', ')}`);
        }

        // Process optional attributes
        for (const attr of this.optionalAttributes) {
            if (element.$[attr] !== undefined) {
                attributes[attr] = element.$[attr];
            }
        }

        // Handle special attribute types (like code)
        for (const [key, value] of Object.entries(attributes)) {
            if (this.constructor.codeAttributes.includes(key)) {
                attributes[key] = await this.formatCodeByType(value, this.defaultCodeType);
            }
        }

        return attributes;
    }

    /**
     * Process child elements
     * @param {Object} element - The element to process children for
     * @returns {Promise<Array>} - Array of processed children
     */
    async processChildren(element) {
        const children = [];

        // Handle child elements that are direct properties
        for (const [key, value] of Object.entries(element)) {
            // Skip special properties and non-object values
            if (key === '$' || key === '$$' || typeof value !== 'object' || value === null) {
                continue;
            }

            // Handle both single objects and arrays of objects
            const childElements = Array.isArray(value) ? value : [value];

            for (const childElement of childElements) {
                // Get the element type from the key or value
                const elementType = this.getElementType(childElement, key);
                if (!elementType) {
                    continue;
                }

                try {
                    // Get the processor for this child type
                    const childProcessor = await this.getProcessorForType(elementType);
                    if (!childProcessor) {
                        console.warn(`No processor found for child type: ${elementType}`);
                        continue;
                    }

                    // Process the child element
                    const processedChild = await childProcessor.processElement(childElement);
                    if (processedChild) {
                        children.push(processedChild);
                    }
                } catch (error) {
                    console.error(`Error processing child element ${elementType}:`, error);
                }
            }
        }

        return children;
    }

    /**
     * Determines the type of XML element based on its structure
     * @param {Object} element - The element to analyze
     * @returns {number} The element type (1-5)
     * 
     * Types of elements:
     * 1: Simple content - <simple>test</simple>
     * 2: Self-closing with attributes - <WithAttributes attribute='test'/>
     * 3: Element with child elements - <WithNestedElements><nested>test</nested></WithNestedElements>
     * 4: Element with attributes and child elements - <WithAttributesAndNestedElements attrib='1'><nested2>more text</nested2></WithAttributesAndNestedElements>
     */
    getElementType(element) {
        if (!element) return ELEMENT_TYPE.UNKNOWN;

        const hasAttributes = element.$ && Object.keys(element.$).length > 0;
        const hasTextContent = element._ !== undefined;
        const hasChildElements = Object.keys(element).some(key =>
            key !== '$' && key !== '_' && (
                (Array.isArray(element[key]) && key !== '$$') || // Regular child elements
                (key === '$$' && Object.keys(element[key]).length > 0) // Children in $$ property
            )
        );

        // Type 1: Simple content - <simple>test</simple>
        if (!hasAttributes && !hasChildElements && hasTextContent) {
            return ELEMENT_TYPE.SIMPLE;
        }
        // Type 2: Self-closing with attributes - <WithAttributes attribute='test'/>
        if (hasAttributes && !hasTextContent && !hasChildElements) {
            return ELEMENT_TYPE.SELF_CLOSING_WITH_ATTRIBUTES;
        }
        // Type 3: Element with child elements - <WithNestedElements><nested>test</nested></WithNestedElements>
        if (!hasAttributes && hasChildElements && !hasTextContent) {
            return ELEMENT_TYPE.WITH_CHILD_ELEMENTS;
        }
        // Type 4: Element with attributes and child elements - <WithAttributesAndNestedElements attrib='1'><nested2>more text</nested2></WithAttributesAndNestedElements>
        if (hasAttributes && hasChildElements) {
            return ELEMENT_TYPE.WITH_ATTRIBUTES_AND_CHILDREN;
        }

        return ELEMENT_TYPE.UNKNOWN;
    }

    /**
     * Process the root element
     * @param {Object} element - The XML element to process
     * @returns {Promise<Object>} The processed element data
     */
    async processRootElement(element) {
        if (!element) {
            return element;
        }

        console.log('--BaseProcessor processRootElement element:', JSON.stringify(element, null, 2));

        // Determine the type of the element
        const elementType = this.getElementType(element);
        console.log('--BaseProcessor element type:', elementType);

        if (elementType === ELEMENT_TYPE.SIMPLE) {
            //<simple>test</simple>
            console.log(`--BaseProcessor using ELEMENT_TYPE.SIMPLE`);

            return {
                type: this.elementType,
                elementType: elementType,
                attributes: {},  // has no attributes
                value: await this.getFormattedTextContent(element._), // has text content
                $$: element.$$ // preserve child elements
            };
        }
        else if (elementType === ELEMENT_TYPE.SELF_CLOSING_WITH_ATTRIBUTES) {
            //<WithAttributes attribute='test'/>
            console.log(`--BaseProcessor using ELEMENT_TYPE.SELF_CLOSING_WITH_ATTRIBUTES`);
            const attrs = await this.processAttributes(element, console.warn);
            return {
                type: this.elementType,
                elementType: elementType,
                attributes: attrs,  // has attributes but no text content
                value: undefined, // has no text content or children
                $$: element.$$ // preserve child elements
            };
        }
        else if (elementType === ELEMENT_TYPE.WITH_CHILD_ELEMENTS) {
            //<WithNestedElements><nested>test</nested></WithNestedElements>
            console.log(`--BaseProcessor using ELEMENT_TYPE.WITH_CHILD_ELEMENTS`);
            return {
                type: this.elementType,
                elementType: elementType,
                attributes: {}, // has no attributes
                value: await this.processChildren(element), // has children
                $$: element.$$ // preserve child elements
            };
        }
        else if (elementType === ELEMENT_TYPE.WITH_ATTRIBUTES_AND_CHILDREN) {
            //<WithAttributesAndNestedElements attrib='1'><nested2>more text</nested2></WithAttributesAndNestedElements>
            console.log(`--BaseProcessor using ELEMENT_TYPE.WITH_ATTRIBUTES_AND_CHILDREN`);
            const attrs = await this.processAttributes(element, console.warn);
            return {
                type: this.elementType,
                elementType: elementType,
                attributes: attrs,  // has attributes
                value: await this.processChildren(element), // has children
                $$: element.$$ // preserve child elements
            };
        }
        else {
            throw new Error(`Invalid element structure for ${this.elementType}`);
        }
    }

    /**
     * Format attribute results into markdown tables
     * @param {Object} element - The element containing attributes
     * @param {Array} output - Output array
     */
    async formatAttributeResults(element, output) {
        // Get attributes from either element.$ or element.attributes
        const attributes = element.$ || element.attributes || {};

        // Format mandatory attributes if present
        const mandatoryAttrs = this.mandatoryAttributes.filter(attr => attributes[attr]);
        if (mandatoryAttrs.length > 0) {
            output.push('#### Mandatory Attributes');

            // First output non-code attributes in a table
            const nonCodeAttrs = mandatoryAttrs.filter(attr => !this.constructor.codeAttributes.includes(attr));
            if (nonCodeAttrs.length > 0) {
                output.push('| Attribute | Value |\n|-----------|-------|');
                for (const attr of nonCodeAttrs) {
                    output.push(`| ${attr} | ${attributes[attr]} |`);
                }
                output.push('');  // Empty line after table
            }

            // Then output code attributes outside the table
            const codeAttrs = mandatoryAttrs.filter(attr => this.constructor.codeAttributes.includes(attr));
            for (const attr of codeAttrs) {
                output.push(`**${attr}**:\n\`\`\`sql\n${attributes[attr]}\n\`\`\`\n`);
            }
        }

        // Format optional attributes if present
        const optionalAttrs = this.optionalAttributes.filter(attr => attributes[attr]);
        if (optionalAttrs.length > 0) {
            output.push('#### Optional Attributes');

            // First output non-code attributes in a table
            const nonCodeAttrs = optionalAttrs.filter(attr => !this.constructor.codeAttributes.includes(attr));
            if (nonCodeAttrs.length > 0) {
                output.push('| Attribute | Value |\n|-----------|-------|');
                for (const attr of nonCodeAttrs) {
                    output.push(`| ${attr} | ${attributes[attr]} |`);
                }
                output.push('');  // Empty line after table
            }

            // Then output code attributes outside the table
            const codeAttrs = optionalAttrs.filter(attr => this.constructor.codeAttributes.includes(attr));
            for (const attr of codeAttrs) {
                output.push(`**${attr}**:\n\`\`\`sql\n${attributes[attr]}\n\`\`\`\n`);
            }
        }

        // Format any remaining attributes that aren't in mandatory or optional lists
        const allAttrs = Object.keys(attributes);
        const remainingAttrs = allAttrs.filter(attr =>
            !mandatoryAttrs.includes(attr) &&
            !optionalAttrs.includes(attr)
            //!optionalAttrs.includes(attr) &&
            //attr !== 'Name' // Skip Name as it's already handled
        );

        if (remainingAttrs.length > 0) {
            output.push('#### Additional Attributes');

            // First output non-code attributes in a table
            const nonCodeAttrs = remainingAttrs.filter(attr => !this.constructor.codeAttributes.includes(attr));
            if (nonCodeAttrs.length > 0) {
                output.push('| Attribute | Value |\n|-----------|-------|');
                for (const attr of nonCodeAttrs) {
                    output.push(`| ${attr} | ${attributes[attr]} |`);
                }
                output.push('');  // Empty line after table
            }

            // Then output code attributes outside the table
            const codeAttrs = remainingAttrs.filter(attr => this.constructor.codeAttributes.includes(attr));
            for (const attr of codeAttrs) {
                output.push(`**${attr}**:\n\`\`\`sql\n${attributes[attr]}\n\`\`\`\n`);
            }
        }
    }

    /**
     * Format simple text content into a code block
     * @param {string} content - The text content to format
     * @param {Array} output - Output array
     */
    formatSimpleContent(content, output) {
        if (content && typeof content === 'string') {
            output.push('#### Content\n```\n' + content + '\n```\n');
        }
    }

    /**
     * Format the results of processing an element
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        // Add the element type header
        output.push(`### ${this.elementType}`);

        // Format attributes
        await this.formatAttributeResults(element, output);

        // Format content
        this.formatSimpleContent(element.value, output);

        // Process children - collect all child elements from $$ property
        const children = [];
        if (element.$$) {
            for (const [type, typeChildren] of Object.entries(element.$$)) {
                if (Array.isArray(typeChildren)) {
                    for (const child of typeChildren) {
                        if (child && typeof child === 'object') {
                            children.push({ ...child, type });
                        }
                    }
                } else if (typeChildren && typeof typeChildren === 'object') {
                    children.push({ ...typeChildren, type });
                }
            }
        }

        if (children.length > 0) {
            await this.formatChildrenResults(children, log, output);
        }
    }

    /**
     * Format child elements recursively
     * @param {Array} children - Array of child elements
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatChildrenResults(children, log, output) {
        if (children && Array.isArray(children) && children.length > 0) {
            // Group children by type
            const groupedChildren = children.reduce((acc, child) => {
                if (!acc[child.type]) {
                    acc[child.type] = [];
                }
                acc[child.type].push(child);
                return acc;
            }, {});

            // Format each group of children
            for (const [type, typeChildren] of Object.entries(groupedChildren)) {
                for (const child of typeChildren) {
                    // Get the appropriate processor for this child type
                    const processor = await this.getProcessorForType(type);
                    if (processor) {
                        // Process the child element
                        const processedChild = await processor.processRootElement(child);

                        // Format the child using the processor's formatResults method
                        await processor.formatResults(processedChild, log, output);

                        // Recursively process any nested children
                        if (processedChild.children && processedChild.children.length > 0) {
                            await this.formatChildrenResults(processedChild.children, log, output);
                        }
                    }
                }
            }
        }
    }

    /**
     * Format a basic element without a specific processor
     * @param {Object} element - The element to format
     * @param {number} indentLevel - The current indentation level
     * @returns {Array<string>} Formatted output lines
     */
    formatBasicElement(element, indentLevel = 0) {
        const output = [];
        const indent = '  '.repeat(indentLevel);

        output.push(`${indent}### ${element.type}`);
        if (element.attributes && Object.keys(element.attributes).length > 0) {
            for (const [key, value] of Object.entries(element.attributes)) {
                output.push(`${indent}  ${key}: ${value}`);
            }
        }

        if (element.value) {
            output.push(`${indent}  Content: ${element.value}`);
        }

        return output;
    }

    /**
     * Gets a processor for a given element type
     * @param {string} type - The element type
     * @returns {Promise<BaseProcessor|undefined>} The processor instance
     */
    async getProcessorForType(type) {
        try {
            console.log(`--BaseProcessor getProcessorForType called for type: ${type}`);
            const { elementProcessors } = await import('./elementTypes.js');
            const processor = await elementProcessors[type];
            console.log(`--BaseProcessor got processor for ${type}:`, processor ? 'Found' : 'Not found');
            return processor;
        } catch (error) {
            console.warn(`Failed to get processor for type ${type}:`, error);
            return undefined;
        }
    }
} 