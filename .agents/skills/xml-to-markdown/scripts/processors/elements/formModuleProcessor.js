/**
 * tools/standalone/xml-to-markdown/src/processors/elements/formModuleProcessor.js
 * ================================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms FormModule elements. FormModule is the root container
 *   for an Oracle Form, holding all Blocks, Canvases, Windows, and Triggers.
 * 
 * Input:
 *   - Parsed <FormModule> XML element (from _fmb.xml files)
 * 
 * Output:
 *   - Structured form metadata with name, title, menu references
 *   - Markdown document with form structure
 * 
 * Key Attributes Extracted:
 *   - Name: Form module name (e.g., FORM0000)
 *   - Title: Window title displayed to users
 *   - MenuModule: Associated menu file
 *   - FirstNavigationBlockName: Initial block on form open
 *   - ConsoleWindow: Window for status messages
 * 
 * Child Elements:
 *   - Block, Canvas, Window, Trigger, ProgramUnit
 *   - Alert, Lov, RecordGroup, Relation
 *   - AttachedLibrary (important for dependency tracking)
 * 
 * Usage:
 *   import { formModuleProcessor } from './formModuleProcessor.js';
 *   const result = await formModuleProcessor.processRootElement(formElement);
 * 
 * @module FormModuleProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class FormModuleProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('FormModule',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'SavepointMode',
                'Use3dControls',
                'CursorMode',
                'InteractionMode',
                'IsolationMode',
                'LanguageDirection',
                'MaximumQueryTime',
                'MaximumRecordsFetched',
                'MouseNavigationLimit',
                'NewdeferReqEnf',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'RuntimeComp',
                'ValidationUnit',
                'Comment',
                'ConsoleWindow',
                'FirstNavigationBlockName',
                'HelpBookTitle',
                'HorizontalToolbarCanvas',
                'InitializeMenu',
                'MenuModule',
                'MenuRole',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'RecordVisualAttributeGroupName',
                'Title',
                'VerticalToolbarCanvas'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }


    /**
     * Process the root FormModule element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--FormModuleProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the FormModule
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--FormModuleProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the FormModule
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--FormModuleProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const formModuleProcessor = new FormModuleProcessor(process.env.DEBUG === 'true');