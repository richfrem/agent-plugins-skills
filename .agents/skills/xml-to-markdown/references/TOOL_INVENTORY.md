# xml-to-markdown - Tool Inventory

> **Auto-generated:** 2026-01-24 11:27
> **Regenerate:** `python tools/curate/documentation/generate_tool_inventory_docs.py --tool xml-to-markdown`

---

## 📁 Src

| Script | Description |
| :--- | :--- |
| [`convert-forms-xml-to-markdown.js`](../scripts/src/convert-forms-xml-to-markdown.js) | Converts Oracle Forms XML files (FMB/MMB/OLB) into structured Markdown documentation optimized for LLM analysis. |
| [`convert-pll-to-markdown.js`](../scripts/src/convert-pll-to-markdown.js) | Converts PL/SQL Library (.pll) text dumps into structured Markdown with syntax highlighting and procedure/function headers. |
| [`convert-report-xml-to-markdown.js`](../scripts/src/convert-report-xml-to-markdown.js) | Converts Oracle Reports XML files into structured Markdown documentation optimized for LLM analysis. |

## 🔧 Src / Processors

| Script | Description |
| :--- | :--- |
| [`BaseProcessor.js`](../scripts/src/processors/BaseProcessor.js) | Abstract base class for all Oracle Forms XML element processors. |
| [`elementProcessor.js`](../scripts/src/processors/elementProcessor.js) | Routes XML elements to their corresponding processor classes. |
| [`elementTypes.js`](../scripts/src/processors/elementTypes.js) | Central registry mapping XML element types to their processor files. |

## 📦 Src / Processors / Elements

