/**
 * tools/standalone/xml-to-markdown/src/processors/elementTypes.js
 * =================================================================
 * 
 * Purpose:
 *   Central registry mapping XML element types to their processor files.
 *   Provides lazy-loading of processors via dynamic imports.
 * 
 * Input:
 *   - Element type name (e.g., 'Block', 'Trigger', 'MenuItem')
 * 
 * Output:
 *   - Instantiated processor object for the element type
 * 
 * Assumptions:
 *   - Processor files are named {ElementType}Processor.js
 *   - Each processor file exports a class named {ElementType}Processor
 *   - All processors extend BaseProcessor
 * 
 * Registry (42 elements):
 *   - FormModule elements: Block, Item, Trigger, Canvas, Window, etc.
 *   - MenuModule elements: Menu, MenuItem, MenuItemRole, etc.
 *   - ObjectLibrary elements: ObjectLibrary, ObjectLibraryTab, etc.
 * 
 * Key Exports:
 *   - processorPaths: Object mapping element names to file paths
 *   - getProcessor(type): Async function returning processor instance
 *   - elementProcessors: Proxy for lazy-loading processors
 * 
 * Usage:
 *   import { getProcessor, elementProcessors } from './elementTypes.js';
 *   
 *   // Direct lookup
 *   const blockProc = await getProcessor('Block');
 *   
 *   // Via proxy (lazy-load)
 *   const triggerProc = await elementProcessors.Trigger;
 * 
 * Related:
 *   - BaseProcessor.js (parent class for all processors)
 *   - ./elements/*.js (42 element processor implementations)
 * 
 * @module elementTypes
 */

// Map of element names to their processor file paths
const processorPaths = {
    Alert: './elements/AlertProcessor.js',
    AttachedLibrary: './elements/AttachedLibraryProcessor.js',
    Block: './elements/BlockProcessor.js',
    Canvas: './elements/CanvasProcessor.js',
    CompoundText: './elements/CompoundTextProcessor.js',
    Coordinate: './elements/CoordinateProcessor.js',
    DataSourceColumn: './elements/DataSourceColumnProcessor.js',
    DataSourceArgument: './elements/DataSourceArgumentProcessor.js',
    Editor: './elements/EditorProcessor.js',
    Event: './elements/EventProcessor.js',
    Font: './elements/FontProcessor.js',
    FormModule: './elements/FormModuleProcessor.js',
    Graphics: './elements/GraphicsProcessor.js',
    Item: './elements/ItemProcessor.js',
    ListItemElement: './elements/ListItemElementProcessor.js',
    Lov: './elements/LovProcessor.js',
    LovColumnMapping: './elements/LovColumnMappingProcessor.js',
    Menu: './elements/MenuProcessor.js',
    MenuItem: './elements/MenuItemProcessor.js',
    MenuItemRole: './elements/MenuItemRoleProcessor.js',
    MenuModule: './elements/MenuModuleProcessor.js',
    MenuModuleRole: './elements/MenuModuleRoleProcessor.js',
    Module: './elements/ModuleProcessor.js',
    ModuleParameter: './elements/ModuleParameterProcessor.js',
    ObjectGroup: './elements/ObjectGroupProcessor.js',
    ObjectGroupChild: './elements/ObjectGroupChildProcessor.js',
    ObjectLibrary: './elements/ObjectLibraryProcessor.js',
    ObjectLibraryTab: './elements/ObjectLibraryTabProcessor.js',
    Point: './elements/PointProcessor.js',
    ProgramUnit: './elements/ProgramUnitProcessor.js',
    PropertyClass: './elements/PropertyClassProcessor.js',
    RadioButton: './elements/RadioButtonProcessor.js',
    RecordGroup: './elements/RecordGroupProcessor.js',
    RecordGroupColumn: './elements/RecordGroupColumnProcessor.js',
    Relation: './elements/RelationProcessor.js',
    Report: './elements/ReportProcessor.js',
    TabPage: './elements/TabPageProcessor.js',
    TextSegment: './elements/TextSegmentProcessor.js',
    Trigger: './elements/TriggerProcessor.js',
    VisualAttribute: './elements/VisualAttributeProcessor.js',
    VisualState: './elements/VisualStateProcessor.js',
    Window: './elements/WindowProcessor.js'
};

// Cache for loaded processors
const processorCache = new Map();

/**
 * Get a processor for a given element type
 * @param {string} elementType - The type of element to get a processor for
 * @returns {Promise<Function>} - The processor function for the element type
 */
export async function getProcessor(elementType) {
    // Check if processor is already cached
    if (processorCache.has(elementType)) {
        return processorCache.get(elementType);
    }

    // Get the processor path
    const processorPath = processorPaths[elementType];
    if (!processorPath) {
        throw new Error(`No processor found for element type: ${elementType}`);
    }

    try {
        // Dynamically import the processor
        const module = await import(processorPath);

        // Get the processor class name
        const processorClassName = `${elementType}Processor`;
        const ProcessorClass = module[processorClassName];

        if (!ProcessorClass) {
            throw new Error(`Processor class ${processorClassName} not found in ${processorPath}`);
        }

        // Instantiate the processor
        const processor = new ProcessorClass();

        // Cache the processor
        processorCache.set(elementType, processor);
        return processor;
    } catch (error) {
        throw new Error(`Failed to load processor for ${elementType}: ${error.message}`);
    }
}

// Export the processor paths for reference
export { processorPaths };

// Export elementProcessors as a function that uses getProcessor
export const elementProcessors = new Proxy({}, {
    get: async (target, prop) => {
        try {
            return await getProcessor(prop);
        } catch (error) {
            console.warn(`Failed to get processor for type ${prop}:`, error);
            return undefined;
        }
    }
}); 