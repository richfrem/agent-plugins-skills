/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/WebSettingsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <webSettings> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module WebSettingsProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class WebSettingsProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('webSettings');
    }
}
