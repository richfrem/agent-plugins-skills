/**
 * tools/standalone/xml-to-markdown/src/processors/elements/canvasProcessor.js
 * ============================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Canvas elements. Canvases are visual containers
 *   that hold Items and define the layout of form screens.
 * 
 * Input:
 *   - Parsed <Canvas> XML element
 * 
 * Output:
 *   - Structured canvas data with dimensions and display settings
 *   - Markdown section with canvas properties
 * 
 * Key Attributes Extracted:
 *   - Name: Canvas identifier
 *   - CanvasType: CONTENT, STACKED, TAB, TOOLBAR
 *   - WindowName: Parent window
 *   - Width, Height: Canvas dimensions
 *   - Visible: Display state
 * 
 * Child Elements:
 *   - Graphics (shapes, images)
 *   - TabPage (for tab canvases)
 * 
 * @module CanvasProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class CanvasProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Canvas',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (all other attributes from forms.xsd)
            [
                'DirtyInfo',
                'DisplayViewport',
                'RaiseOnEnter',
                'ShowHorizontalScrollbar',
                'ShowVerticalScrollbar',
                'SubclassObjectGroup',
                'Visible',
                'Bevel',
                'CanvasType',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'GradientStart',
                'Height',
                'LanguageDirection',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'TabActionStyle',
                'TabAttachmentEdge',
                'TabStyle',
                'TabWidthStyle',
                'ViewportHeight',
                'ViewportWidth',
                'ViewportXPosition',
                'ViewportXPositionOnCanvas',
                'ViewportYPosition',
                'ViewportYPositionOnCanvas',
                'Width',
                'BackColor',
                'Comment',
                'FillPattern',
                'FontName',
                'ForegroundColor',
                'HelpBookTopic',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'PopupMenuName',
                'VisualAttributeName',
                'WindowName',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Canvas element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--CanvasProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Canvas
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--CanvasProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a Canvas element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--CanvasProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const canvasProcessor = new CanvasProcessor(process.env.DEBUG === 'true');