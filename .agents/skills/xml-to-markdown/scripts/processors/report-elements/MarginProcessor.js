/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/MarginProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <margin> elements.
 *   Extends GroupProcessor for shared logic.
 * 
 * @module MarginProcessor
 * @extends GroupProcessor
 */

import { GroupProcessor } from './GroupProcessor.js';

export class MarginProcessor extends GroupProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('margin');
    }
}
