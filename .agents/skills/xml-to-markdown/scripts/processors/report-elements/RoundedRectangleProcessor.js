/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/RoundedRectangleProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <roundedRectangle> elements.
 *   Extends GraphicsProcessor for shared logic.
 * 
 * @module RoundedRectangleProcessor
 * @extends GraphicsProcessor
 */

import { GraphicsProcessor } from './GraphicsProcessor.js';

export class RoundedRectangleProcessor extends GraphicsProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('roundedRectangle');
    }
}
