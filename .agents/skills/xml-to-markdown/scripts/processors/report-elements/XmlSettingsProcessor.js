/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/XmlSettingsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <xmlSettings> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module XmlSettingsProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class XmlSettingsProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('xmlSettings');
    }
}
