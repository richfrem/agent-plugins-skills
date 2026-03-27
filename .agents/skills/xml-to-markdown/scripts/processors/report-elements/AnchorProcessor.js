/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/AnchorProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <anchor> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module AnchorProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class AnchorProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('anchor');
    }
}
