/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/FontProcessor.js
 * =================================================================================
 * 
 * Purpose:
 *   Processes Oracle Reports Font elements. These define text styling
 *   attributes like face, size, and weight.
 * 
 * Schema Attributes (from discovery):
 *   - bold (yes/no)
 *   - face (e.g., "Arial")
 *   - italic (yes/no)
 *   - size (points)
 *   - textColor
 *   - underline (yes/no)
 * 
 * @module FontProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class FontProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    enrichData(data, element) {
        // Create a summary string for easier display
        const attrs = data.attributes;
        const details = [];

        if (attrs.face) details.push(attrs.face);
        if (attrs.size) details.push(`${attrs.size}pt`);
        if (attrs.bold === 'yes') details.push('Bold');
        if (attrs.italic === 'yes') details.push('Italic');
        if (attrs.underline === 'yes') details.push('Underline');

        data.summary = details.join(' ');
        return data;
    }

    generateMarkdown(data, mdOutput) {
        // Often embedded, so maybe just inline?
        // But if called directly:
        mdOutput.push(`**Font:** ${data.summary}`);
    }
}
