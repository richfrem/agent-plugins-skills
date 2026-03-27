import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';
import { formatPLSQL } from '../../utils/codeUtils.js';

export class ProgramUnitProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    async process(element, context) {
        const data = await super.process(element, context);

        if (this.elementName === 'function' || this.elementName === 'plsqlStatement') {
            let text = '';
            if (element.textSource) {
                const ts = Array.isArray(element.textSource) ? element.textSource[0] : element.textSource;
                text = ts._ || (typeof ts === 'string' ? ts : '');
            } else {
                text = element._ || (typeof element === 'string' ? element : '');
            }
            data.code = text ? text.trim() : '';
        }

        return data;
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        if (this.elementName === 'programUnits') {
            if (data.children.length > 0) {
                mdOutput.push('## Program Units');
                if (generateChildMarkdown) {
                    for (const child of data.children) {
                        generateChildMarkdown(child, mdOutput);
                    }
                }
            }
            return;
        }

        if (this.elementName === 'function') {
            mdOutput.push(`### Function: ${data.attributes.name}`);
            if (data.attributes.returnType) {
                mdOutput.push(`**Returns:** ${data.attributes.returnType}`);
            }
            if (data.code) {
                mdOutput.push('```sql');
                mdOutput.push(formatPLSQL(data.code));
                mdOutput.push('```\n');
            }
        }
    }
}
