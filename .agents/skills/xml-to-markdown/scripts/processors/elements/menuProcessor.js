/**
 * tools/standalone/xml-to-markdown/src/processors/elements/menuProcessor.js
 * ==========================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Menu elements. Menus are containers for MenuItems
 *   within a MenuModule, defining pulldown menu structure.
 * 
 * Key Attributes: Name, MenuStyle, TearOffMenu
 * Child Elements: MenuItem
 * 
 * @module MenuProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class MenuProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Menu',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'SubclassObjectGroup',
                'TearOffMenu',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'BottomTitle',
                'Comment',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'SubTitle',
                'Title',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Menu element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--MenuProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Menu
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--MenuProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Menu
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--MenuProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const menuProcessor = new MenuProcessor(process.env.DEBUG === 'true');