/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/AfterPageHtmlEscapeProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <afterPageHtmlEscape> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module AfterPageHtmlEscapeProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class AfterPageHtmlEscapeProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('afterPageHtmlEscape');
    }
}
