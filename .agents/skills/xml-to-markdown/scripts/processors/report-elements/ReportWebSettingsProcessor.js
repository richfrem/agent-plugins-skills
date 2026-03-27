/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ReportWebSettingsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <reportWebSettings> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module ReportWebSettingsProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class ReportWebSettingsProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('reportWebSettings');
    }
}
