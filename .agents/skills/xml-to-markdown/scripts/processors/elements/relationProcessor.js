/**
 * tools/standalone/xml-to-markdown/src/processors/elements/relationProcessor.js
 * ==============================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Relation elements. Relations define master-detail
 *   relationships between blocks for coordinated data navigation.
 * 
 * Input:
 *   - Parsed <Relation> XML element
 * 
 * Output:
 *   - Structured relation data with join conditions
 *   - Markdown section with master-detail configuration
 * 
 * Key Attributes Extracted:
 *   - Name: Relation identifier
 *   - DetailBlock: Child block name
 *   - JoinCondition: SQL linking master to detail
 *   - RelationType: JOIN, REF
 *   - AutoQuery: Whether detail auto-queries on master navigation
 *   - DeleteRecord: CASCADE, ISOLATED, NON_ISOLATED
 * 
 * @module RelationProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class RelationProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Relation',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd: AutoQuery, Deferred, DirtyInfo, PreventMasterlessOperations, SubclassSubObject, DeleteRecord, PersistentClientInfoLength, RelationType, Comment, DetailBlock, DetailItemref, JoinCondition)
            [
                'AutoQuery',
                'Deferred',
                'DirtyInfo',
                'PreventMasterlessOperations',
                'SubclassSubObject',
                'DeleteRecord',
                'PersistentClientInfoLength',
                'RelationType',
                'Comment',
                'DetailBlock',
                'DetailItemref',
                'JoinCondition'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Relation element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--RelationProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Relation
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--RelationProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Relation
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--RelationProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const relationProcessor = new RelationProcessor(process.env.DEBUG === 'true');