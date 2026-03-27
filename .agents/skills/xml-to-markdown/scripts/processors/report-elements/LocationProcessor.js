/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/LocationProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <location> elements.
 *   Extends GeometryInfoProcessor for shared logic.
 * 
 * @module LocationProcessor
 * @extends GeometryInfoProcessor
 */

import { GeometryInfoProcessor } from './GeometryInfoProcessor.js';

export class LocationProcessor extends GeometryInfoProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('location');
    }
}
