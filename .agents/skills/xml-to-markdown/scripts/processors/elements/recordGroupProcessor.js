/**
 * tools/standalone/xml-to-markdown/src/processors/elements/recordGroupProcessor.js
 * =================================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms RecordGroup elements. RecordGroups are data structures
 *   that hold query results or static data for LOVs and programmatic use.
 * 
 * Input:
 *   - Parsed <RecordGroup> XML element
 * 
 * Output:
 *   - Structured record group data with query and column definitions
 *   - Markdown section with query SQL
 * 
 * Key Attributes Extracted:
 *   - Name: RecordGroup identifier
 *   - RecordGroupType: QUERY, STATIC
 *   - RecordGroupQuery: SQL SELECT statement
 *   - RecordGroupFetchSize: Number of rows to fetch
 * 
 * Child Elements:
 *   - RecordGroupColumn (column definitions)
 * 
 * @module RecordGroupProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class RecordGroupProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('RecordGroup',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'SubclassObjectGroup',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'RecordGroupFetchSize',
                'RecordGroupType',
                'Comment',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'RecordGroupQuery',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root RecordGroup element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--RecordGroupProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the RecordGroup
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--RecordGroupProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a RecordGroup element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--RecordGroupProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const recordGroupProcessor = new RecordGroupProcessor(process.env.DEBUG === 'true');