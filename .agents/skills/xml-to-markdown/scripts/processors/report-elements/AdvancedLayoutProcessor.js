/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/AdvancedLayoutProcessor.js
 * ========================================================================================
 * 
 * Purpose:
 *   Processes <advancedLayout> elements - settings inside frames.
 *   Contains printing/positioning properties, not a section header.
 * 
 * @module AdvancedLayoutProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class AdvancedLayoutProcessor extends BaseReportElementProcessor {
    constructor() {
        super('advancedLayout');
    }

    // Settings element - no markdown output needed
    generateMarkdown(data, mdOutput) {
        // Silently skip - this is a settings/property container
    }
}
