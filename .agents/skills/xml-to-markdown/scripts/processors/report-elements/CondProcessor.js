/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/CondProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <cond> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module CondProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class CondProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('cond');
    }
}
