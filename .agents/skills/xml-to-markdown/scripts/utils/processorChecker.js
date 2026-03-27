/**
 * tools/standalone/xml-to-markdown/src/utils/processorChecker.js
 * ================================================================
 * 
 * Purpose:
 *   Utility to audit processor coverage. Scans XML files for element types
 *   and compares against available processors to identify gaps.
 * 
 * Exports:
 *   - ProcessorChecker: Class with loadProcessors(), scanXmlFiles(), check()
 *   - processorChecker: Singleton instance
 * 
 * @module processorChecker
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { glob } from 'glob';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '../..');

/**
 * Utility to check which XML elements have processors and which ones don't
 */
export class ProcessorChecker {
    constructor() {
        this.processors = new Set();
        this.xmlElements = new Set();
    }

    /**
     * Load all processors from the elements directory
     */
    async loadProcessors() {
        const processorFiles = await glob('src/processors/elements/*Processor.js', { cwd: rootDir });

        for (const file of processorFiles) {
            const processorName = path.basename(file, '.js');
            const elementType = processorName.replace('Processor', '').toLowerCase();
            this.processors.add(elementType);
        }
    }

    /**
     * Scan XML files for elements
     */
    async scanXmlFiles() {
        const xmlFiles = await glob('test-data/**/*.xml', { cwd: rootDir });
        const xmlInputFiles = await glob('inputs/**/*.xml', { cwd: rootDir });
        const allXmlFiles = [...xmlFiles, ...xmlInputFiles];

        for (const file of allXmlFiles) {
            const content = fs.readFileSync(path.join(rootDir, file), 'utf8');
            const elements = content.match(/<([A-Z][a-zA-Z]+)/g);
            if (elements) {
                elements.forEach(element => {
                    // Defensive: ensure element is a string and matches expected pattern
                    let elementType = '';
                    if (typeof element === 'string') {
                        // Remove all leading '<' characters and only keep valid tag name
                        elementType = element.replace(/^<+/, '').replace(/[^a-zA-Z0-9:_-].*$/, '').toLowerCase();
                    }
                    if (elementType) {
                        this.xmlElements.add(elementType);
                    }
                });
            }
        }
    }

    /**
     * Generate a report of processed and unprocessed elements
     */
    generateReport() {
        const processed = [];
        const unprocessed = [];

        for (const element of this.xmlElements) {
            if (this.processors.has(element)) {
                processed.push(element);
            } else {
                unprocessed.push(element);
            }
        }

        return {
            processed: processed.sort(),
            unprocessed: unprocessed.sort(),
            totalProcessed: processed.length,
            totalUnprocessed: unprocessed.length,
            totalElements: this.xmlElements.size
        };
    }

    /**
     * Run the check and return results
     */
    async check() {
        await this.loadProcessors();
        await this.scanXmlFiles();
        return this.generateReport();
    }
}

// Create and export a singleton instance
export const processorChecker = new ProcessorChecker();