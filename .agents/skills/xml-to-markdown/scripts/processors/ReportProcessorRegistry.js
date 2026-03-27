/**
 * tools/standalone/xml-to-markdown/src/processors/ReportProcessorRegistry.js
 * ===========================================================================
 * 
 * Purpose:
 *   Central registry for Oracle Report element processors.
 *   Dispatches processing to specific handlers based on XML element names,
 *   leveraging lazy-loading from reportElementTypes.js.
 * 
 * Usage:
 *   import { registry } from './ReportProcessorRegistry.js';
 *   const processor = await registry.getProcessor('userParameter');
 * 
 * @module ReportProcessorRegistry
 */

import { BaseReportElementProcessor } from './BaseReportElementProcessor.js';
import { getReportProcessor } from './reportElementTypes.js';

class ReportProcessorRegistry {
    constructor() {
        this.defaultProcessor = new BaseReportElementProcessor('Generic');
    }

    /**
     * Get processor for an element
     * @param {string} elementName 
     * @returns {Promise<BaseReportElementProcessor>}
     */
    async getProcessor(elementName) {
        // Try to get specific processor
        const processor = await getReportProcessor(elementName);

        // Return specific processor if found, otherwise default generic
        return processor || this.defaultProcessor;
    }
}

// Singleton instance
export const reportProcessorRegistry = new ReportProcessorRegistry();
