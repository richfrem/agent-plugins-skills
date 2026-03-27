/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/PlaceholderProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <placeholder> elements.
 *   Extends FormulaProcessor for shared logic.
 * 
 * @module PlaceholderProcessor
 * @extends FormulaProcessor
 */

import { FormulaProcessor } from './FormulaProcessor.js';

export class PlaceholderProcessor extends FormulaProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('placeholder');
    }
}
