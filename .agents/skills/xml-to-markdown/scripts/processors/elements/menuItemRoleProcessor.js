/**
 * tools/standalone/xml-to-markdown/src/processors/elements/menuItemRoleProcessor.js
 * ==================================================================================
 * 
 * Purpose:
 *   Processes MenuItemRole elements. Defines which roles can access a MenuItem.
 *   Critical for security analysis and role-based access control documentation.
 * 
 * Key Attributes: RoleName
 * 
 * @module MenuItemRoleProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class MenuItemRoleProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('MenuItemRole',
            // Mandatory attributes (from forms.xsd: Index, Value)
            ['Index', 'Value'],
            // Optional attributes (none in forms.xsd for MenuItemRole)
            [],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root MenuItemRole element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--MenuItemRoleProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the MenuItemRole
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--MenuItemRoleProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the MenuItemRole
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--MenuItemRoleProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const menuItemRoleProcessor = new MenuItemRoleProcessor(process.env.DEBUG === 'true');