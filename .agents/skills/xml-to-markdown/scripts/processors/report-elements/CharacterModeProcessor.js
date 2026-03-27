/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/CharacterModeProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <characterMode> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module CharacterModeProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class CharacterModeProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('characterMode');
    }
}
