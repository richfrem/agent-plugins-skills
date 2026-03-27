/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/LayoutPrivateProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <layoutPrivate> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module LayoutPrivateProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class LayoutPrivateProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('layoutPrivate');
    }
}
