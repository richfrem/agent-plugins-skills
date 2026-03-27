/**
 * Processor for <section> elements (header/trailer/main sections).
 * @module SectionProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class SectionProcessor extends BaseReportElementProcessor {
    constructor() {
        super('section');
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        const name = data.attributes?.name || 'main';
        mdOutput.push(`### Section: ${name}`);

        if (generateChildMarkdown && data.children && data.children.length > 0) {
            for (const child of data.children) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}
