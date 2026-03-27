/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/FormulaProcessor.js
 * ===================================================================================
 * 
 * Purpose:
 *   Processes formula and summary columns in Oracle Reports XML.
 *   Formulas calculate values using PL/SQL; summaries aggregate data.
 * 
 * Input:
 *   - <formula> elements with name, source (function ref), datatype attributes
 *   - <summary> elements with similar structure
 * 
 * Output:
 *   - Table row format: | Name | Datatype | Source: `function_name` |
 * 
 * @module FormulaProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class FormulaProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName || 'formula');
    }

    enrichData(data, element) {
        const attrs = data.attributes || {};
        data.source = attrs.source || '';
        data.dataType = attrs.datatype || 'N/A';
        return data;
    }

    generateMarkdown(data, mdOutput) {
        const attrs = data.attributes || {};
        const name = attrs.name || '';
        const dataType = data.dataType || attrs.datatype || 'N/A';
        const source = data.source || attrs.source || '';

        mdOutput.push(`| ${name} | ${dataType} | Source: \`${source}\` |`);
    }
}
