/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/RepeatingFrameProcessor.js
 * =========================================================================================
 * 
 * Purpose:
 *   Processes Repeating Frames (R_...). These are the visual iteration containers
 *   linked to Groups in the data model.
 * 
 * Schema Attributes:
 *   - source (Group Name)
 *   - printDirection, maxRecordsPerPage
 * 
 * @module RepeatingFrameProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class RepeatingFrameProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    enrichData(data, element) {
        const attrs = data.attributes || {};
        data.summary = `Recursive Frame sourced from: ${attrs.source || 'Unknown'}`;
        return data;
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        const attrs = data.attributes || {};
        const name = attrs.name;

        // Skip frames without names - they're structural containers
        if (!name) {
            if (generateChildMarkdown && data.children) {
                for (const child of data.children) {
                    generateChildMarkdown(child, mdOutput);
                }
            }
            return;
        }

        mdOutput.push(`#### Frame: ${name} (${attrs.printDirection || 'Unknown Direction'})`);
        mdOutput.push(`> Source Group: **${attrs.source || 'None'}**`);

        if (generateChildMarkdown && data.children) {
            for (const child of data.children) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}

