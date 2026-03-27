/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/StringProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <string> elements.
 *   Extends TextSegmentProcessor for shared logic.
 * 
 * @module StringProcessor
 * @extends TextSegmentProcessor
 */

import { TextSegmentProcessor } from './TextSegmentProcessor.js';

export class StringProcessor extends TextSegmentProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('string');
    }
}
