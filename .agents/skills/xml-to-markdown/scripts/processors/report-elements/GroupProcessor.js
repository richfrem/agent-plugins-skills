/**
 * Processor for <group> elements - data groups with items and formulas.
 * @module GroupProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class GroupProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName || 'group');
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        const name = data.attributes?.name;

        // Skip output if no name - this prevents "Unnamed Group" artifacts
        if (!name) {
            // Still process children silently
            if (generateChildMarkdown && data.children) {
                for (const child of data.children) {
                    generateChildMarkdown(child, mdOutput);
                }
            }
            return;
        }

        mdOutput.push(`### Group: ${name}`);

        // Data Items Table
        const dataItems = (data.children || []).filter(c => c.type === 'dataItem');
        if (dataItems.length > 0) {
            mdOutput.push('');
            mdOutput.push('**Data Items:**');
            mdOutput.push('| Name | Datatype | Width | Label |');
            mdOutput.push('|------|----------|-------|-------|');
            for (const item of dataItems) {
                const attrs = item.attributes || {};
                const dtype = attrs.datatype || attrs.oracleDatatype || '';
                mdOutput.push(`| ${attrs.name || ''} | ${dtype} | ${attrs.width || ''} | ${attrs.defaultLabel || ''} |`);
            }
            mdOutput.push('');
        }

        // Formulas
        const formulas = (data.children || []).filter(c => c.type === 'formula');
        if (formulas.length > 0) {
            mdOutput.push('**Formulas:**');
            mdOutput.push('| Name | Source | Datatype |');
            mdOutput.push('|------|--------|----------|');
            for (const f of formulas) {
                const attrs = f.attributes || {};
                mdOutput.push(`| ${attrs.name || ''} | ${attrs.source || ''} | ${attrs.datatype || ''} |`);
            }
            mdOutput.push('');
        }

        // Recurse for other children
        const handledTypes = ['dataItem', 'formula'];
        const otherChildren = (data.children || []).filter(c => !handledTypes.includes(c.type));

        if (generateChildMarkdown && otherChildren.length > 0) {
            for (const child of otherChildren) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}
