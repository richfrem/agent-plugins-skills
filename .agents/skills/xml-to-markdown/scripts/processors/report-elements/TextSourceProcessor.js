/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/TextSourceProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <textSource> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module TextSourceProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class TextSourceProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('textSource');
    }
}
