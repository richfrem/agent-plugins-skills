/**
 * tools/standalone/xml-to-markdown/src/processors/elements/attachedLibraryProcessor.js
 * =====================================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms AttachedLibrary elements. AttachedLibrary references
 *   PL/SQL Libraries (.pll) that provide shared code to the form.
 * 
 * Input:
 *   - Parsed <AttachedLibrary> XML element
 * 
 * Output:
 *   - Library name and location data for dependency tracking
 *   - Markdown section listing attached libraries
 * 
 * Key Attributes Extracted:
 *   - Name: Library name (e.g., EXAMPLE_LIB, AGLIB)
 *   - LibraryLocation: File path to the .pll file
 *   - LibrarySource: Source type (FILE, DATABASE)
 * 
 * Importance:
 *   This processor is CRITICAL for dependency analysis. AttachedLibrary
 *   elements reveal which shared code libraries a form depends on.
 * 
 * Usage:
 *   import { attachedLibraryProcessor } from './attachedLibraryProcessor.js';
 *   const result = await attachedLibraryProcessor.processRootElement(libElement);
 * 
 * @module AttachedLibraryProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class AttachedLibraryProcessor extends BaseProcessor {
    constructor(debug = false) {
        super(
            'AttachedLibrary',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd: LibrarySource, PersistentClientInfoLength, Comment, LibraryLocation)
            [
                'LibrarySource',
                'PersistentClientInfoLength',
                'Comment',
                'LibraryLocation'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root AttachedLibrary element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--AttachedLibraryProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the AttachedLibrary
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--AttachedLibraryProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing an AttachedLibrary element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--AttachedLibraryProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const attachedLibraryProcessor = new AttachedLibraryProcessor(process.env.DEBUG === 'true');