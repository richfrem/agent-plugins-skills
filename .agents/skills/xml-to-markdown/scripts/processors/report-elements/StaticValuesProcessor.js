/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/StaticValuesProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <staticValues> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module StaticValuesProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class StaticValuesProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('staticValues');
    }
}
