/**
 * tools/standalone/xml-to-markdown/src/processors/elements/dataSourceArgumentProcessor.js
 * ========================================================================================
 * 
 * Purpose:
 *   Processes DataSourceArgument elements. Defines parameters for stored procedure
 *   data sources used in blocks.
 * 
 * Key Attributes: Name, Type, Mode (IN, OUT, IN_OUT)
 * 
 * @module DataSourceArgumentProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class DataSourceArgumentProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('DataSourceArgument',
            // Mandatory attributes (from forms.xsd: DSAName, DSAType, DSAValue, DSAMode, Type, DSATypeName)
            [
                'DSAName',
                'DSAType',
                'DSAValue',
                'DSAMode',
                'Type',
                'DSATypeName'
            ],
            // Optional attributes (from forms.xsd: SubclassSubObject, PersistentClientInfoLength)
            [
                'SubclassSubObject',
                'PersistentClientInfoLength'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root DataSourceArgument element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--DataSourceArgumentProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the DataSourceArgument
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--DataSourceArgumentProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a DataSourceArgument element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--DataSourceArgumentProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const dataSourceArgumentProcessor = new DataSourceArgumentProcessor(process.env.DEBUG === 'true');