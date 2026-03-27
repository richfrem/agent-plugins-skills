/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/SelectStatementProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <selectStatement> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module SelectStatementProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class SelectStatementProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('selectStatement');
    }
}
