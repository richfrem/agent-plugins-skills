/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ImageProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <image> elements.
 *   Extends GraphicsProcessor for shared logic.
 * 
 * @module ImageProcessor
 * @extends GraphicsProcessor
 */

import { GraphicsProcessor } from './GraphicsProcessor.js';

export class ImageProcessor extends GraphicsProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('image');
    }
}
