/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/SelectProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <select> elements.
 *   Extends DataSourceProcessor for shared logic.
 * 
 * @module SelectProcessor
 * @extends DataSourceProcessor
 */

import { DataSourceProcessor } from './DataSourceProcessor.js';

export class SelectProcessor extends DataSourceProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('select');
    }
}
