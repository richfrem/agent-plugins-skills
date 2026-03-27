/**
 * tools/standalone/xml-to-markdown/src/processors/elements/TextSegmentProcessor.js
 * =================================================================================
 * 
 * Purpose:
 *   Processes TextSegment elements. Individual text runs with specific formatting
 *   within a CompoundText container.
 * 
 * Key Attributes: Text, FontName, FontSize, FontStyle
 * 
 * @module TextSegmentProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class TextSegmentProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('TextSegment',
            // Mandatory attributes (from forms.xsd: Name, Text)
            ['Name', 'Text'],
            // Optional attributes (from forms.xsd: DirtyInfo, SubclassSubObject, FontSize, FontSpacing, FontStyle, FontWeight, FontName, ForegroundColor)
            [
                'DirtyInfo',
                'SubclassSubObject',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'FontName',
                'ForegroundColor'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root TextSegment element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--TextSegmentProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the TextSegment
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--TextSegmentProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the TextSegment
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--TextSegmentProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const textSegmentProcessor = new TextSegmentProcessor(process.env.DEBUG === 'true');