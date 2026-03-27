/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/DisplayInfoProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <displayInfo> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module DisplayInfoProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class DisplayInfoProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('displayInfo');
    }
}
