/**
 * tools/standalone/xml-to-markdown/src/processors/elements/PointProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processes Point elements. Individual vertices within polyline or polygon
 *   graphics, defining shape paths via XPosition/YPosition.
 * 
 * Key Attributes: XPosition, YPosition
 * 
 * @module PointProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class PointProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Point',
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
     * Process the root Point element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--PointProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Point
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--PointProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Point
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--PointProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const pointProcessor = new PointProcessor(process.env.DEBUG === 'true');