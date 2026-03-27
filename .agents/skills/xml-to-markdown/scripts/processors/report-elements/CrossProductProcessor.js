/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/CrossProductProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <crossProduct> elements.
 *   Extends RepeatingFrameProcessor for shared logic.
 * 
 * @module CrossProductProcessor
 * @extends RepeatingFrameProcessor
 */

import { RepeatingFrameProcessor } from './RepeatingFrameProcessor.js';

export class CrossProductProcessor extends RepeatingFrameProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('crossProduct');
    }
}
