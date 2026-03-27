/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/MetadataProcessor.js
 * =====================================================================================
 * 
 * Purpose:
 *   Processes metadata elements like comments, display info, and settings.
 * 
 * @module MetadataProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class MetadataProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    async process(element, context) {
        const data = await super.process(element, context);

        // Handle text content for comments
        if (this.elementName === 'comment') {
            // xml2js puts text in _ or #text or direct string if simple
            // mixed content is tricky, traverse helper might have normalized
            const text = element._ || (typeof element === 'string' ? element : '');
            data.text = text ? text.trim() : '';
        }

        return data;
    }

    generateMarkdown(data, mdOutput) {
        if (this.elementName === 'comment' && data.text) {
            mdOutput.push('### Comment');
            mdOutput.push('```');
            mdOutput.push(data.text);
            mdOutput.push('```\n');
        }
    }
}