| Script | Description |
| :--- | :--- |
| [`CompoundTextProcessor.js`](../scripts/src/processors/elements/CompoundTextProcessor.js) | Processes CompoundText elements within Graphics. Contains styled text segments for rich text rendering in boilerplate graphics. |
| [`EditorProcessor.js`](../scripts/src/processors/elements/EditorProcessor.js) | Processes Editor elements. Named text editor configurations for multi-line text editing in items (invoked via Edit menu or programmatically). |
| [`EventProcessor.js`](../scripts/src/processors/elements/EventProcessor.js) | Processes Event elements. JavaBean event handlers for Java components integrated into Oracle Forms. |
| [`FontProcessor.js`](../scripts/src/processors/elements/FontProcessor.js) | Processes Font elements. Font definitions with name, size, weight, and style attributes for text rendering configuration. |
| [`ListItemElementProcessor.js`](../scripts/src/processors/elements/ListItemElementProcessor.js) | Processes ListItemElement within List Items. Individual options in a dropdown list, poplist, or T-list with label and value pairs. |
| [`LovColumnMappingProcessor.js`](../scripts/src/processors/elements/LovColumnMappingProcessor.js) | Processes LovColumnMapping elements. Maps LOV columns to form items, defining which LOV values populate which form fields on selection. |
| [`LovProcessor.js`](../scripts/src/processors/elements/LovProcessor.js) | Processes Oracle Forms LOV (List of Values) elements. LOVs provide popup selection dialogs for field validation and data entry. |
| [`ModuleProcessor.js`](../scripts/src/processors/elements/ModuleProcessor.js) | Generic Module processor for module-level elements. Used as fallback when a specific processor is not available. |
| [`ObjectGroupChildProcessor.js`](../scripts/src/processors/elements/ObjectGroupChildProcessor.js) | Processes ObjectGroupChild elements. References to objects included in a group, enabling inheritance of properties from ObjectLibrary templates. |
| [`ObjectLibraryTabProcessor.js`](../scripts/src/processors/elements/ObjectLibraryTabProcessor.js) | Processes ObjectLibraryTab elements. Tabs organize objects within an ObjectLibrary for easier navigation in the Forms Builder IDE. |
| [`PointProcessor.js`](../scripts/src/processors/elements/PointProcessor.js) | Processes Point elements. Individual vertices within polyline or polygon graphics, defining shape paths via XPosition/YPosition. |
| [`RecordGroupColumnProcessor.js`](../scripts/src/processors/elements/RecordGroupColumnProcessor.js) | Processes RecordGroupColumn elements. Defines columns within a RecordGroup including name, data type, and width for query result storage. |
| [`TextItemProcessor.js`](../scripts/src/processors/elements/TextItemProcessor.js) | Processes TextItem elements. Extended item processing for text-based input fields with specific text handling properties. |
| [`TextSegmentProcessor.js`](../scripts/src/processors/elements/TextSegmentProcessor.js) | Processes TextSegment elements. Individual text runs with specific formatting within a CompoundText container. |
| [`VisualStateProcessor.js`](../scripts/src/processors/elements/VisualStateProcessor.js) | Processes VisualState elements. Named visual states for TreeItem nodes defining appearance based on node state. |
| [`alertProcessor.js`](../scripts/src/processors/elements/alertProcessor.js) | Processes Oracle Forms Alert elements. Alerts are modal message dialogs used for user notifications, confirmations, and error messages. |
| [`attachedLibraryProcessor.js`](../scripts/src/processors/elements/attachedLibraryProcessor.js) | Processes Oracle Forms AttachedLibrary elements. AttachedLibrary references |
| [`blockProcessor.js`](../scripts/src/processors/elements/blockProcessor.js) | Processes Oracle Forms Block elements. Blocks are data containers that hold Items (fields) and manage database operations (query, insert, update, delete). |
| [`canvasProcessor.js`](../scripts/src/processors/elements/canvasProcessor.js) | Processes Oracle Forms Canvas elements. Canvases are visual containers that hold Items and define the layout of form screens. |
| [`coordinateProcessor.js`](../scripts/src/processors/elements/coordinateProcessor.js) | Processes Coordinate elements. Defines the coordinate system and units for form layout (character cells, pixels, etc.). |
| [`dataSourceArgumentProcessor.js`](../scripts/src/processors/elements/dataSourceArgumentProcessor.js) | Processes DataSourceArgument elements. Defines parameters for stored procedure data sources used in blocks. |
| [`dataSourceColumnProcessor.js`](../scripts/src/processors/elements/dataSourceColumnProcessor.js) | Processes DataSourceColumn elements. Defines column bindings between database columns and block items for query/DML operations. |
| [`formModuleProcessor.js`](../scripts/src/processors/elements/formModuleProcessor.js) | Processes Oracle Forms FormModule elements. FormModule is the root container for an Oracle Form, holding all Blocks, Canvases, Windows, and Triggers. |
| [`graphicsProcessor.js`](../scripts/src/processors/elements/graphicsProcessor.js) | Processes Oracle Forms Graphics elements. Graphics define visual decorations including lines, rectangles, images, and text labels on canvases. |
| [`itemProcessor.js`](../scripts/src/processors/elements/itemProcessor.js) | Processes Oracle Forms Item elements. Items are UI fields (text, checkbox, button, LOV, etc.) that display and capture data within Blocks. |
| [`menuItemProcessor.js`](../scripts/src/processors/elements/menuItemProcessor.js) | Processes Oracle Forms MenuItem elements. MenuItems are individual commands or actions in the menu bar (e.g., File > Save, Edit > Copy). |
| [`menuItemRoleProcessor.js`](../scripts/src/processors/elements/menuItemRoleProcessor.js) | Processes MenuItemRole elements. Defines which roles can access a MenuItem. |
| [`menuModuleProcessor.js`](../scripts/src/processors/elements/menuModuleProcessor.js) | Processes Oracle Forms MenuModule elements. MenuModule is the root container for an Oracle Menu (.mmb), defining the application's menu bar and actions. |
| [`menuModuleRoleProcessor.js`](../scripts/src/processors/elements/menuModuleRoleProcessor.js) | Processes MenuModuleRole elements. Defines module-level role assignments for the entire menu, used when UseSecurity=true. |
| [`menuProcessor.js`](../scripts/src/processors/elements/menuProcessor.js) | Processes Oracle Forms Menu elements. Menus are containers for MenuItems within a MenuModule, defining pulldown menu structure. |
| [`moduleParameterProcessor.js`](../scripts/src/processors/elements/moduleParameterProcessor.js) | Processes ModuleParameter elements. Parameters passed to forms via CALL_FORM or OPEN_FORM, enabling inter-form communication. |
| [`objectGroupProcessor.js`](../scripts/src/processors/elements/objectGroupProcessor.js) | Processes ObjectGroup elements in ObjectLibraries. Groups logically related objects for subclassing (e.g., all items in a reusable block template). |
| [`objectLibraryProcessor.js`](../scripts/src/processors/elements/objectLibraryProcessor.js) | Processes Oracle Forms ObjectLibrary elements. ObjectLibrary is the root container for .olb files that hold reusable UI components and templates. |
| [`programUnitProcessor.js`](../scripts/src/processors/elements/programUnitProcessor.js) | Processes Oracle Forms ProgramUnit elements. ProgramUnits contain PL/SQL packages, procedures, and functions defined within the form. |
| [`propertyClassProcessor.js`](../scripts/src/processors/elements/propertyClassProcessor.js) | Processes PropertyClass elements. Named property collections that can be inherited by multiple objects, enabling consistent styling and behavior across forms. |
| [`radioButtonProcessor.js`](../scripts/src/processors/elements/radioButtonProcessor.js) | Processes RadioButton elements. Individual radio options within a RadioGroup item, typically for mutually exclusive choices. |
| [`recordGroupProcessor.js`](../scripts/src/processors/elements/recordGroupProcessor.js) | Processes Oracle Forms RecordGroup elements. RecordGroups are data structures that hold query results or static data for LOVs and programmatic use. |
| [`relationProcessor.js`](../scripts/src/processors/elements/relationProcessor.js) | Processes Oracle Forms Relation elements. Relations define master-detail relationships between blocks for coordinated data navigation. |
| [`reportProcessor.js`](../scripts/src/processors/elements/reportProcessor.js) | Processes Report elements. References to Oracle Reports that can be invoked from the form via RUN_REPORT_OBJECT. |
| [`tabPageProcessor.js`](../scripts/src/processors/elements/tabPageProcessor.js) | Processes TabPage elements within Tab Canvases. Each page represents a switchable view in tabbed interfaces. |
| [`triggerProcessor.js`](../scripts/src/processors/elements/triggerProcessor.js) | Processes Oracle Forms Trigger elements. Triggers contain PL/SQL code that executes in response to events (WHEN-BUTTON-PRESSED, PRE-QUERY, etc.). |
| [`visualAttributeProcessor.js`](../scripts/src/processors/elements/visualAttributeProcessor.js) | Processes VisualAttribute elements. Named style definitions (fonts, colors) that can be applied to items, blocks, and canvases for consistent appearance. |
| [`windowProcessor.js`](../scripts/src/processors/elements/windowProcessor.js) | Processes Oracle Forms Window elements. Windows are the top-level visual containers that hold Canvases and define form window behavior. |

