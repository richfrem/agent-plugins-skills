/**
 * tools/standalone/xml-to-markdown/src/processors/elements/EventProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processes Event elements. JavaBean event handlers for Java components
 *   integrated into Oracle Forms.
 * 
 * Key Attributes: EventName, FireInEnterQuery
 * 
 * @module EventProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class EventProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Event',
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
     * Process the root Event element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--EventProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Event
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--EventProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Event
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--EventProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const eventProcessor = new EventProcessor(process.env.DEBUG === 'true');