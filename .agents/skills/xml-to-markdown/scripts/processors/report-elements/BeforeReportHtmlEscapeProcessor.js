/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/BeforeReportHtmlEscapeProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <beforeReportHtmlEscape> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module BeforeReportHtmlEscapeProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class BeforeReportHtmlEscapeProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('beforeReportHtmlEscape');
    }
}
