/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/PageNavigationHtmlEscapeProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <pageNavigationHtmlEscape> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module PageNavigationHtmlEscapeProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class PageNavigationHtmlEscapeProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('pageNavigationHtmlEscape');
    }
}
