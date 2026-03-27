/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/FilterProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <filter> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module FilterProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class FilterProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('filter');
    }
}
