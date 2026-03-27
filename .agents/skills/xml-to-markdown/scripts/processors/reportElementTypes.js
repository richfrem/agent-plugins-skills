/**
 * tools/standalone/xml-to-markdown/src/processors/reportElementTypes.js
 * ======================================================================
 * 
 * Purpose:
 *   Central registry mapping Report XML element names to their processor files.
 *   Provides lazy-loading of processors via dynamic imports.
 * 
 * Coverage:
 *   Mapped to 78 unique element types discovered in report schema.
 *   Each element has a dedicated processor file (extending base classes).
 * 
 * Usage:
 *   import { getReportProcessor } from './reportElementTypes.js';
 *   const proc = await getReportProcessor('userParameter');
 * 
 * @module reportElementTypes
 */

// Map of element name -> processor file relative path
// 1:1 Mapping to dedicated files
const processorPaths = {
    // === ROOT ===
    report: './report-elements/ReportModuleProcessor.js', // Manual naming

    // === DATA MODEL ===
    data: './report-elements/DataProcessor.js',
    dataSource: './report-elements/DataSourceProcessor.js',
    select: './report-elements/SelectProcessor.js',
    plsqlStatement: './report-elements/PlsqlStatementProcessor.js',
    group: './report-elements/GroupProcessor.js',
    filter: './report-elements/FilterProcessor.js',

    // === PARAMETERS ===
    parameterForm: './report-elements/ParameterFormProcessor.js',
    userParameter: './report-elements/UserParameterProcessor.js',
    systemParameter: './report-elements/SystemParameterProcessor.js',
    listOfValues: './report-elements/ListOfValuesProcessor.js',
    staticValues: './report-elements/StaticValuesProcessor.js',
    validValue: './report-elements/ValidValueProcessor.js',
    selectStatement: './report-elements/SelectStatementProcessor.js',

    // === COLUMNS / ITEMS ===
    dataItem: './report-elements/DataItemProcessor.js',
    dataDescriptor: './report-elements/DataDescriptorProcessor.js',
    formula: './report-elements/FormulaProcessor.js',
    summary: './report-elements/SummaryProcessor.js',
    placeholder: './report-elements/PlaceholderProcessor.js',
    link: './report-elements/LinkProcessor.js',

    // === LOGIC ===
    programUnits: './report-elements/ProgramUnitsProcessor.js',
    function: './report-elements/FunctionProcessor.js',

    // === STRUCTURE / LAYOUT ===
    layout: './report-elements/LayoutProcessor.js',
    section: './report-elements/SectionProcessor.js',
    body: './report-elements/BodyProcessor.js',
    margin: './report-elements/MarginProcessor.js',
    repeatingFrame: './report-elements/RepeatingFrameProcessor.js',
    frame: './report-elements/FrameProcessor.js',
    matrix: './report-elements/MatrixProcessor.js',
    crossProduct: './report-elements/CrossProductProcessor.js',
    dimension: './report-elements/DimensionProcessor.js',

    // === GRAPHICS ===
    line: './report-elements/LineProcessor.js',
    rectangle: './report-elements/RectangleProcessor.js',
    arc: './report-elements/ArcProcessor.js',
    image: './report-elements/ImageProcessor.js',
    polyline: './report-elements/PolylineProcessor.js',
    roundedRectangle: './report-elements/RoundedRectangleProcessor.js',

    // === TEXT ===
    field: './report-elements/FieldProcessor.js',
    text: './report-elements/TextProcessor.js',
    textSegment: './report-elements/TextSegmentProcessor.js',
    string: './report-elements/StringProcessor.js',
    font: './report-elements/FontProcessor.js',

    // === GEOMETRY / SETTINGS ===
    geometryInfo: './report-elements/GeometryInfoProcessor.js',
    point: './report-elements/PointProcessor.js',
    points: './report-elements/PointsProcessor.js',
    location: './report-elements/LocationProcessor.js',

    visualSettings: './report-elements/VisualSettingsProcessor.js',
    textSettings: './report-elements/TextSettingsProcessor.js',
    webSettings: './report-elements/WebSettingsProcessor.js',
    xmlSettings: './report-elements/XmlSettingsProcessor.js',
    reportWebSettings: './report-elements/ReportWebSettingsProcessor.js',

    advancedLayout: './report-elements/AdvancedLayoutProcessor.js',
    generalLayout: './report-elements/GeneralLayoutProcessor.js',
    pageNumbering: './report-elements/PageNumberingProcessor.js',
    layoutPrivate: './report-elements/LayoutPrivateProcessor.js',
    reportPrivate: './report-elements/ReportPrivateProcessor.js',

    // === METADATA / MISC ===
    comment: './report-elements/CommentProcessor.js',
    displayInfo: './report-elements/DisplayInfoProcessor.js',
    textSource: './report-elements/TextSourceProcessor.js',
    webSource: './report-elements/WebSourceProcessor.js',

    // HTML Escapes
    reportHtmlEscapes: './report-elements/ReportHtmlEscapesProcessor.js',
    beforeReportHtmlEscape: './report-elements/BeforeReportHtmlEscapeProcessor.js',
    beforePageHtmlEscape: './report-elements/BeforePageHtmlEscapeProcessor.js',
    afterPageHtmlEscape: './report-elements/AfterPageHtmlEscapeProcessor.js',
    beforeFormHtmlEscape: './report-elements/BeforeFormHtmlEscapeProcessor.js',
    pageNavigationHtmlEscape: './report-elements/PageNavigationHtmlEscapeProcessor.js',

    // Other
    attachedLibrary: './report-elements/AttachedLibraryProcessor.js',
    characterMode: './report-elements/CharacterModeProcessor.js',
    colorPalette: './report-elements/ColorPaletteProcessor.js',
    color: './report-elements/ColorProcessor.js',
    binaryData: './report-elements/BinaryDataProcessor.js',
    cond: './report-elements/CondProcessor.js',
    formatException: './report-elements/FormatExceptionProcessor.js',
    conditionalFormat: './report-elements/ConditionalFormatProcessor.js',
    formatVisualSettings: './report-elements/FormatVisualSettingsProcessor.js',
    rulers: './report-elements/RulersProcessor.js',
    dataItemPrivate: './report-elements/DataItemPrivateProcessor.js',
    anchor: './report-elements/AnchorProcessor.js'
};

// Cache for loaded processors
const processorCache = new Map();

/**
 * Get a processor for a given element type
 * @param {string} elementName - The XML element name
 * @returns {Promise<Object>} - The processor instance
 */
export async function getReportProcessor(elementName) {
    if (processorCache.has(elementName)) {
        return processorCache.get(elementName);
    }

    const processorPath = processorPaths[elementName];

    if (!processorPath) {
        // Fallback to Generic?
        // In strict mode we might want to know about unmapped elements.
        // But we believe we mapped all 78.
        console.warn(`No processor mapped for element: ${elementName}`);
        return null;
    }

    try {
        const module = await import(processorPath);

        let ProcessorClass = null;
        for (const exportName of Object.keys(module)) {
            if (exportName.endsWith('Processor')) {
                ProcessorClass = module[exportName];
                break;
            }
        }

        if (!ProcessorClass) {
            throw new Error(`No Processor class found in ${processorPath}`);
        }

        const processor = new ProcessorClass(elementName);
        processorCache.set(elementName, processor);
        return processor;

    } catch (error) {
        console.warn(`Failed to load processor for ${elementName} (${processorPath}): ${error.message}`);
        return null;
    }
}
