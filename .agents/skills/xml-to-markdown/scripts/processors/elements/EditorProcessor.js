/**
 * tools/standalone/xml-to-markdown/src/processors/elements/EditorProcessor.js
 * ============================================================================
 * 
 * Purpose:
 *   Processes Editor elements. Named text editor configurations for multi-line
 *   text editing in items (invoked via Edit menu or programmatically).
 * 
 * Key Attributes: Name, Title, ShowHorizontalScrollbar, ShowVerticalScrollbar
 * 
 * @module EditorProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class EditorProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Editor',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (all other attributes from forms.xsd)
            [
                'DirtyInfo',
                'ShowHorizontalScrollbar',
                'ShowVerticalScrollbar',
                'SubclassObjectGroup',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'Height',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'Width',
                'WrapStyle',
                'XPosition',
                'YPosition',
                'BackColor',
                'BottomTitle',
                'Comment',
                'FillPattern',
                'FontName',
                'ForegroundColor',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'Title',
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
     * Process the root Editor element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--EditorProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Editor
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--EditorProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Editor
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--EditorProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const editorProcessor = new EditorProcessor(process.env.DEBUG === 'true');