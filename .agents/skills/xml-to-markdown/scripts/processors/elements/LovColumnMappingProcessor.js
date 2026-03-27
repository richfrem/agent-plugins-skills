/**
 * tools/standalone/xml-to-markdown/src/processors/elements/LovColumnMappingProcessor.js
 * ======================================================================================
 * 
 * Purpose:
 *   Processes LovColumnMapping elements. Maps LOV columns to form items,
 *   defining which LOV values populate which form fields on selection.
 * 
 * Key Attributes: Name, ReturnItem, DisplayWidth, Title
 * 
 * @module LovColumnMappingProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class LovColumnMappingProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('LovColumnMapping',
            // Mandatory attributes (from forms.xsd: Name, ReturnItem, Title, DisplayWidth)
            ['Name', 'ReturnItem', 'Title', 'DisplayWidth'],
            // Optional attributes (from forms.xsd: DirtyInfo, PersistentClientInfoLength)
            [
                'DirtyInfo',
                'PersistentClientInfoLength'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root LovColumnMapping element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--LovColumnMappingProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the LovColumnMapping
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--LovColumnMappingProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the LovColumnMapping
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--LovColumnMappingProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const lovColumnMappingProcessor = new LovColumnMappingProcessor(process.env.DEBUG === 'true');