/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ParameterProcessor.js
 * ====================================================================================
 * 
 * Purpose:
 *   Processes System and User Parameters.
 *   These define input arguments for the report (e.g., date ranges, IDs).
 * 
 * Schema Attributes:
 *   - name, datatype, width, precision, scale
 *   - label, initialValue, inputMask
 *   - display (yes/no)
 * 
 * @module ParameterProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class ParameterProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    enrichData(data, element) {
        const attrs = data.attributes;

        // Normalize parameter type
        data.paramType = this.elementName === 'userParameter' ? 'User' : 'System';

        // Create concise summary for listing
        data.summary = `${data.paramType}: ${attrs.name}`;
        if (attrs.datatype) data.summary += ` (${attrs.datatype})`;
        if (attrs.initialValue) data.summary += ` = ${attrs.initialValue}`;

        return data;
    }

    generateMarkdown(data, mdOutput) {
        // Can be rendered as table row or detail block
        // For now, let's just push attribute summary as a bullet if called directly

        mdOutput.push(`- **${data.attributes.name}** (${data.paramType} - ${data.attributes.datatype || 'Unknown'})`);
        if (data.attributes.label) mdOutput.push(`  - Label: ${data.attributes.label}`);
        if (data.attributes.initialValue) mdOutput.push(`  - Default: \`${data.attributes.initialValue}\``);
    }
}
