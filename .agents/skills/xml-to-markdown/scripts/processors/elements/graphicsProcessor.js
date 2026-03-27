/**
 * tools/standalone/xml-to-markdown/src/processors/elements/graphicsProcessor.js
 * ==============================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Graphics elements. Graphics define visual decorations
 *   including lines, rectangles, images, and text labels on canvases.
 * 
 * Input:
 *   - Parsed <Graphics> XML element with 100+ possible attributes
 * 
 * Output:
 *   - Structured graphics data with dimensions and styling
 *   - Markdown section with graphic properties
 * 
 * Key Attributes Extracted:
 *   - Name: Graphics identifier
 *   - GraphicsType: TEXT, LINE, RECTANGLE, ARC, IMAGE, FRAME, etc.
 *   - Width, Height, XPosition, YPosition: Geometry
 *   - GraphicsText: Text content for labels
 *   - ImageFilename: Path for image graphics
 * 
 * Child Elements:
 *   - Point (for polylines)
 *   - CompoundText, TextSegment (for styled text)
 * 
 * @module GraphicsProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class GraphicsProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Graphics',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (all other attributes from forms.xsd)
            [
                'AllowExpansion',
                'AllowMultiLinePrompts',
                'AllowStartAttachmentPrompts',
                'AllowTopAttachmentPrompts',
                'BoundingBoxScalable',
                'Closed',
                'DirtyInfo',
                'Dither',
                'FixedBoundingBox',
                'FontScaleable',
                'ShowScrollbar',
                'Shrinkwrap',
                'SubclassSubObject',
                'VerticalFill',
                'WrapText',
                'ArrowStyle',
                'Bevel',
                'CapStyle',
                'ClipHeight',
                'ClipWidth',
                'ClipXPosition',
                'ClipYPosition',
                'CornerRadiusX',
                'CornerRadiusY',
                'CustomSpacing',
                'DashStyle',
                'DisplayQuality',
                'DistanceBetweenRecords',
                'FrameAlign',
                'FrameTitleAlign',
                'FrameTitleFontSize',
                'FrameTitleFontSpacing',
                'FrameTitleFontStyle',
                'FrameTitleFontWeight',
                'FrameTitleOffset',
                'FrameTitleSpacing',
                'GraphicsFontColorCode',
                'GraphicsFontSize',
                'GraphicsFontSpacing',
                'GraphicsFontStyle',
                'GraphicsFontWeight',
                'GraphicsType',
                'Height',
                'HorizontalJustification',
                'HorizontalMargin',
                'HorizontalObjectOffset',
                'HorizontalOrigin',
                'ImageDepth',
                'ImageFormat',
                'InternalEndAngle',
                'InternalLineWidth',
                'InternalRotationAngle',
                'InternalStartAngle',
                'JoinStyle',
                'LanguageDirection',
                'LayoutStyle',
                'LineSpacing',
                'MaximumObjs',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'RecordsDisplayCount',
                'ScrollbarAlign',
                'ScrollbarWidth',
                'SingleObjectAlign',
                'StartPromptAlign',
                'StartPromptOffset',
                'TopPromptAlign',
                'TopPromptOffset',
                'TitleReadingOrder',
                'UpdateLayout',
                'VerticalJustification',
                'VerticalMargin',
                'VerticalObjectOffset',
                'VerticalOrigin',
                'Width',
                'XPosition',
                'YPosition',
                'BackColor',
                'EdgeBackColor',
                'EdgeForegroundColor',
                'EdgePattern',
                'FillPattern',
                'ForegroundColor',
                'FrameTitle',
                'FrameTitleBackColor',
                'FrameTitleFillPattern',
                'FrameTitleFontName',
                'FrameTitleForegroundColor',
                'FrameTitleVisualAttributeName',
                'GraphicsFontColor',
                'GraphicsFontName',
                'GraphicsText',
                'LayoutDataBlockName',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'TabPageName',
                'VisualAttributeName',
                'ImageFilename',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Graphics element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--GraphicsProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Graphics
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--GraphicsProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing a Graphics element
     * @param {Object} element - The processed element data
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--GraphicsProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const graphicsProcessor = new GraphicsProcessor(process.env.DEBUG === 'true');