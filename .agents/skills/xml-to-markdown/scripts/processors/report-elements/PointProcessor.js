/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/PointProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <point> elements.
 *   Extends GeometryInfoProcessor for shared logic.
 * 
 * @module PointProcessor
 * @extends GeometryInfoProcessor
 */

import { GeometryInfoProcessor } from './GeometryInfoProcessor.js';

export class PointProcessor extends GeometryInfoProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('point');
    }
}
