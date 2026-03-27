/**
 * tools/standalone/xml-to-markdown/src/processors/elements/LovProcessor.js
 * =========================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms LOV (List of Values) elements. LOVs provide
 *   popup selection dialogs for field validation and data entry.
 * 
 * Input:
 *   - Parsed <Lov> XML element
 * 
 * Output:
 *   - Structured LOV data with record group and display settings
 *   - Markdown section with LOV properties
 * 
 * Key Attributes Extracted:
 *   - Name: LOV identifier
 *   - RecordGroupName: Data source for LOV values
 *   - Title: Dialog title
 *   - Width, Height: LOV dialog dimensions
 *   - AutoDisplay: Whether to show automatically
 * 
 * Child Elements:
 *   - LovColumnMapping (maps LOV columns to form items)
 * 
 * @module LovProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class LovProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Lov',
            // Mandatory attributes (from forms.xsd: Name, RecordGroupName, Width, Height)
            ['Name', 'RecordGroupName', 'Width', 'Height'],
            // Optional attributes (from forms.xsd)
            [
                'AutoColumnWidth',
                'AutoDisplay',
                'AutoPosition',
                'AutoRefresh',
                'AutoSkip',
                'AutoSelect',
                'DirtyInfo',
                'FilterBeforeDisplay',
                'SubclassObjectGroup',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'LanguageDirection',
                'ListType',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'XPosition',
                'YPosition',
                'BackColor',
                'Comment',
                'FillPattern',
                'FontName',
                'ForegroundColor',
                'OldLovText',
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
       * Process the root Lov element
       * @param {Object} element - The XML element to process
       * @returns {Object} The processed element data
       */
    async processRootElement(element) {
        if (this.debug) console.log('--LovProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Lov
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--LovProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Lov
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--LovProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const lovProcessor = new LovProcessor(process.env.DEBUG === 'true');