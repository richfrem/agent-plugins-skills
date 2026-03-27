/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/PolylineProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <polyline> elements.
 *   Extends GraphicsProcessor for shared logic.
 * 
 * @module PolylineProcessor
 * @extends GraphicsProcessor
 */

import { GraphicsProcessor } from './GraphicsProcessor.js';

export class PolylineProcessor extends GraphicsProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('polyline');
    }
}
