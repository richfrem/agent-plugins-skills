/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/TextSettingsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <textSettings> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module TextSettingsProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class TextSettingsProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('textSettings');
    }
}
