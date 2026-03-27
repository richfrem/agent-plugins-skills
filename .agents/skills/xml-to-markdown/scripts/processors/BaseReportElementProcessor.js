/**
 * tools/standalone/xml-to-markdown/src/processors/report-elements/BaseReportElementProcessor.js
 * ==============================================================================================
 * 
 * Purpose:
 *   Abstract base class for all Oracle Report element processors. Provides common
 *   functionality for attribute extraction, child processing, and formatting specific
 *   to the Reports XML schema (which differs from Forms XML).
 * 
 * Key Differences from Forms BaseProcessor:
 *   - Schema is camelCase (e.g. `userParameter` not `UserParameter`)
 *   - Attributes are in `$` object but keys are camelCase (e.g. `datatype` not `DataType`)
 *   - Child elements handling tailored for xml2js structure
 * 
 * @module BaseReportElementProcessor
 */

export class BaseReportElementProcessor {
    /**
     * @param {string} elementName - The specific XML tag name this processor handles
     */
    constructor(elementName) {
        this.elementName = elementName;
    }

    /**
     * Main entry point for processing an element
     * @param {Object} element - The raw XML element
     * @param {Object} context - processing context (registry, etc)
     * @returns {Object} Processed data structure
     */
    async process(element, context) {
        if (!element) return null;

        // Collect stats
        if (context.stats) {
            context.stats.elements.add(this.elementName);
            if (typeof element === 'object') {
                const attrs = element.$ || {};
                context.stats.attributeCount += Object.keys(attrs).length;
            }
        }

        let data = {
            type: this.elementName
        };

        if (typeof element !== 'object') {
            // Handle primitive string content (e.g. <tag>text</tag>)
            data.text = String(element).trim();
            data.attributes = {};
            data.children = [];
        } else {
            // Handle element object structure
            data.attributes = this.extractAttributes(element);
            data.children = await this.processChildren(element, context);

            // Check for explicit text content identifier from xml2js
            if (element._) {
                data.text = element._.trim();
            }
        }

        // Allow subclasses to enrich data
        return this.enrichData(data, element);
    }

    /**
     * Extract attributes from the element
     * @param {Object} element 
     */
    extractAttributes(element) {
        return element.$ || {}; // xml2js stores attributes in $
    }

    /**
     * Process child elements recursively using the context registry
     * @param {Object} element 
     * @param {Object} context 
     */
    async processChildren(element, context) {
        const children = [];
        const { registry } = context;

        // Iterate over all keys that aren't attributes ($) or text (_)
        for (const key of Object.keys(element)) {
            if (key === '$' || key === '_' || key === '$$') continue;

            // Debug log for troubleshooting "0" issue
            if (key === '0') console.log('Found key "0" in element:', JSON.stringify(element, null, 2).substring(0, 200));

            const childElements = Array.isArray(element[key]) ? element[key] : [element[key]];

            for (const child of childElements) {
                // Find processor for this child type
                const processor = await registry.getProcessor(key);
                if (processor) {
                    const processedChild = await processor.process(child, context);
                    if (processedChild) children.push(processedChild);
                } else {
                    // Default generic handling if no processor found
                    // Can store as generic node or skip
                }
            }
        }
        return children;
    }

    /**
     * Hook for subclasses to add specific logic
     * @param {Object} data 
     * @param {Object} originalElement 
     */
    enrichData(data, originalElement) {
        return data;
    }

    /**
     * Format execution to markdown
     * @param {Object} data - Processed data
     * @param {Array} mdOutput - Markdown lines array
     */
    /**
     * Format execution to markdown
     * @param {Object} data - Processed data
     * @param {Array} mdOutput - Markdown lines array
     * @param {Function} [generateChildMarkdown] - Recursion callback
     */
    generateMarkdown(data, mdOutput, generateChildMarkdown) {
        // Default implementation - header and attributes table
        mdOutput.push(`### ${data.type}`);

        if (Object.keys(data.attributes).length > 0) {
            mdOutput.push(`| Attribute | Value |`);
            mdOutput.push(`|-----------|-------|`);
            for (const [key, val] of Object.entries(data.attributes)) {
                mdOutput.push(`| ${key} | ${val} |`);
            }
            mdOutput.push('');
        }

        // If generic processor or base, iterate children if callback provided
        if (generateChildMarkdown && data.children && data.children.length > 0) {
            for (const child of data.children) {
                generateChildMarkdown(child, mdOutput);
            }
        }
    }
}
