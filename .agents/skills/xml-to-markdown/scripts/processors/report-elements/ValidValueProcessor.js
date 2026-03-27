/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ValidValueProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <validValue> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module ValidValueProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class ValidValueProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('validValue');
    }
}
