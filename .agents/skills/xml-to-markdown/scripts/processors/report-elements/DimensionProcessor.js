/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/DimensionProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <dimension> elements.
 *   Extends RepeatingFrameProcessor for shared logic.
 * 
 * @module DimensionProcessor
 * @extends RepeatingFrameProcessor
 */

import { RepeatingFrameProcessor } from './RepeatingFrameProcessor.js';

export class DimensionProcessor extends RepeatingFrameProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('dimension');
    }
}
