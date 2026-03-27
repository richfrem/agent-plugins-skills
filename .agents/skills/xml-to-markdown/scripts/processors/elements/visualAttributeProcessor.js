/**
 * tools/standalone/xml-to-markdown/src/processors/elements/visualAttributeProcessor.js
 * =====================================================================================
 * 
 * Purpose:
 *   Processes VisualAttribute elements. Named style definitions (fonts, colors)
 *   that can be applied to items, blocks, and canvases for consistent appearance.
 * 
 * Key Attributes: Name, FontName, FontSize, BackColor, ForegroundColor, FillPattern
 * 
 * @module VisualAttributeProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class VisualAttributeProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('VisualAttribute',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'SubclassObjectGroup',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'FrameTitleFontSize',
                'FrameTitleFontSpacing',
                'FrameTitleFontStyle',
                'FrameTitleFontWeight',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'PromptFontSize',
                'PromptFontSpacing',
                'PromptFontStyle',
                'PromptFontWeight',
                'VisualAttributeType',
                'BackColor',
                'Comment',
                'FillPattern',
                'FontName',
                'ForegroundColor',
                'FrameTitleBackColor',
                'FrameTitleFillPattern',
                'FrameTitleFontName',
                'FrameTitleForegroundColor',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'PromptBackColor',
                'PromptFillPattern',
                'PromptFontName',
                'PromptForegroundColor',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root VisualAttribute element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--VisualAttributeProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the VisualAttribute
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--VisualAttributeProcessor processChildren called');
        return super.processChildren(element, log, output);
    }
}

// Create and export a singleton instance
export const visualAttributeProcessor = new VisualAttributeProcessor(process.env.DEBUG === 'true');