/**
 * tools/standalone/xml-to-markdown/src/processors/elements/coordinateProcessor.js
 * ================================================================================
 * 
 * Purpose:
 *   Processes Coordinate elements. Defines the coordinate system and units
 *   for form layout (character cells, pixels, etc.).
 * 
 * Key Attributes: CharacterCellWidth, CharacterCellHeight, CoordinateSystem
 * 
 * @module CoordinateProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class CoordinateProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Coordinate',
            // Mandatory attributes (from forms.xsd: CharacterCellWidth, RealUnit, DefaultFontScaling, CharacterCellHeight, CoordinateSystem)
            [
                'CharacterCellWidth',
                'RealUnit',
                'DefaultFontScaling',
                'CharacterCellHeight',
                'CoordinateSystem'
            ],
            // Optional attributes (none defined in forms.xsd for Coordinate)
            [],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Coordinate element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--CoordinateProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Coordinate
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--CoordinateProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a Coordinate element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--CoordinateProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const coordinateProcessor = new CoordinateProcessor(process.env.DEBUG === 'true');