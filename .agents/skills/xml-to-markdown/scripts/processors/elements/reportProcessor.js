/**
 * tools/standalone/xml-to-markdown/src/processors/elements/reportProcessor.js
 * ============================================================================
 * 
 * Purpose:
 *   Processes Report elements. References to Oracle Reports that can be invoked
 *   from the form via RUN_REPORT_OBJECT.
 * 
 * Key Attributes: Name, Filename, ReportDestinationType, ReportServer
 * 
 * @module ReportProcessor
 * @extends BaseProcessor
 */

import { BaseProcessor } from '../BaseProcessor.js';

export class ReportProcessor extends BaseProcessor {
    constructor(debug = false) {
        super('Report',
            // Mandatory attributes (from forms.xsd: Name)
            ['Name'],
            // Optional attributes (from forms.xsd)
            [
                'DirtyInfo',
                'ReportFtpSecured',
                'SubclassObjectGroup',
                'CommMode',
                'ExecuteMode',
                'ParentModuleType',
                'ParentType',
                'PersistentClientInfoLength',
                'ReportDeleteType',
                'ReportDestinationType',
                'ReportObjectType',
                'ReportPrintNumberofcopy',
                'ReportPrintOrientation',
                'ReportPrintSide',
                'ReportPrintTray',
                'ReportSslConn',
                'ReportWebdavAuthtype',
                'Comment',
                'DataSourceBlock',
                'Filename',
                'ParentFilename',
                'ParentFilepath',
                'ParentModule',
                'ParentName',
                'QueryName',
                'ReportAbsPath',
                'ReportBipParameters',
                'ReportDestinationFormat',
                'ReportDestinationName',
                'ReportFaxNumber',
                'ReportFaxServer',
                'ReportFtpFilename',
                'ReportFtpServer',
                'ReportFtpUser',
                'ReportLocalFilename',
                'ReportLocale',
                'ReportMailBcc',
                'ReportMailBody',
                'ReportMailCc',
                'ReportMailFrom',
                'ReportMailReplyto',
                'ReportMailServer',
                'ReportMailSubject',
                'ReportMailTo',
                'ReportOptionFormat',
                'ReportParameters',
                'ReportPrintName',
                'ReportPrintPagerange',
                'ReportSrvcLocation',
                'ReportServer',
                'ReportTemplateName',
                'ReportWebdavFile',
                'ReportWebdavServer',
                'ReportWebdavUser',
                'SmartClass'
            ],
            {
                defaultCodeType: 'PLSQL'
            }
        );
        this.debug = debug;
    }

    /**
     * Process the root Report element
     * @param {Object} element - The XML element to process
     * @returns {Object} The processed element data
     */
    async processRootElement(element) {
        if (this.debug) console.log('--ReportProcessor processRootElement called');
        return super.processRootElement(element);
    }

    /**
     * Process child elements of the Report
     * @param {Object} element - The parent element
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async processChildren(element, log, output) {
        if (this.debug) console.log('--ReportProcessor processChildren called');
        return super.processChildren(element, log, output);
    }

    /**
     * Format the results of processing the Report
     * @param {Object} element - The element to format
     * @param {Function} log - Logger function
     * @param {Array} output - Output array
     */
    async formatResults(element, log, output) {
        if (this.debug) console.log('--ReportProcessor formatResults called');
        return super.formatResults(element, log, output);
    }
}

// Create and export a singleton instance
export const reportProcessor = new ReportProcessor(process.env.DEBUG === 'true');