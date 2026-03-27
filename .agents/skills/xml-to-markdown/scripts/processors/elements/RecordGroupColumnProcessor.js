/**
 * tools/standalone/xml-to-markdown/src/processors/elements/RecordGroupColumnProcessor.js
 * =======================================================================================
 * 
 * Purpose:
 *   Processes RecordGroupColumn elements. Defines columns within a RecordGroup
 *   including name, data type, and width for query result storage.
 * 
 * Key Attributes: Name, ColumnDataType, MaximumLength
 * 
 * @module RecordGroupColumnProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class RecordGroupColumnProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('RecordGroupColumn',
            // Mandatory attributes (from forms.xsd: Name, ColumnDataType, MaximumLength)
            ['Name', 'ColumnDataType', 'MaximumLength'],
            // Optional attributes (from forms.xsd: DirtyInfo, ColumnValuesCount, DataLengthSemantics, PersistentClientInfoLength)
            [
                'DirtyInfo',
                'ColumnValuesCount',
                'DataLengthSemantics',
                'PersistentClientInfoLength'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }


    /**
     * Process the root RecordGroupColumn element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--RecordGroupColumnProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the RecordGroupColumn
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--RecordGroupColumnProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the RecordGroupColumn
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--RecordGroupColumnProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const recordGroupColumnProcessor = new RecordGroupColumnProcessor(process.env.DEBUG === 'true');