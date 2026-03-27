/**
 * Processor for <body> elements - structural container in layout.
 * @module BodyProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class BodyProcessor extends BaseReportElementProcessor {
    constructor() {
        super('body');
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        // Body is a structural container - just recurse into children without header
        if (generateChildMarkdown && data.children && data.children.length > 0) {
            for (const child of data.children) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}
