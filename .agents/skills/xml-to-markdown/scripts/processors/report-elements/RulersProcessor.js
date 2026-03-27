/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/RulersProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <rulers> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module RulersProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class RulersProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('rulers');
    }
}
