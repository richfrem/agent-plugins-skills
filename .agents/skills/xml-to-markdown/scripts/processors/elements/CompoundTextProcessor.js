/**
 * tools/standalone/xml-to-markdown/src/processors/elements/CompoundTextProcessor.js
 * ==================================================================================
 * 
 * Purpose:
 *   Processes CompoundText elements within Graphics. Contains styled text
 *   segments for rich text rendering in boilerplate graphics.
 * 
 * Child Elements: TextSegment
 * 
 * @module CompoundTextProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class CompoundTextProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('CompoundText',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd: DirtyInfo, SubclassSubObject)
            [
                'DirtyInfo',
                'SubclassSubObject'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root CompoundText element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--CompoundTextProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the CompoundText
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--CompoundTextProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a CompoundText element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--CompoundTextProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const compoundTextProcessor = new CompoundTextProcessor(process.env.DEBUG === 'true');