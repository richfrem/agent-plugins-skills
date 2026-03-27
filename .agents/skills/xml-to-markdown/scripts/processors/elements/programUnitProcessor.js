/**
 * tools/standalone/xml-to-markdown/src/processors/elements/programUnitProcessor.js
 * =================================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms ProgramUnit elements. ProgramUnits contain PL/SQL
 *   packages, procedures, and functions defined within the form.
 * 
 * Input:
 *   - Parsed <ProgramUnit> XML element
 * 
 * Output:
 *   - Structured code unit data with name, type, and source code
 *   - Markdown section with formatted PLSQL code block
 * 
 * Key Attributes Extracted:
 *   - Name: Unit name (procedure/function/package name)
 *   - ProgramUnitType: PROCEDURE, FUNCTION, PACKAGE_SPEC, PACKAGE_BODY
 *   - ProgramUnitText: Full PL/SQL source code
 *   - Comment: Developer notes
 * 
 * Importance:
 *   ProgramUnits reveal form-level business logic that may need
 *   extraction and modernization as separate API services.
 * 
 * Usage:
 *   import { programUnitProcessor } from './programUnitProcessor.js';
 *   const result = await programUnitProcessor.processRootElement(puElement);
 * 
 * @module ProgramUnitProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ProgramUnitProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('ProgramUnit',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd: SubclassObjectGroup, ParentModuleType, ParentType, PersistentClientInfoLength, ProgramUnitType, Comment, ParentFilename, ParentFilepath, ParentModule, ParentName, ProgramUnitText, SmartClass)
            [
                'SubclassObjectGroup',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'ProgramUnitType',
                'Comment',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'ProgramUnitText',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root ProgramUnit element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ProgramUnitProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the ProgramUnit
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ProgramUnitProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a ProgramUnit element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ProgramUnitProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const programUnitProcessor = new ProgramUnitProcessor(process.env.DEBUG === 'true');