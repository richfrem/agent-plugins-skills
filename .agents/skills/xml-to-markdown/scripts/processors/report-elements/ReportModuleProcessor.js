/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ReportModuleProcessor.js
 * =======================================================================================
 * 
 * Purpose:
 *   Root processor for the <report> element.
 *   Orchestrates the high-level sections.
 * 
 * @module ReportModuleProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class ReportModuleProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    // Default processing suffices, capturing all children
    // GenerateMarkdown will be custom to order sections? 
    // Actually, the main script largely controls the root structure, 
    // but this processor can provide a "generateBody" method if we switch to full recursion.

    generateMarkdown(data, mdOutput) {
        // Root level metadata is handled by main script usually, 
        // but this could handle children.
    }
}
