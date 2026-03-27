/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/BinaryDataProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <binaryData> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module BinaryDataProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class BinaryDataProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('binaryData');
    }
}
