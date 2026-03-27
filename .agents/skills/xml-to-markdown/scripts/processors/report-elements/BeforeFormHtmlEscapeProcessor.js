/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/BeforeFormHtmlEscapeProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <beforeFormHtmlEscape> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module BeforeFormHtmlEscapeProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class BeforeFormHtmlEscapeProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('beforeFormHtmlEscape');
    }
}
