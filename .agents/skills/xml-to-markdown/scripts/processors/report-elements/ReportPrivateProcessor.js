/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ReportPrivateProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <reportPrivate> elements.
 *   Extends MetadataProcessor for shared logic.
 * 
 * @module ReportPrivateProcessor
 * @extends MetadataProcessor
 */

import { MetadataProcessor } from './MetadataProcessor.js';

export class ReportPrivateProcessor extends MetadataProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('reportPrivate');
    }
}
