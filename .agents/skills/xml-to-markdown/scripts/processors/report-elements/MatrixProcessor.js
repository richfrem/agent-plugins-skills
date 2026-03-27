/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/MatrixProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <matrix> elements.
 *   Extends RepeatingFrameProcessor for shared logic.
 * 
 * @module MatrixProcessor
 * @extends RepeatingFrameProcessor
 */

import { RepeatingFrameProcessor } from './RepeatingFrameProcessor.js';

export class MatrixProcessor extends RepeatingFrameProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('matrix');
    }
}
