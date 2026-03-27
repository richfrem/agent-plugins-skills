/**
 * tools/standalone/xml-to-markdown/src/processors/elements/objectLibraryProcessor.js
 * ===================================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms ObjectLibrary elements. ObjectLibrary is the root
 *   container for .olb files that hold reusable UI components and templates.
 * 
 * Input:
 *   - Parsed <ObjectLibrary> XML element (from _olb.xml files)
 * 
 * Output:
 *   - Structured library metadata with component counts
 *   - Markdown document with library contents
 * 
 * Key Attributes Extracted:
 *   - Name: Object library name (e.g., Project)
 *   - ObjectCount: Number of contained objects
 *   - Comment: Library description
 * 
 * Child Elements:
 *   - ObjectLibraryTab (organizational tabs)
 *   - ObjectGroup (component groups)
 * 
 * @module ObjectLibraryProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ObjectLibraryProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('ObjectLibrary',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
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
     * Process the root ObjectLibrary element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ObjectLibraryProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the ObjectLibrary
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ObjectLibraryProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a ObjectLibrary element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ObjectLibraryProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const objectLibraryProcessor = new ObjectLibraryProcessor(process.env.DEBUG === 'true');