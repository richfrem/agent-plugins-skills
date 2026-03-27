/**
 * tools/standalone/xml-to-markdown/src/processors/elements/menuItemProcessor.js
 * ==============================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms MenuItem elements. MenuItems are individual commands
 *   or actions in the menu bar (e.g., File > Save, Edit > Copy).
 * 
 * Input:
 *   - Parsed <MenuItem> XML element
 * 
 * Output:
 *   - Structured menu item data with label, command, and access settings
 *   - Markdown section with menu command details
 * 
 * Key Attributes Extracted:
 *   - Name: Internal identifier
 *   - Label: Display text shown in menu
 *   - CommandType: MENU, PLSQL, NULL
 *   - MenuItemCode: PL/SQL code to execute
 *   - KeyboardAccelerator: Shortcut (Ctrl+S, etc.)
 *   - Enabled, Visible: State flags
 *   - RoleCount: Number of roles with access
 * 
 * Child Elements:
 *   - MenuItemRole (role-based access control)
 * 
 * Usage:
 *   import { menuItemProcessor } from './menuItemProcessor.js';
 *   const result = await menuItemProcessor.processRootElement(menuItemElement);
 * 
 * @module MenuItemProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class MenuItemProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Menuitem',
            // Mandatory attributes (from forms.xsd: Name, Label, CommandType)
            ['Name', 'Label', 'CommandType'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'DisplayNoPriv',
                'Enabled',
                'IconInMenu',
                'SubclassSubObject',
                'Visible',
                'VisibleInHorizontalMenuToolbar',
                'VisibleInMenu',
                'VisibleInVerticalMenuToolbar',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'MagicItem',
                'MenuItemType',
                'ParentModuleType',
                'ParentSourceLevel1ObjectType',
                'ParentType',
                'PersistentClientInfoLength',
                'RoleCount',
                'CommandText',
                'Comment',
                'FontName',
                'Hint',
                'IconFilename',
                'KeyboardAccelerator',
                'MenuItemCode',
                'MenuItemRadioGroup',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'ParentSourceLevel1ObjectName',
                'SubMenuName',
                'VisualAttributeName',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root MenuItem element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--MenuItemProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the MenuItem
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--MenuItemProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a MenuItem element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--MenuItemProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const menuItemProcessor = new MenuItemProcessor(process.env.DEBUG === 'true');