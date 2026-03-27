/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/DataItemProcessor.js
 * ====================================================================================
 * 
 * Purpose:
 *   Processes Data Items (columns) within groups.
 *   This is the core schema definition for the report's data output.
 * 
 * Schema Elements:
 *   - <dataItem> (Visual Rep)
 *   - <dataDescriptor> (Logic Rep)
 * 
 * Attributes:
 *   - name, source, datatype, oracleDatatype
 *   - width, precision, scale
 *   - defaultLabel
 * 
 * @module DataItemProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class DataItemProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    enrichData(data, element) {
        const attrs = data.attributes;

        // Normalize DataType
        data.dataType = attrs.datatype || attrs.oracleDatatype || 'UNKNOWN';

        // Normalize Label
        data.label = attrs.defaultLabel || attrs.label || '';

        // Summary for table rows
        data.summary = `${attrs.name} (${data.dataType})`;

        return data;
    }

    generateMarkdown(data, mdOutput) {
        // Table row format mostly
        // | Name | Type | Width | Label | 
        const width = data.attributes.width || '';
        mdOutput.push(`| ${data.attributes.name} | ${data.dataType} | ${width} | ${data.label} |`);
    }
}
