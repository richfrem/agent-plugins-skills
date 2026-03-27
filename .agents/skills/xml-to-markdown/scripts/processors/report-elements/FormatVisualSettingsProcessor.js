/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/FormatVisualSettingsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <formatVisualSettings> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module FormatVisualSettingsProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class FormatVisualSettingsProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('formatVisualSettings');
    }
}
