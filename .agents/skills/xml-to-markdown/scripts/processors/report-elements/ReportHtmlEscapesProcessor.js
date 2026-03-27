/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ReportHtmlEscapesProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <reportHtmlEscapes> elements.
 *   Extends GroupProcessor for shared logic.
 * 
 * @module ReportHtmlEscapesProcessor
 * @extends GroupProcessor
 */

import { GroupProcessor } from './GroupProcessor.js';

export class ReportHtmlEscapesProcessor extends GroupProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('reportHtmlEscapes');
    }
}
