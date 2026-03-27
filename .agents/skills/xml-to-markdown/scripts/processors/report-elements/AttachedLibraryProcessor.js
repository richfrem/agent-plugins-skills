/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/AttachedLibraryProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <attachedLibrary> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module AttachedLibraryProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class AttachedLibraryProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('attachedLibrary');
    }
}
