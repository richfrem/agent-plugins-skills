/**
 * tools/standalone/xml-to-markdown/src/processors/elements/ListItemElementProcessor.js
 * =====================================================================================
 * 
 * Purpose:
 *   Processes ListItemElement within List Items. Individual options in a
 *   dropdown list, poplist, or T-list with label and value pairs.
 * 
 * Key Attributes: Name (label), ListElementValue
 * 
 * @module ListItemElementProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ListItemElementProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('ListItemElement',
            // Mandatory attributes (from forms.xsd: Index, Name, Value)
            ['Index', 'Name', 'Value'],
            // Optional attributes (none in forms.xsd for ListItemElement)
            [],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root ListItemElement element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ListItemElementProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the ListItemElement
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ListItemElementProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the ListItemElement
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ListItemElementProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const listItemElementProcessor = new ListItemElementProcessor(process.env.DEBUG === 'true');