/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/FormatExceptionProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <formatException> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module FormatExceptionProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class FormatExceptionProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('formatException');
    }
}
