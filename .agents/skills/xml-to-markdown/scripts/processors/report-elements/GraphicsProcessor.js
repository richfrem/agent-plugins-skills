/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/GraphicsProcessor.js
 * ====================================================================================
 * 
 * Purpose:
 *   Processes graphical layout elements.
 * 
 * Schema Elements:
 *   - line, arc, rectangle, image
 *   - polyline, roundedRectangle
 * 
 * @module GraphicsProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class GraphicsProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    enrichData(data, element) {
        const attrs = data.attributes;
        data.summary = `${this.elementName}`;
        if (attrs.name) data.summary += ` (${attrs.name})`;

        return data;
    }
}
