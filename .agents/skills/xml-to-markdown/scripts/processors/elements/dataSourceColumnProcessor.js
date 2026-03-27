/**
 * tools/standalone/xml-to-markdown/src/processors/elements/dataSourceColumnProcessor.js
 * ======================================================================================
 * 
 * Purpose:
 *   Processes DataSourceColumn elements. Defines column bindings between database
 *   columns and block items for query/DML operations.
 * 
 * Key Attributes: Name, ColumnName, DataType, MaximumLength
 * 
 * @module DataSourceColumnProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class DataSourceColumnProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('DataSourceColumn',
            // Mandatory attributes (from forms.xsd: DSCName, DSCType, Type, DSCLength, DSCPrecision, DSCScale, DSCMandatory)
            [
                'DSCName',
                'DSCType',
                'Type',
                'DSCLength',
                'DSCPrecision',
                'DSCScale',
                'DSCMandatory'
            ],
            // Optional attributes (from forms.xsd: DSCNochildren, Name)
            [
                'DSCNochildren',
                'Name'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root DataSourceColumn element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--DataSourceColumnProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the DataSourceColumn
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--DataSourceColumnProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the DataSourceColumn
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--DataSourceColumnProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const dataSourceColumnProcessor = new DataSourceColumnProcessor(process.env.DEBUG === 'true');
