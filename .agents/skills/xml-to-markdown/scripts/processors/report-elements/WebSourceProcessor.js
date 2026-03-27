/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/WebSourceProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <webSource> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module WebSourceProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class WebSourceProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('webSource');
    }
}
