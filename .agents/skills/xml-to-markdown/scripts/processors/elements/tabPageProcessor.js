/**
 * tools/standalone/xml-to-markdown/src/processors/elements/tabPageProcessor.js
 * =============================================================================
 * 
 * Purpose:
 *   Processes TabPage elements within Tab Canvases. Each page represents a
 *   switchable view in tabbed interfaces.
 * 
 * Key Attributes: Name, Label, Enabled, Visible
 * 
 * @module TabPageProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class TabPageProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('TabPage',
            // Mandatory attributes (from forms.xsd: Name, Label)
            ['Name', 'Label'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'Enabled',
                'SubclassSubObject',
                'Visible',
                'GradientStart',
                'ParentModuleType',
                'ParentSourceLevel1ObjectType',
                'ParentType',
                'PersistentClientInfoLength',
                'BackColor',
                'Comment',
                'FillPattern',
                'ForegroundColor',
                'IconFilename',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'ParentSourceLevel1ObjectName',
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
     * Process the root TabPage element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--TabPageProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the TabPage
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--TabPageProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a TabPage element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--TabPageProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const tabPageProcessor = new TabPageProcessor(process.env.DEBUG === 'true');