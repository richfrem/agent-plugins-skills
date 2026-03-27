/**
 * tools/standalone/xml-to-markdown/src/processors/elements/ModuleProcessor.js
 * ============================================================================
 * 
 * Purpose:
 *   Generic Module processor for module-level elements. Used as fallback
 *   when a specific processor is not available.
 * 
 * Key Attributes: Name
 * 
 * @module ModuleProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ModuleProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Module',
            // Mandatory attributes (from forms.xsd: version)
            [
                'version'
            ],
            // Optional attributes (none defined in forms.xsd for Module)
            [],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }


    /**
     * Process the root Module element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ModuleProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Module
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ModuleProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a Module element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ModuleProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const moduleProcessor = new ModuleProcessor(process.env.DEBUG === 'true');