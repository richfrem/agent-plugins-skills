/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/GeometryInfoProcessor.js
 * =========================================================================================
 * 
 * Purpose:
 *   Processes geometry and layout coordinates.
 *   Handles <geometryInfo> (bounding box) and <point> (vector nodes).
 * 
 * Schema Attributes:
 *   - x, y
 *   - width, height (geometryInfo only)
 * 
 * @module GeometryInfoProcessor
 * @extends BaseReportElementProcessor
 */

// Correct import path:
import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class GeometryInfoProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    enrichData(data, element) {
        const attrs = data.attributes;

        if (this.elementName === 'geometryInfo') {
            data.summary = `Box(${attrs.x},${attrs.y} ${attrs.width}x${attrs.height})`;
        } else if (this.elementName === 'point') {
            data.summary = `Pt(${attrs.x},${attrs.y})`;
        }

        return data;
    }

    generateMarkdown(data, mdOutput) {
        // Usually minimal output unless debug
        // mdOutput.push(`- ${data.summary}`);
    }
}
