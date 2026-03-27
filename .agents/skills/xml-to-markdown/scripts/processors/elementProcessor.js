/**
 * tools/standalone/xml-to-markdown/src/processors/elementProcessor.js
 * =====================================================================
 * 
 * Purpose:
 *   Routes XML elements to their corresponding processor classes.
 *   Acts as the central dispatcher for the processor pattern.
 * 
 * Input:
 *   - XML element object with type identifier
 *   - Logger function for error reporting
 *   - Output array for collecting Markdown results
 * 
 * Output:
 *   - Processed element data via processor.processElement()
 *   - Markdown content appended to output array
 * 
 * Assumptions:
 *   - Element processors are registered in elementTypes.js
 *   - All processors extend BaseProcessor
 *   - Element type names match XML tag names (PascalCase)
 * 
 * Key Functions:
 *   - determineProcessorType(elementName) - Maps XML name to processor
 *   - processElement(element, type, log, output) - Routes to correct processor
 *   - processElementList(elements, type, log, output) - Batch processing
 * 
 * Usage:
 *   import { processElement, processElementList } from './elementProcessor.js';
 *   
 *   // Process single element
 *   await processElement(blockElement, 'Block', console.log, output);
 *   
 *   // Process array of elements
 *   await processElementList(triggerElements, 'Trigger', console.log, output);
 * 
 * Related:
 *   - BaseProcessor.js (abstract base class)
 *   - elementTypes.js (processor registry)
 * 
 * @module elementProcessor
 */

// Import the centralized registry of all element processors
// This maps element types to their corresponding processor functions
import { elementProcessors } from './elementTypes.js';

/**=====================================================
 * Determines the processor type from an XML element name
 * Maps XML element names to their corresponding processor types for execution
 * 
 * @param {string} elementName - XML element name to check and return associated processor to execute for that type of element
 * @returns {string} The corresponding processor type name (matches processor file names)
 * 
 * @example
 * // Basic element mapping
 * determineProcessorType('FormModule')  // returns 'formModuleProcessor'
 * determineProcessorType('Block')       // returns 'blockProcessor'
 * // Special case mappings
 * determineProcessorType('LOV')         // returns 'lovProcessor'
 * determineProcessorType('LOVColumn')   // returns 'lovColumnProcessor'
 * // Child element mapping
 * determineProcessorType('Item')        // returns 'itemProcessor'
 * determineProcessorType('Trigger')     // returns 'triggerProcessor'
**=====================================================*/
export function determineProcessorType(elementName) {
    // Convert to PascalCase for consistency
    const type = elementName.charAt(0).toUpperCase() + elementName.slice(1);
    return type;
}

/**=====================================================
 * Processes an element using its corresponding processor
 * @param {Object} element - The element to process
 * @param {string} type - The type of the element
 * @param {Function} log - Logging function
 * @param {Array} output - Array to collect output
 * @param {number} indentLevel - Current indentation level
 * @returns {Promise<void>}
**=====================================================*/
export async function processElement(element, type, log, output, indentLevel = 0) {
    try {
        // Determine the processor type from the element name
        const processorType = determineProcessorType(type);

        // Get the processor for this element type
        const processor = elementProcessors[processorType];
        if (!processor) {
            throw new Error(`No processor found for element type: ${processorType}`);
        }

        // Process the element using its specific processor
        // Individual processors will handle their own child elements if needed
        await processor.processElement(element, log, output, indentLevel);
    } catch (error) {
        log(`Error processing element ${type}: ${error.message}`);
        throw error;
    }
}

/**
 * Processes a list of elements of the same type.
 * This function handles both single elements and arrays of elements.
 * 
 * @param {Object|Array} elements - The element or array of elements to process
 * @param {string} elementType - The type of elements to process
 * @param {Function} log - Logging function
 * @param {Array} output - Output array to store results
 * @param {number} indentLevel - Current indentation level
 * @returns {Promise<void>}
 */
export async function processElementList(elements, elementType, log, output, indentLevel = 0) {
    if (!elements) return;

    const elementList = Array.isArray(elements) ? elements : [elements];

    for (const element of elementList) {
        await processElement(element, elementType, log, output, indentLevel);
    }
} 