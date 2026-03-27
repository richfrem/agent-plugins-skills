/**
 * tools/standalone/xml-to-markdown/src/processors/elements/blockProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Block elements. Blocks are data containers that
 *   hold Items (fields) and manage database operations (query, insert, update, delete).
 * 
 * Input:
 *   - Parsed <Block> XML element with 70+ possible attributes
 * 
 * Output:
 *   - Structured block data with name, query source, DML settings
 *   - Markdown section with attribute tables
 * 
 * Key Attributes Extracted:
 *   - Name: Block identifier
 *   - QueryDataSourceName: Table/view name for queries
 *   - WhereClause, OrderByClause: Query filters
 *   - DML settings: InsertAllowed, UpdateAllowed, DeleteAllowed
 *   - DatabaseBlock: Whether block is database-backed
 * 
 * Child Elements:
 *   - Item (fields), Trigger (event handlers), Relation (master-detail)
 * 
 * Usage:
 *   import { blockProcessor } from './blockProcessor.js';
 *   const result = await blockProcessor.processRootElement(blockElement);
 * 
 * @module BlockProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class BlockProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Block',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (all other attributes from forms.xsd)
            [
                'DatabaseBlock',
                'DeleteAllowed',
                'DirtyInfo',
                'DMLReturnValue',
                'EnforcedColumnSecurity',
                'EnforcedPrimaryKey',
                'IncludeRefitem',
                'InsertAllowed',
                'PrecompSummary',
                'QueryAllRecords',
                'QueryAllowed',
                'ReverseDirection',
                'ShowScrollbar',
                'SingleRecord',
                'SubclassObjectGroup',
                'UpdateAllowed',
                'UpdateChangedColumns',
                'DMLArraySize',
                'DMLDataType',
                'KeyMode',
                'LanguageDirection',
                'LockMode',
                'MaximumQueryTime',
                'MaximumRecordsFetched',
                'NavigationStyle',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'QueryDataSourceType',
                'RecordOrientation',
                'RecordsBufferedCount',
                'RecordsDisplayCount',
                'RecordsFetchedCount',
                'RowBandingFreq',
                'ScrollbarLength',
                'ScrollbarOrientation',
                'ScrollbarWidth',
                'ScrollbarXPosition',
                'ScrollbarYPosition',
                'Alias',
                'BackColor',
                'Comment',
                'DeleteProcedureName',
                'DMLDataName',
                'FillPattern',
                'ForegroundColor',
                'InsertProcedureName',
                'LockProcedureName',
                'NextNavigationBlockName',
                'OptionHint',
                'OrderByClause',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'PreviousNavigationBlockName',
                'QueryDataSourceName',
                'RecordVisualAttributeGroupName',
                'ScrollbarCanvasName',
                'ScrollbarTabPageName',
                'UpdateProcedureName',
                'VisualAttributeName',
                'WhereClause',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Block element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--BlockProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Block
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--BlockProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing an Block element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--BlockProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const blockProcessor = new BlockProcessor(process.env.DEBUG === 'true');