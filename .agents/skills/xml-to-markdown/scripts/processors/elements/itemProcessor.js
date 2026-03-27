/**
 * tools/standalone/xml-to-markdown/src/processors/elements/itemProcessor.js
 * ==========================================================================
 * 
 * Purpose:
 *   Processes Oracle Forms Item elements. Items are UI fields (text, checkbox,
 *   button, LOV, etc.) that display and capture data within Blocks.
 * 
 * Input:
 *   - Parsed <Item> XML element with 170+ possible attributes
 * 
 * Output:
 *   - Structured item data with name, type, validation rules
 *   - Markdown section with attribute tables
 * 
 * Key Attributes Extracted:
 *   - Name: Item identifier (BLOCK.ITEM syntax)
 *   - ItemType: TEXT_ITEM, CHECK_BOX, PUSH_BUTTON, LIST_ITEM, etc.
 *   - DataType: VARCHAR2, NUMBER, DATE, etc.
 *   - Required, Enabled, Visible: Validation/display flags
 *   - LovName: Associated List of Values
 *   - FormatMask: Display formatting
 *   - Prompt: Field label
 * 
 * Child Elements:
 *   - Trigger (field-level event handlers)
 *   - ListItemElement (for list items)
 * 
 * Usage:
 *   import { itemProcessor } from './itemProcessor.js';
 *   const result = await itemProcessor.processRootElement(itemElement);
 * 
 * @module ItemProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ItemProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Item',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (all other attributes from forms.xsd)
            [
                'AutoHint',
                'AutoSkip',
                'CaseInsensitiveQuery',
                'ConcealData',
                'DatabaseItem',
                'DefaultButton',
                'DirtyInfo',
                'Enabled',
                'FixedLength',
                'Iconic',
                'InsertAllowed',
                'KeyboardNavigable',
                'KeepCursorPosition',
                'LockRecord',
                'MultiLine',
                'MouseNavigate',
                'OleInPlaceAction',
                'OleInsideOutSupport',
                'OleShowPopupMenu',
                'OleShowTenantTypeType',
                'PrimaryKey',
                'QueryAllowed',
                'QueryOnly',
                'Rendered',
                'Required',
                'ShowFastForward',
                'ShowHorizontalScrollbar',
                'ShowPlay',
                'ShowRecord',
                'ShowRewind',
                'ShowSlider',
                'ShowTime',
                'ShowVerticalScrollbar',
                'ShowVolume',
                'SubclassSubObject',
                'TreeAllowEmpBranch',
                'TreeMultiSelect',
                'TreeShowLines',
                'TreeShowSymbol',
                'UpdateAllowed',
                'UpdateCommit',
                'UpdateIfNull',
                'UpdateQuery',
                'ValidateFromList',
                'Visible',
                'AudioChannels',
                'Bevel',
                'CalculateMode',
                'CaseRestriction',
                'CheckBoxOtherValues',
                'CompressionQuality',
                'CommMode',
                'Compress',
                'CursorStyle',
                'DataType',
                'DataLengthSemantics',
                'DisplayQuality',
                'DistanceBetweenRecords',
                'EditXPosition',
                'EditYPosition',
                'ExecuteMode',
                'FontSize',
                'FontSpacing',
                'FontStyle',
                'FontWeight',
                'Height',
                'ImageDepth',
                'ImageFormat',
                'InitializeKeyboardDirection',
                'ItemType',
                'ItemsDisplay',
                'Justification',
                'KeyboardState',
                'LanguageDirection',
                'LovXPosition',
                'LovYPosition',
                'ListElementCount',
                'ListStyle',
                'MaximumLength',
                'OleActionStyle',
                'OlePopupMenuItems',
                'OleResizStyle',
                'OleTenantTypeAspect',
                'OleTenantTypeType',
                'ParentModuleType',
                'ParentSourceLevel1ObjectType',
                'ParentType',
                'PersistentClientInfoLength',
                'PromptAlign',
                'PromptAlignOffset',
                'PromptAttachmentEdge',
                'PromptAttachmentOffset',
                'PromptDisplayStyle',
                'PromptFontSize',
                'PromptFontSpacing',
                'PromptFontStyle',
                'PromptFontWeight',
                'PromptJustification',
                'PromptReadingOrder',
                'QueryLength',
                'ReadingOrder',
                'RowBandingFreq',
                'SizingStyle',
                'SoundFormat',
                'SoundQuality',
                'SummaryFunction',
                'Width',
                'WrapStyle',
                'XPosition',
                'YPosition',
                'AccessKey',
                'BackColor',
                'CheckedValue',
                'CanvasName',
                'ColumnName',
                'Comment',
                'CopyValueFromItem',
                'DataSourceBlock',
                'DataSourceXAxis',
                'DataSourceYAxis',
                'EditName',
                'FillPattern',
                'Filename',
                'FormatMask',
                'FontName',
                'ForegroundColor',
                'Formula',
                'HelpBookTopic',
                'HighestAllowedValue',
                'Hint',
                'IconFilename',
                'ImplementationClass',
                'InitializeValue',
                'Label',
                'LovName',
                'LowestAllowedValue',
                'NextNavigationItemName',
                'OleClass',
                'OtherValues',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'ParentSourceLevel1ObjectName',
                'PopupMenuName',
                'PreviousNavigationItemName',
                'Prompt',
                'PromptBackColor',
                'PromptFillPattern',
                'PromptFontName',
                'PromptForegroundColor',
                'PromptVisualAttributeName',
                'QueryName',
                'RecordGroupName',
                'RecordVisualAttributeGroupName',
                'SummaryBlockName',
                'SummaryItemName',
                'SynchronizedItemName',
                'TabPageName',
                'Tooltip',
                'TooltipVisualAttributeGroup',
                'TreeDataQuery',
                'UncheckedValue',
                'VisualAttributeName',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Item element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ItemProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Item
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ItemProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Item
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ItemProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const itemProcessor = new ItemProcessor(process.env.DEBUG === 'true');