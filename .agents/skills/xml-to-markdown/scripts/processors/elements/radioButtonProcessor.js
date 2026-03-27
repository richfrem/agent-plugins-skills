/**
 * tools/standalone/xml-to-markdown/src/processors/elements/radioButtonProcessor.js
 * =================================================================================
 * 
 * Purpose:
 *   Processes RadioButton elements. Individual radio options within a RadioGroup
 *   item, typically for mutually exclusive choices.
 * 
 * Key Attributes: Name, Label, RadioButtonValue
 * 
 * @module RadioButtonProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class RadioButtonProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('RadioButton',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'Enabled',
                'SubclassSubObject',
                'Visible',
                'DistanceBetweenRecords',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'Height',
                'ParentModuleType',
                'ParentSourceLevel1ObjectType',
                'ParentSourceLevel2ObjectType',
                'ParentType',
                'PersistentClientInfoLength',
                'PromptAlign',
                'PromptAlignOffset',
                'PromptAttachmentEdge',
                'PromptAttachmentOffset',
                'PromptDisplayStyle',
                'PromptFontSize',
                'PromptFontSpacing',
                'PromptFontStyle',
                'PromptFontWeight',
                'PromptJustification',
                'PromptReadingOrder',
                'Width',
                'XPosition',
                'YPosition',
                'AccessKey',
                'BackColor',
                'Comment',
                'FillPattern',
                'FontName',
                'ForegroundColor',
                'Label',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'ParentSourceLevel1ObjectName',
                'ParentSourceLevel2ObjectName',
                'Prompt',
                'PromptBackColor',
                'PromptFillPattern',
                'PromptFontName',
                'PromptForegroundColor',
                'PromptVisualAttributeName',
                'RadioButtonValue',
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
     * Process the root RadioButton element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--RadioButtonProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the RadioButton
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--RadioButtonProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the RadioButton
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--RadioButtonProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const radioButtonProcessor = new RadioButtonProcessor(process.env.DEBUG === 'true');