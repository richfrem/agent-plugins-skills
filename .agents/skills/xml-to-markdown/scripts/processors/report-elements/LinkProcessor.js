/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/LinkProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <link> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module LinkProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class LinkProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('link');
    }
}
