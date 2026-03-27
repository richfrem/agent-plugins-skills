/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/RectangleProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <rectangle> elements.
 *   Extends GraphicsProcessor for shared logic.
 * 
 * @module RectangleProcessor
 * @extends GraphicsProcessor
 */

import { GraphicsProcessor } from './GraphicsProcessor.js';

export class RectangleProcessor extends GraphicsProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('rectangle');
    }
}
