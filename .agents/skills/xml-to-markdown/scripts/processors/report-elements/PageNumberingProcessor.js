/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/PageNumberingProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <pageNumbering> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module PageNumberingProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class PageNumberingProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('pageNumbering');
    }
}
