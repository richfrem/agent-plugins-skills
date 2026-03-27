/**
 * tools/standalone/xml-to-markdown/src/processors/elements/TextItemProcessor.js
 * ==============================================================================
 * 
 * Purpose:
 *   Processes TextItem elements. Extended item processing for text-based
 *   input fields with specific text handling properties.
 * 
 * Key Attributes: Name, DataType, MaximumLength, Required, Enabled, Visible
 * Child: Trigger
 * 
 * @module TextItemProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class TextItemProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('TextItem',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (all other attributes from forms.xsd for Item)
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
     * Process the root Textitem element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--TextItemProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Textitem
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--TextItemProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Textitem
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--TextItemProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const textItemProcessor = new TextItemProcessor(process.env.DEBUG === 'true');