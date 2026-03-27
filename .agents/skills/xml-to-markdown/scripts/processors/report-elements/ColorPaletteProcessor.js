/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ColorPaletteProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <colorPalette> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module ColorPaletteProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class ColorPaletteProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('colorPalette');
    }
}
