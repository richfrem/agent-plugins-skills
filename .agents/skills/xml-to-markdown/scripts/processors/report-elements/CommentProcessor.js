/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/CommentProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <comment> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module CommentProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class CommentProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('comment');
    }
}
