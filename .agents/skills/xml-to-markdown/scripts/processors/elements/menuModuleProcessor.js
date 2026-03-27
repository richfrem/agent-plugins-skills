/**
 * tools/standalone/xml-to-markdown/src/processors/elements/menuModuleProcessor.js
 * ================================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms MenuModule elements. MenuModule is the root container
 *   for an Oracle Menu (.mmb), defining the application's menu bar and actions.
 * 
 * Input:
 *   - Parsed <MenuModule> XML element (from _mmb.xml files)
 * 
 * Output:
 *   - Structured menu metadata with name and security settings
 *   - Markdown document with menu structure
 * 
 * Key Attributes Extracted:
 *   - Name: Menu module name (e.g., FORM0000)
 *   - MainMenu: Root menu definition
 *   - UseSecurity: Whether role-based access is enabled
 *   - StartupCode: PL/SQL executed on menu load
 * 
 * Child Elements:
 *   - Menu (menu definitions)
 *   - MenuItem (individual menu commands)
 *   - MenuModuleRole (role assignments)
 *   - ProgramUnit (menu-level code)
 * 
 * Usage:
 *   import { menuModuleProcessor } from './menuModuleProcessor.js';
 *   const result = await menuModuleProcessor.processRootElement(menuElement);
 * 
 * @module MenuModuleProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class MenuModuleProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('MenuModule',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'ShareLibrary',
                'UseSecurity',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'RoleCount',
                'Comment',
                'MainMenu',
                'MenuDirectory',
                'MenuFilename',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'StartupCode'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root MenuModule element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--MenuModuleProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the MenuModule
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--MenuModuleProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the MenuModule
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--MenuModuleProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const menuModuleProcessor = new MenuModuleProcessor(process.env.DEBUG === 'true');