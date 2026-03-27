/**
 * tools/standalone/xml-to-markdown/src/processors/elements/FontProcessor.js
 * ==========================================================================
 * 
 * Purpose:
 *   Processes Font elements. Font definitions with name, size, weight, and
 *   style attributes for text rendering configuration.
 * 
 * Key Attributes: FontName, FontSize, FontWeight, FontStyle
 * 
 * @module FontProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class FontProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Font',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (all other attributes from forms.xsd)
            [
                'DirtyInfo'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }


    /**
     * Process the root Font element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--FontProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Font
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--FontProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Font
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--FontProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const fontProcessor = new FontProcessor(process.env.DEBUG === 'true');