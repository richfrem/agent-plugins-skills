import { TextSegmentProcessor } from './TextSegmentProcessor.js';

export class FieldProcessor extends TextSegmentProcessor {
    constructor() {
        super('field');
    }

    generateMarkdown(data, mdOutput) {
        const name = data.attributes.name || 'Unnamed Field';
        const source = data.attributes.source ? ` (Source: \`${data.attributes.source}\`)` : '';

        mdOutput.push(`- **Field:** ${name}${source}`);
    }
}
