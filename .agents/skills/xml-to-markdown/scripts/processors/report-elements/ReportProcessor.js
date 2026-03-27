/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ReportProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <report> elements.
 *   Extends ReportModuleProcessor for shared logic.
 * 
 * @module ReportProcessor
 * @extends ReportModuleProcessor
 */

import { ReportModuleProcessor } from './ReportModuleProcessor.js';

export class ReportProcessor extends ReportModuleProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('report');
    }
}
