/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/GenericReportElementProcessor.js
 * ==============================================================================================
 * 
 * Purpose:
 *   Fallback processor for elements that don't need specific Markdown formatting logic
 *   but should still retain their attributes and structure in the processed data tree.
 * 
 * @module GenericReportElementProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class GenericReportElementProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    generateMarkdown(data, mdOutput) {
        // Default behavior: Don't render generic containers explicitly unless debug?
        // OR render them as simplified blocks.

        // If it has children, we definitely want to render children
        // (Recursive generation loop handles children iteration)

        // If it has attributes, maybe render a summary?
        // For now, minimal output to reduce noise.
    }
}
