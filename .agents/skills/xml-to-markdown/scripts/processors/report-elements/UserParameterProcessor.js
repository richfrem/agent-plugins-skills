/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/UserParameterProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <userParameter> elements.
 *   Extends ParameterProcessor for shared logic.
 * 
 * @module UserParameterProcessor
 * @extends ParameterProcessor
 */

import { ParameterProcessor } from './ParameterProcessor.js';

export class UserParameterProcessor extends ParameterProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('userParameter');
    }
}
