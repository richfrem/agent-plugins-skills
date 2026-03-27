/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/TextSegmentProcessor.js
 * ======================================================================================
 * 
 * Purpose:
 *   Processes text segments which combine font styling and string content.
 *   Flattened representation is useful for documentation.
 * 
 * Structure:
 *   <textSegment>
 *     <font .../>
 *     <string>Actual Content</string>
 *   </textSegment>
 * 
 * @module TextSegmentProcessor
 * @extends BaseReportElementProcessor
 */

import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';

export class TextSegmentProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    enrichData(data, element) {
        // Flatten children to find text and font
        // Children processing has already run, so we look at data.children

        const fontNode = data.children.find(c => c.type === 'font');
        const stringNode = data.children.find(c => c.type === 'string'); // We need a StringProcessor? Or generic.

        // If string processor doesn't exist, we might have raw objects in children 
        // or we need to look at raw element if 'string' is just a container wrapper

        let textContent = '';
        if (element.string) {
            const strEl = Array.isArray(element.string) ? element.string[0] : element.string;
            textContent = strEl._ || (typeof strEl === 'string' ? strEl : '');
        }

        data.text = textContent;
        data.font = fontNode ? fontNode.summary : null;

        return data;
    }

    generateMarkdown(data, mdOutput) {
        if (data.text) {
            let line = data.text;
            if (data.font) line += ` *(${data.font})*`;
            mdOutput.push(`- ${line}`);
        }
    }
}
