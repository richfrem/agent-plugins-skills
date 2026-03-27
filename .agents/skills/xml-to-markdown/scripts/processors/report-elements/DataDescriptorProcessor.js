/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/DataDescriptorProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <dataDescriptor> elements.
 *   Extends DataItemProcessor for shared logic.
 * 
 * @module DataDescriptorProcessor
 * @extends DataItemProcessor
 */

import { DataItemProcessor } from './DataItemProcessor.js';

export class DataDescriptorProcessor extends DataItemProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('dataDescriptor');
    }
}
