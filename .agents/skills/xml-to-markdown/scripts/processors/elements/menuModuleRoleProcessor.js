/**
 * tools/standalone/xml-to-markdown/src/processors/elements/menuModuleRoleProcessor.js
 * ====================================================================================
 * 
 * Purpose:
 *   Processes MenuModuleRole elements. Defines module-level role assignments
 *   for the entire menu, used when UseSecurity=true.
 * 
 * Key Attributes: RoleName
 * 
 * @module MenuModuleRoleProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class MenuModuleRoleProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('MenuModuleRole',
            // Mandatory attributes (from forms.xsd: Index, Value)
            ['Index', 'Value'],
            // Optional attributes (none in forms.xsd for MenuModuleRole)
            [],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root MenuModuleRole element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--MenuModuleRoleProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the MenuModuleRole
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--MenuModuleRoleProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the MenuModuleRole
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--MenuModuleRoleProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const menuModuleRoleProcessor = new MenuModuleRoleProcessor(process.env.DEBUG === 'true');