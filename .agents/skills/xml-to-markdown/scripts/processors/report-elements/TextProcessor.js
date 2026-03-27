/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/TextProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <text> elements.
 *   Extends TextSegmentProcessor for shared logic.
 * 
 * @module TextProcessor
 * @extends TextSegmentProcessor
 */

import { TextSegmentProcessor } from './TextSegmentProcessor.js';

export class TextProcessor extends TextSegmentProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('text');
    }
}
