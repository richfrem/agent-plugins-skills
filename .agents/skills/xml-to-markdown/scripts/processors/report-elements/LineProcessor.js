/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/LineProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <line> elements.
 *   Extends GraphicsProcessor for shared logic.
 * 
 * @module LineProcessor
 * @extends GraphicsProcessor
 */

import { GraphicsProcessor } from './GraphicsProcessor.js';

export class LineProcessor extends GraphicsProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('line');
    }
}
