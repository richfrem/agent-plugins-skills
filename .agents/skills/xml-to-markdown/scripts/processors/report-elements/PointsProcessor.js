/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/PointsProcessor.js
 * ===========================================================================
 * 
 * Purpose:
 *   Processor for <points> elements.
 *   Extends GeometryInfoProcessor for shared logic.
 * 
 * @module PointsProcessor
 * @extends GeometryInfoProcessor
 */

import { GeometryInfoProcessor } from './GeometryInfoProcessor.js';

export class PointsProcessor extends GeometryInfoProcessor {
    constructor() { // registry passes elementName but we can hardcode or pass through
        super('points');
    }
}
