/**
 * tools/standalone/xml-to-markdown/src/processors/elements/ObjectLibraryTabProcessor.js
 * ======================================================================================
 * 
 * Purpose:
 *   Processes ObjectLibraryTab elements. Tabs organize objects within an ObjectLibrary
 *   for easier navigation in the Forms Builder IDE.
 * 
 * Key Attributes: Name, Label, Comment
 * Child Elements: ObjectGroup
 * 
 * @module ObjectLibraryTabProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ObjectLibraryTabProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('ObjectLibraryTab',
            // Mandatory attributes (from forms.xsd: Name, Label)
            ['Name', 'Label'],
            // Optional attributes (from forms.xsd: DirtyInfo, ObjectCount, PersistentClientInfoLength, Comment)
            [
                'DirtyInfo',
                'ObjectCount',
                'PersistentClientInfoLength',
                'Comment'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }


    /**
     * Process the root ObjectLibraryTab element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ObjectLibraryTabProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the ObjectLibraryTab
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ObjectLibraryTabProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a ObjectLibraryTab element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ObjectLibraryTabProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const objectLibraryTabProcessor = new ObjectLibraryTabProcessor(process.env.DEBUG === 'true');