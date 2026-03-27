/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ArcProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <arc> elements.
 *   Extends GraphicsProcessor for shared logic.
 * 
 * @module ArcProcessor
 * @extends GraphicsProcessor
 */

import { GraphicsProcessor } from './GraphicsProcessor.js';

export class ArcProcessor extends GraphicsProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('arc');
    }
}
