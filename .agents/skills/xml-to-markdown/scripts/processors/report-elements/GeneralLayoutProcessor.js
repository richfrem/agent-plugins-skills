/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/GeneralLayoutProcessor.js
 * ========================================================================================
 * 
 * Purpose:
 *   Processes <generalLayout> elements - settings elements inside frames.
 *   Contains layout properties like verticalElasticity, not a section header.
 * 
 * @module GeneralLayoutProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class GeneralLayoutProcessor extends BaseReportElementProcessor {
    constructor() {
        super('generalLayout');
    }

    // Settings element - no markdown output needed
    generateMarkdown(data, mdOutput) {
        // Silently skip - this is a settings/property container, not a section
    }
}
