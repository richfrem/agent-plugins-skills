/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/BeforePageHtmlEscapeProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <beforePageHtmlEscape> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module BeforePageHtmlEscapeProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class BeforePageHtmlEscapeProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('beforePageHtmlEscape');
    }
}
