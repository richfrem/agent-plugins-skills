/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ConditionalFormatProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <conditionalFormat> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module ConditionalFormatProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class ConditionalFormatProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('conditionalFormat');
    }
}
