/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/SystemParameterProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <systemParameter> elements.
 *   Extends ParameterProcessor for shared logic.
 * 
 * @module SystemParameterProcessor
 * @extends ParameterProcessor
 */

import { ParameterProcessor } from './ParameterProcessor.js';

export class SystemParameterProcessor extends ParameterProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('systemParameter');
    }
}
