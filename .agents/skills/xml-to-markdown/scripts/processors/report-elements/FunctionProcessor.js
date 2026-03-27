/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/FunctionProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <function> elements.
 *   Extends ProgramUnitProcessor for shared logic.
 * 
 * @module FunctionProcessor
 * @extends ProgramUnitProcessor
 */

import { ProgramUnitProcessor } from './ProgramUnitProcessor.js';

export class FunctionProcessor extends ProgramUnitProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('function');
    }
}
