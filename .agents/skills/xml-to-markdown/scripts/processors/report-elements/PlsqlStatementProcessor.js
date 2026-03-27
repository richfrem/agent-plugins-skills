/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/PlsqlStatementProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <plsqlStatement> elements.
 *   Extends ProgramUnitProcessor for shared logic.
 * 
 * @module PlsqlStatementProcessor
 * @extends ProgramUnitProcessor
 */

import { ProgramUnitProcessor } from './ProgramUnitProcessor.js';

export class PlsqlStatementProcessor extends ProgramUnitProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('plsqlStatement');
    }
}
