/**
 * tools/standalone/xml-to-markdown/src/processors/elements/moduleParameterProcessor.js
 * =====================================================================================
 * 
 * Purpose:
 *   Processes ModuleParameter elements. Parameters passed to forms via CALL_FORM
 *   or OPEN_FORM, enabling inter-form communication.
 * 
 * Key Attributes: Name, ParameterDataType, ParameterInitialValue, MaximumLength
 * 
 * @module ModuleParameterProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ModuleParameterProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('ModuleParameter',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'SubclassObjectGroup',
                'ParentModuleType',
                'ParentType',
                'ParameterDataType',
                'PersistentClientInfoLength',
                'Comment',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'ParameterInitializeValue',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }


    /**
     * Process the root ModuleParameter element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ModuleParameterProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the ModuleParameter
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ModuleParameterProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the ModuleParameter
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ModuleParameterProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const moduleParameterProcessor = new ModuleParameterProcessor(process.env.DEBUG === 'true');