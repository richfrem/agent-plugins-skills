/**
 * tools/standalone/xml-to-markdown/src/processors/elements/VisualStateProcessor.js
 * =================================================================================
 * 
 * Purpose:
 *   Processes VisualState elements. Named visual states for TreeItem nodes
 *   defining appearance based on node state.
 * 
 * Key Attributes: ImageFilename, DisplayQuality
 * 
 * @module VisualStateProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class VisualStateProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('VisualState',
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
     * Process the root VisualState element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--VisualStateProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the VisualState
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--VisualStateProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the VisualState
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--VisualStateProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const visualStateProcessor = new VisualStateProcessor(process.env.DEBUG === 'true');