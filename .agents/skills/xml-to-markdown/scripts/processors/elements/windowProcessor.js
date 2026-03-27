/**
 * tools/standalone/xml-to-markdown/src/processors/elements/windowProcessor.js
 * ============================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Window elements. Windows are the top-level visual
 *   containers that hold Canvases and define form window behavior.
 * 
 * Input:
 *   - Parsed <Window> XML element
 * 
 * Output:
 *   - Structured window data with title, dimensions, and modal settings
 *   - Markdown section with window properties
 * 
 * Key Attributes Extracted:
 *   - Name: Window identifier
 *   - Title: Window title bar text
 *   - Width, Height: Window dimensions
 *   - Modal: Whether window blocks other windows
 *   - PrimaryCanvas: Main canvas displayed
 * 
 * @module WindowProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class WindowProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Window',
            // Mandatory attributes (from forms.xsd: Name, Width, Height)
            ['Name', 'Width', 'Height'],
            // Optional attributes (from forms.xsd)
            [
                'Title',
                'XPosition',
                'YPosition',
                'ShowHorizontalScrollbar',
                'ShowVerticalScrollbar',
                'DirtyInfo',
                'ResizeAllowed',
                'InheritMenu',
                'HideOnExit',
                'ClearAllowed',
                'Modal',
                'PrimaryCanvas',
                'ParentModule',
                'ParentModuleType',
                'ParentName',
                'ParentFilename',
                'ParentType',
                'VisualAttributeName',
                'MinimizeAllowed',
                'MaximizeAllowed',
                'WindowStyle',
                'MoveAllowed',
                'SubclassObjectGroup',
                'Bevel',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'LanguageDirection',
                'PersistentClientInfoLength',
                'BackColor',
                'Comment',
                'FillPattern',
                'FontName',
                'ForegroundColor',
                'HelpBookTopic',
                'HorizontalToolbarCanvasName',
                'IconFilename',
                'MinimizeTitle',
                'ParentFilepath',
                'SmartClass',
                'VerticalToolbarCanvasName'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }


    /**
     * Process the root Window element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--WindowProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Window
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--WindowProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Window
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--WindowProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const windowProcessor = new WindowProcessor(process.env.DEBUG === 'true');