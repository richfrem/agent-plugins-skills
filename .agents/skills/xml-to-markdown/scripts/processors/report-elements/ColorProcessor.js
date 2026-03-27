/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ColorProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <color> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module ColorProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class ColorProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('color');
    }
}
