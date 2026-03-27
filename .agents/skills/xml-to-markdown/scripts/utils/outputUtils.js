/**
 * tools/standalone/xml-to-markdown/src/utils/outputUtils.js
 * ==========================================================
 * 
 * Purpose:
 *   Output utilities for markdown generation. Creates structured output
 *   objects that handle both test and production modes for flexible testing.
 * 
 * Exports:
 *   - createOutputObject(): Factory for output collectors with push/join
 * 
 * @module outputUtils
 */

/**
 * Creates an output object that can be used for both testing and production
 * @param {Object} options - Configuration options
 * @param {boolean} options.isTestMode - Whether to create a test-mode output object
 * @returns {Object} Output object with push and join methods
 */
export function createOutputObject(options = { isTestMode: false }) {
    const lines = [];
    const output = {
        length: 0,
        lines
    };

    // Add push method that handles both test and production modes
    output.push = function (item) {
        if (options.isTestMode) {
            // Test mode: Always wrap items in type/text objects
            if (typeof item === 'string') {
                this[this.length++] = { type: 'text', text: item };
                lines.push(item);
            } else if (item.type === 'text') {
                this[this.length++] = item;
                lines.push(item.text);
            } else if (item.type === 'code') {
                this[this.length++] = item;
                lines.push('```' + item.language + '\n' + item.code + '\n```\n');
            } else if (item.type === 'heading') {
                this[this.length++] = item;
                lines.push('#'.repeat(item.level) + ' ' + item.text + '\n');
            } else {
                this[this.length++] = item;
                lines.push(item);
            }
        } else {
            // Production mode: Handle items based on their type
            if (typeof item === 'string') {
                lines.push(item);
            } else if (item.type === 'text') {
                lines.push(item.text + '\n');
            } else if (item.type === 'code') {
                lines.push('```' + item.language + '\n' + item.code + '\n```\n');
            } else if (item.type === 'heading') {
                lines.push('#'.repeat(item.level) + ' ' + item.text + '\n');
            } else {
                lines.push(item);
            }
            this.length = lines.length;
        }
    };

    // Add join method that works in both modes
    output.join = function (separator = '') {
        if (options.isTestMode) {
            const items = [];
            for (let i = 0; i < this.length; i++) {
                const item = this[i];
                items.push(item.text || item.code || '');
            }
            return items.join(separator);
        }
        return lines.join(separator);
    };

    // Add getLines method for accessing raw lines
    output.getLines = function () {
        return lines;
    };

    return output;
} 