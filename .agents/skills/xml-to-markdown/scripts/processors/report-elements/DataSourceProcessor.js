import { BaseReportElementProcessor } from '../BaseReportElementProcessor.js';
import { formatSQL } from '../../utils/codeUtils.js';

export class DataSourceProcessor extends BaseReportElementProcessor {
    constructor(elementName) {
        super(elementName);
    }

    async process(element, context) {
        const data = await super.process(element, context);

        if (element.select) {
            const selects = Array.isArray(element.select) ? element.select : [element.select];
            const sqlParts = [];

            for (const sel of selects) {
                const text = sel._ || (typeof sel === 'string' ? sel : '');
                if (text) sqlParts.push(text.trim());
            }

            data.sql = sqlParts.join('\n');
        }

        return data;
    }

    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        // Skip if no name and no sql (likely artifact or generic container mistaken for DS)
        if (!data.attributes.name && !data.sql) return;

        mdOutput.push(`### DataSource: ${data.attributes.name || 'Unnamed Source'}`);

        if (data.sql) {
            mdOutput.push('**SQL Query:**');
            mdOutput.push('```sql');
            mdOutput.push(formatSQL(data.sql));
            mdOutput.push('```\n');
        }

        if (generateChildMarkdown && data.children) {
            for (const child of data.children) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}
