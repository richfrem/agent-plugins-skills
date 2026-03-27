/**
 * tools/standalone/xml-to-markdown/src/utils/analyzeProgramUnits.js
 * ===================================================================
 * 
 * Purpose:
 *   Standalone script to analyze ProgramUnit elements from Oracle Forms XML.
 *   Generates reports of required processors, test data, and tests.
 * 
 * Usage:
 *   node src/utils/analyzeProgramUnits.js
 * 
 * @module analyzeProgramUnits
 */

import fs from 'fs';
import path from 'path';
import { XMLParser } from 'fast-xml-parser';

export class ProgramUnitAnalyzer {
    constructor() {
        this.elementTypes = new Set();
        this.programUnitTypes = new Set();
        this.processors = new Set();
        this.testData = new Set();
        this.tests = new Set();
        this.parser = new XMLParser({
            ignoreAttributes: false,
            attributeNamePrefix: '@_',
            isArray: (name, jpath, isLeafNode, isAttribute) => {
                return name === 'ProgramUnit' || name === 'Source';
            }
        });
    }

    async analyzeDirectory(directory) {
        const files = await fs.promises.readdir(directory);

        for (const file of files) {
            const fullPath = path.join(directory, file);
            const stat = await fs.promises.stat(fullPath);

            if (stat.isDirectory()) {
                await this.analyzeDirectory(fullPath);
            } else if (file.endsWith('.xml')) {
                await this.analyzeFile(fullPath);
            }
        }
    }

    async analyzeFile(filePath) {
        try {
            const xmlData = await fs.promises.readFile(filePath, 'utf8');
            const jsonObj = this.parser.parse(xmlData);

            this.processProgramUnits(jsonObj);
        } catch (error) {
            console.error(`Error analyzing file ${filePath}:`, error);
        }
    }

    processProgramUnits(obj) {
        if (!obj) return;

        // Process ProgramUnit elements
        if (obj.ProgramUnit || obj.ProgramUnits?.ProgramUnit) {
            const programUnits = obj.ProgramUnit || obj.ProgramUnits?.ProgramUnit;
            const units = Array.isArray(programUnits) ? programUnits : [programUnits];

            for (const pu of units) {
                this.processProgramUnit(pu);
            }
        }

        // Recursively process child objects
        for (const key in obj) {
            if (typeof obj[key] === 'object') {
                this.processProgramUnits(obj[key]);
            }
        }
    }

    processProgramUnit(pu) {
        if (!pu) return;

        // Add attributes as element types
        if (pu['@_Name']) this.elementTypes.add('Name');
        if (pu['@_Type']) this.elementTypes.add('Type');

        // Add ProgramUnit type
        if (pu.ProgramUnitType) {
            this.programUnitTypes.add(typeof pu.ProgramUnitType === 'string' ? pu.ProgramUnitType : pu.ProgramUnitType['#text']);
        }

        // Process all child elements
        for (const key in pu) {
            if (!key.startsWith('@_')) {
                // Remove any XML-specific prefixes/attributes
                const cleanKey = key.replace(/^@_/, '').replace(/#.*$/, '');
                this.elementTypes.add(cleanKey);

                // Add processor
                const processorName = `${cleanKey.toLowerCase()}Processor`;
                this.processors.add(processorName);

                // Add test data
                this.testData.add(`test_${cleanKey.toLowerCase()}.xml`);

                // Add test file
                this.tests.add(`${cleanKey.toLowerCase()}.test.js`);

                // Recursively process child objects
                if (typeof pu[key] === 'object') {
                    this.processProgramUnit(pu[key]);
                }
            }
        }
    }

    generateReport() {
        const report = {
            elementTypes: Array.from(this.elementTypes).sort(),
            programUnitTypes: Array.from(this.programUnitTypes).sort(),
            processors: Array.from(this.processors).sort(),
            testData: Array.from(this.testData).sort(),
            tests: Array.from(this.tests).sort()
        };

        return report;
    }
}

async function main() {
    const analyzer = new ProgramUnitAnalyzer();
    const inputsDir = path.join(process.cwd(), 'inputs');

    console.log('Analyzing XML files in:', inputsDir);
    await analyzer.analyzeDirectory(inputsDir);

    const report = analyzer.generateReport();

    console.log('\nAnalysis Report:');
    console.log('\nElement Types Found:');
    report.elementTypes.forEach(type => console.log(`- ${type}`));

    console.log('\nProgram Unit Types Found:');
    report.programUnitTypes.forEach(type => console.log(`- ${type}`));

    console.log('\nRequired Processors:');
    report.processors.forEach(processor => console.log(`- src/processors/elements/${processor}.js`));

    console.log('\nRequired Test Data:');
    report.testData.forEach(testData => console.log(`- test-data/elements/${testData}`));

    console.log('\nRequired Tests:');
    report.tests.forEach(test => console.log(`- tests/elements/${test}`));
}

main().catch(console.error); 