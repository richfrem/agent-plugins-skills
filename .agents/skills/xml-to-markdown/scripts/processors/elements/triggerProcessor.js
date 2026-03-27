/**
 * tools/standalone/xml-to-markdown/src/processors/elements/triggerProcessor.js
 * =============================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Trigger elements. Triggers contain PL/SQL code
 *   that executes in response to events (WHEN-BUTTON-PRESSED, PRE-QUERY, etc.).
 * 
 * Input:
 *   - Parsed <Trigger> XML element
 * 
 * Output:
 *   - Structured trigger data with name and PL/SQL code
 *   - Markdown section with formatted PLSQL code block
 * 
 * Key Attributes Extracted:
 *   - Name: Trigger event name (WHEN-NEW-FORM-INSTANCE, PRE-INSERT, etc.)
 *   - TriggerText: PL/SQL code to execute
 *   - Comment: Developer notes
 * 
 * Trigger Naming Patterns:
 *   - Form-level: WHEN-NEW-FORM-INSTANCE, PRE-FORM, POST-FORM
 *   - Block-level: PRE-QUERY, POST-QUERY, PRE-INSERT, POST-INSERT
 *   - Item-level: WHEN-BUTTON-PRESSED, WHEN-VALIDATE-ITEM
 *   - Key triggers: KEY-ENTER, KEY-NEXT-ITEM
 * 
 * Usage:
 *   import { triggerProcessor } from './triggerProcessor.js';
 *   const result = await triggerProcessor.processRootElement(triggerElement);
 * 
 * @module TriggerProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class TriggerProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Trigger',
            // Mandatory attributes (from forms.xsd: Name, TriggerText)
            ['Name', 'TriggerText'],
            // Optional attributes (from forms.xsd: DirtyInfo, Comment)
            [
                'DirtyInfo',
                'Comment'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Trigger element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--TriggerProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Trigger
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--TriggerProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Trigger
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--TriggerProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const triggerProcessor = new TriggerProcessor(process.env.DEBUG === 'true');