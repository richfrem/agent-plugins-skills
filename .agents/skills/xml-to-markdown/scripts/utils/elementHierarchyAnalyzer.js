/**
 * tools/standalone/xml-to-markdown/src/utils/elementHierarchyAnalyzer.js
 * =======================================================================
 * 
 * Purpose:
 *   Analyzes element hierarchies in Oracle Forms XML. Builds relationship
 *   maps showing parent-child-ancestor-descendant chains between elements.
 * 
 * Exports:
 *   - ElementHierarchyAnalyzer: Class with analyzeElement(), buildHierarchy()
 * 
 * @module elementHierarchyAnalyzer
 */

/**
 * Utility class for analyzing element hierarchies in Oracle Forms XML
 * This analyzer recursively examines element types and their relationships
 * to build a complete hierarchy map.
 */
export class ElementHierarchyAnalyzer {
    /**
     * @param {Object} config - Configuration object
     * @param {boolean} [config.debug=false] - Enable debug logging
     */
    constructor(config = {}) {
        this.debug = config.debug || false;
        this.hierarchyMap = new Map();
        this.baseTypes = new Set();
        this.processedTypes = new Set();
    }

    /**
     * Analyzes an element type and its hierarchy
     * @param {string} elementType - The element type to analyze
     * @param {Object} elementData - The element data containing child elements
     * @returns {Object} The hierarchy analysis results
     */
    analyzeElement(elementType, elementData) {
        if (this.processedTypes.has(elementType)) {
            return this.hierarchyMap.get(elementType);
        }

        this.processedTypes.add(elementType);
        const hierarchy = {
            type: elementType,
            parentTypes: new Set(),
            childTypes: new Set(),
            baseTypes: new Set(),
            isBaseType: false
        };

        // Analyze child elements
        if (elementData && elementData.children) {
            for (const child of elementData.children) {
                const childType = child.type;
                hierarchy.childTypes.add(childType);

                // Recursively analyze child types
                const childHierarchy = this.analyzeElement(childType, child);

                // Add child's base types to this element's base types
                childHierarchy.baseTypes.forEach(baseType => {
                    hierarchy.baseTypes.add(baseType);
                });
            }
        }

        // If no child types, this is a base type
        if (hierarchy.childTypes.size === 0) {
            hierarchy.isBaseType = true;
            hierarchy.baseTypes.add(elementType);
            this.baseTypes.add(elementType);
        }

        this.hierarchyMap.set(elementType, hierarchy);
        return hierarchy;
    }

    /**
     * Builds the complete hierarchy for a given element type
     * @param {string} elementType - The element type to build hierarchy for
     * @returns {Object} The complete hierarchy
     */
    buildHierarchy(elementType) {
        const hierarchy = this.hierarchyMap.get(elementType);
        if (!hierarchy) {
            throw new Error(`Element type ${elementType} not found in hierarchy map`);
        }

        const completeHierarchy = {
            type: hierarchy.type,
            baseTypes: Array.from(hierarchy.baseTypes),
            childTypes: Array.from(hierarchy.childTypes),
            isBaseType: hierarchy.isBaseType,
            ancestors: this.findAncestors(elementType),
            descendants: this.findDescendants(elementType)
        };

        return completeHierarchy;
    }

    /**
     * Finds all ancestor types for a given element type
     * @param {string} elementType - The element type to find ancestors for
     * @returns {string[]} Array of ancestor types
     */
    findAncestors(elementType) {
        const ancestors = new Set();
        const queue = [elementType];

        while (queue.length > 0) {
            const currentType = queue.shift();
            const hierarchy = this.hierarchyMap.get(currentType);

            if (hierarchy) {
                for (const childType of hierarchy.childTypes) {
                    if (!ancestors.has(childType)) {
                        ancestors.add(childType);
                        queue.push(childType);
                    }
                }
            }
        }

        return Array.from(ancestors);
    }

    /**
     * Finds all descendant types for a given element type
     * @param {string} elementType - The element type to find descendants for
     * @returns {string[]} Array of descendant types
     */
    findDescendants(elementType) {
        const descendants = new Set();
        const queue = [elementType];

        while (queue.length > 0) {
            const currentType = queue.shift();
            const hierarchy = this.hierarchyMap.get(currentType);

            if (hierarchy) {
                for (const parentType of hierarchy.parentTypes) {
                    if (!descendants.has(parentType)) {
                        descendants.add(parentType);
                        queue.push(parentType);
                    }
                }
            }
        }

        return Array.from(descendants);
    }

    /**
     * Gets all base types in the hierarchy
     * @returns {string[]} Array of base types
     */
    getBaseTypes() {
        return Array.from(this.baseTypes);
    }

    /**
     * Gets the complete hierarchy map
     * @returns {Map} The hierarchy map
     */
    getHierarchyMap() {
        return this.hierarchyMap;
    }

    /**
     * Prints the hierarchy analysis results
     * @param {string} elementType - The element type to print hierarchy for
     */
    printHierarchy(elementType) {
        const hierarchy = this.buildHierarchy(elementType);

        console.log(`\nHierarchy Analysis for ${elementType}:`);
        console.log('----------------------------------------');
        console.log(`Type: ${hierarchy.type}`);
        console.log(`Is Base Type: ${hierarchy.isBaseType}`);
        console.log('\nBase Types:');
        hierarchy.baseTypes.forEach(type => console.log(`  - ${type}`));
        console.log('\nChild Types:');
        hierarchy.childTypes.forEach(type => console.log(`  - ${type}`));
        console.log('\nAncestors:');
        hierarchy.ancestors.forEach(type => console.log(`  - ${type}`));
        console.log('\nDescendants:');
        hierarchy.descendants.forEach(type => console.log(`  - ${type}`));
    }
} 