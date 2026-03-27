/**
 * tools/standalone/xml-to-markdown/src/processors/elements/ObjectGroupChildProcessor.js
 * ======================================================================================
 * 
 * Purpose:
 *   Processes ObjectGroupChild elements. References to objects included in a group,
 *   enabling inheritance of properties from ObjectLibrary templates.
 * 
 * Key Attributes: Name, SubclassObjectGroup, SubclassModule
 * 
 * @module ObjectGroupChildProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ObjectGroupChildProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Objectgroupchild',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd: DirtyInfo, SubclassSubObject, PersistentClientInfoLength, Type, ProgramUnitType)
            [
                'DirtyInfo',
                'SubclassSubObject',
                'PersistentClientInfoLength',
                'Type',
                'ProgramUnitType'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Objectgroupchild element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ObjectGroupChildProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Objectgroupchild
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ObjectGroupChildProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Objectgroupchild
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ObjectGroupChildProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const objectGroupChildProcessor = new ObjectGroupChildProcessor(process.env.DEBUG === 'true');