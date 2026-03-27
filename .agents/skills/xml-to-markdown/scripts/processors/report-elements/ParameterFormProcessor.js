/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ParameterFormProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <parameterForm> elements.
 *   Extends GroupProcessor for shared logic.
 * 
 * @module ParameterFormProcessor
 * @extends GroupProcessor
 */

import { GroupProcessor } from './GroupProcessor.js';

export class ParameterFormProcessor extends GroupProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('parameterForm');
    }
}
