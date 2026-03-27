/**
 * Processor for <data> elements - data model container.
 * @module DataProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class DataProcessor extends BaseReportElementProcessor {
    constructor() {
        super('data');
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        mdOutput.push('## Data Model');
        mdOutput.push('');

        if (generateChildMarkdown && data.children && data.children.length > 0) {
            for (const child of data.children) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}
