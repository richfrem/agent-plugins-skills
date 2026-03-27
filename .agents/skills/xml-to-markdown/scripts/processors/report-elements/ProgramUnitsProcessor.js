/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ProgramUnitsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <programUnits> elements.
 *   Extends ProgramUnitProcessor for shared logic.
 * 
 * @module ProgramUnitsProcessor
 * @extends ProgramUnitProcessor
 */

import { ProgramUnitProcessor } from './ProgramUnitProcessor.js';

export class ProgramUnitsProcessor extends ProgramUnitProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('programUnits');
    }
}
