/**
 * tools/standalone/xml-to-markdown/src/processors/elements/alertProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Alert elements. Alerts are modal message dialogs
 *   used for user notifications, confirmations, and error messages.
 * 
 * Input:
 *   - Parsed <Alert> XML element
 * 
 * Output:
 *   - Structured alert data with message, button labels, and style
 *   - Markdown section with alert properties
 * 
 * Key Attributes Extracted:
 *   - Name: Alert identifier
 *   - AlertMessage: Message text displayed
 *   - AlertStyle: STOP, CAUTION, NOTE
 *   - Title: Dialog title
 *   - Button1Label, Button2Label, Button3Label: Button texts
 *   - DefaultAlertButton: Which button is default
 * 
 * @module AlertProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class AlertProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Alert',
            // Mandatory attributes (from forms.xsd)
            ['Name'], // <-- update this list if more are required
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'SubclassObjectGroup',
                'AlertStyle',
                'DefaultAlertButton',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'LanguageDirection',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'AlertMessage',
                'BackColor',
                'Button1Label',
                'Button2Label',
                'Button3Label',
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
     * Process the root Alert element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--AlertProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Alert
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--AlertProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing an Alert element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--AlertProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const alertProcessor = new AlertProcessor(process.env.DEBUG === 'true');