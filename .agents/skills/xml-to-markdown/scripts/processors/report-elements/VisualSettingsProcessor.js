/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/VisualSettingsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <visualSettings> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module VisualSettingsProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class VisualSettingsProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('visualSettings');
    }
}
