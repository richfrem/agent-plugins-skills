/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/ListOfValuesProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <listOfValues> elements.
 *   Extends GenericReportElementProcessor for shared logic.
 * 
 * @module ListOfValuesProcessor
 * @extends GenericReportElementProcessor
 */

import { GenericReportElementProcessor } from './GenericReportElementProcessor.js';

export class ListOfValuesProcessor extends GenericReportElementProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('listOfValues');
    }
}
