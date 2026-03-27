/**
 * tools/standalone/xml-to-markdown/src/utils/programUnitAnalyzer.js
 * ===================================================================
 * 
 * Purpose:
 *   Analyzes ProgramUnit elements and hierarchies using ElementHierarchyAnalyzer.
 *   Extracts element types and relationships from XML files.
 * 
 * Exports:
 *   - ProgramUnitAnalyzer: Class with loadXmlFiles(), analyzeProgramUnits()
 * 
 * @module programUnitAnalyzer
 */

import { ElementHierarchyAnalyzer } from './elementHierarchyAnalyzer.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseStringPromise } from 'xml2js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Analyzes ProgramUnit elements and their hierarchies
 */
export class ProgramUnitAnalyzer {
    constructor(config = {}) {
        this.analyzer = new ElementHierarchyAnalyzer(config);
        this.programUnitTypes = new Set();
        this.debug = config.debug || false;
    }

    /**
     * Loads and parses XML files from a directory
     * @param {string} directory - Directory containing XML files
     * @returns {Promise<Array>} Array of parsed XML objects
     */
    async loadXmlFiles(directory) {
        const files = fs.readdirSync(directory)
            .filter(file => file.endsWith('.xml'));

        const xmlObjects = [];

        for (const file of files) {
            const filePath = path.join(directory, file);
            if (this.debug) console.log(`Processing file: ${filePath}`);

            const xmlContent = fs.readFileSync(filePath, 'utf8');
            const result = await parseStringPromise(xmlContent, {
                explicitArray: false,
                preserveChildrenOrder: true,
                explicitChildren: true
            });
            xmlObjects.push(result);
        }

        return xmlObjects;
    }

    /**
     * Extracts element types and their relationships from XML objects
     * @param {Array} xmlObjects - Array of parsed XML objects
     */
    extractElementTypes(xmlObjects) {
        for (const xml of xmlObjects) {
            if (this.debug) console.log('Processing XML object:', JSON.stringify(xml, null, 2));
            this.processElement(xml);
        }
    }

    /**
     * Recursively processes an element and its children
     * @param {Object} element - The element to process
     * @param {string} [parentType] - Parent element type
     */
    processElement(element, parentType) {
        if (!element || typeof element !== 'object') return;

        // Handle both direct elements and those with $$ prefix from xml2js
        const elementType = Object.keys(element).find(key => !key.startsWith('$'));
        if (!elementType) return;

        const elementData = element[elementType];
        if (!elementData) return;

        if (this.debug) {
            console.log(`Processing element type: ${elementType}`);
            console.log(`Parent type: ${parentType}`);
            console.log('Element data:', JSON.stringify(elementData, null, 2));
        }

        // Record parent-child relationship
        if (parentType) {
            const hierarchy = this.analyzer.hierarchyMap.get(elementType) || {
                type: elementType,
                parentTypes: new Set(),
                childTypes: new Set(),
                baseTypes: new Set(),
                isBaseType: false
            };
            hierarchy.parentTypes.add(parentType);
            this.analyzer.hierarchyMap.set(elementType, hierarchy);
        }

        // Process child elements
        const children = elementData.$$;
        if (children) {
            for (const child of children) {
                const childType = Object.keys(child).find(key => !key.startsWith('$'));
                if (childType) {
                    if (this.debug) console.log(`Found child type: ${childType}`);
                    this.processElement({ [childType]: child[childType] }, elementType);
                }
            }
        }

        // Analyze the element
        this.analyzer.analyzeElement(elementType, {
            type: elementType,
            children: children ? children.map(child => {
                const childType = Object.keys(child).find(key => !key.startsWith('$'));
                return { type: childType };
            }) : []
        });
    }

    /**
     * Analyzes ProgramUnit elements from XML files
     * @param {string} directory - Directory containing XML files
     */
    async analyzeProgramUnits(directory) {
        try {
            const xmlObjects = await this.loadXmlFiles(directory);
            this.extractElementTypes(xmlObjects);

            // Find all ProgramUnit-related types
            const hierarchyMap = this.analyzer.getHierarchyMap();
            for (const [type, hierarchy] of hierarchyMap) {
                if (type === 'ProgramUnit' ||
                    hierarchy.ancestors.includes('ProgramUnit') ||
                    hierarchy.descendants.includes('ProgramUnit')) {
                    this.programUnitTypes.add(type);
                }
            }

            // Print analysis results
            console.log('\nProgramUnit Element Analysis');
            console.log('===========================');
            console.log('\nAll ProgramUnit-related types:');
            this.programUnitTypes.forEach(type => {
                this.analyzer.printHierarchy(type);
            });

            console.log('\nBase types in ProgramUnit hierarchy:');
            const baseTypes = this.analyzer.getBaseTypes();
            baseTypes.forEach(type => {
                if (this.programUnitTypes.has(type)) {
                    console.log(`- ${type}`);
                }
            });

        } catch (error) {
            console.error('Error analyzing ProgramUnit elements:', error);
            throw error;
        }
    }
} 