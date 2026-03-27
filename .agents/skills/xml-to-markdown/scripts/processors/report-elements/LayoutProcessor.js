/**
 * Processor for <layout> elements - root layout container.
 * @module LayoutProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class LayoutProcessor extends BaseReportElementProcessor {
    constructor() {
        super('layout');
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        // Only output header once, then recurse children
        mdOutput.push('## Layout');
        mdOutput.push('');

        if (generateChildMarkdown && data.children && data.children.length > 0) {
            for (const child of data.children) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}
