/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/DataItemPrivateProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <dataItemPrivate> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module DataItemPrivateProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class DataItemPrivateProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('dataItemPrivate');
    }
}