## 🔨 Src / Tools

| Script | Description |
| :--- | :--- |
| [`checkProcessorConsistency.js`](../scripts/src/tools/checkProcessorConsistency.js) | Quality assurance tool that scans all element processors for consistency with the "evolved approach" patterns (documentation, implementation). |
| [`moduleTypeDetector.js`](../scripts/src/tools/moduleTypeDetector.js) | TBD |

## 🛠️ Src / Utils

| Script | Description |
| :--- | :--- |
| [`analyzeProgramUnits.js`](../scripts/src/utils/analyzeProgramUnits.js) | Standalone script to analyze ProgramUnit elements from Oracle Forms XML. |
| [`attributeUtils.js`](../scripts/src/utils/attributeUtils.js) | XML attribute extraction and normalization utilities. Handles multiple parser formats and provides case-insensitive attribute access. |
| [`codeUtils.js`](../scripts/src/utils/codeUtils.js) | PL/SQL and SQL code formatting utilities. Handles entity decoding, whitespace normalization, and syntax-aware indentation. |
| [`elementHierarchyAnalyzer.js`](../scripts/src/utils/elementHierarchyAnalyzer.js) | Analyzes element hierarchies in Oracle Forms XML. Builds relationship maps showing parent-child-ancestor-descendant chains between elements. |
| [`logger.js`](../scripts/src/utils/logger.js) | Logging utilities with environment-aware configuration. Provides test-mode logging that captures messages for verification. |
| [`outputUtils.js`](../scripts/src/utils/outputUtils.js) | Output utilities for markdown generation. Creates structured output objects that handle both test and production modes for flexible testing. |
| [`processorChecker.js`](../scripts/src/utils/processorChecker.js) | Utility to audit processor coverage. Scans XML files for element types and compares against available processors to identify gaps. |
| [`programUnitAnalyzer.js`](../scripts/src/utils/programUnitAnalyzer.js) | Analyzes ProgramUnit elements and hierarchies using ElementHierarchyAnalyzer. |
| [`reorganizeTestData.js`](../scripts/src/utils/reorganizeTestData.js) | Reorganizes test data XML files into element-type subdirectories. |
| [`scanWindowAttributes.js`](../scripts/src/utils/scanWindowAttributes.js) | Utility script to scan XML files for Window element attributes. |
| [`scanWindowElements.js`](../scripts/src/utils/scanWindowElements.js) | Scans XML files for Window elements and generates analysis reports. |
| [`testUtils.js`](../scripts/src/utils/testUtils.js) | Testing utilities for processor validation. Provides helpers for loading test XML data and running element processor tests. |
| [`xmlUtils.js`](../scripts/src/utils/xmlUtils.js) | XML parsing utilities for Oracle Forms XML files. Configures xml2js parser with optimal settings for processing FMB/MMB/OLB exported XML. |

## 📁 Src / Utils / Migration

| Script | Description |
| :--- | :--- |
| [`updateUtilsReferences.js`](../scripts/src/utils/migration/updateUtilsReferences.js) | Updates import paths across the codebase when utility modules are moved to new locations. This handles refactoring of import statements. |

## 📁 Tests

| Script | Description |
| :--- | :--- |
| [`run-element-tests.js`](../scripts/tests/run-element-tests.js) | TBD |

## 🛠️ Tests / Utils

| Script | Description |
| :--- | :--- |
| [`runElementTests.js`](../scripts/tests/utils/runElementTests.js) | TBD |
| [`testUtils.js`](../scripts/tests/utils/testUtils.js) | TBD |
| [`testXmlParser.js`](../scripts/tests/utils/testXmlParser.js) | TBD |
| [`updateTestFiles.js`](../scripts/tests/utils/updateTestFiles.js) | TBD |
