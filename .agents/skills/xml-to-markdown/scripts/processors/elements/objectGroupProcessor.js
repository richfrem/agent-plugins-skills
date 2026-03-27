/**
 * tools/standalone/xml-to-markdown/src/processors/elements/objectGroupProcessor.js
 * =================================================================================
 * 
 * Purpose:
 *   Processes ObjectGroup elements in ObjectLibraries. Groups logically related
 *   objects for subclassing (e.g., all items in a reusable block template).
 * 
 * Key Attributes: Name, Comment
 * Child Elements: ObjectGroupChild
 * 
 * @module ObjectGroupProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ObjectGroupProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('ObjectGroup',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd: DirtyInfo, ObjectGroupType, ParentModuleType, ParentType, PersistentClientInfoLength, Comment, ParentFilename, ParentFilepath, ParentModule, ParentName, SmartClass)
            [
                'DirtyInfo',
                'ObjectGroupType',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'Comment',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root ObjectGroup element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ObjectGroupProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the ObjectGroup
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ObjectGroupProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the ObjectGroup
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ObjectGroupProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const objectGroupProcessor = new ObjectGroupProcessor(process.env.DEBUG === 'true');