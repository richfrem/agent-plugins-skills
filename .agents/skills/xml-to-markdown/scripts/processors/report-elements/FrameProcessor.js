/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/FrameProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <frame> elements.
 *   Extends RepeatingFrameProcessor for shared logic.
 * 
 * @module FrameProcessor
 * @extends RepeatingFrameProcessor
 */

import { RepeatingFrameProcessor } from './RepeatingFrameProcessor.js';

export class FrameProcessor extends RepeatingFrameProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('frame');
    }
}
