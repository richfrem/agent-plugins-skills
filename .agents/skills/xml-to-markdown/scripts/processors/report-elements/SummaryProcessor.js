/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/SummaryProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <summary> elements.
 *   Extends FormulaProcessor for shared logic.
 * 
 * @module SummaryProcessor
 * @extends FormulaProcessor
 */

import { FormulaProcessor } from './FormulaProcessor.js';

export class SummaryProcessor extends FormulaProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('summary');
    }
}
