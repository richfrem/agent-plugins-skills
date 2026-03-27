/**
 * tools/standalone/xml-to-markdown/src/utils/reorganizeTestData.js
 * ==================================================================
 * 
 * Purpose:
 *   Reorganizes test data XML files into element-type subdirectories.
 *   Extracts main elements and moves files to appropriate directories.
 * 
 * Usage:
 *   node src/utils/reorganizeTestData.js
 * 
 * @module reorganizeTestData
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const TEST_DATA_DIR = path.join(__dirname, '../../test-data');

// Map of element types to their directories (all lowercase)
const ELEMENT_DIRECTORIES = {
    'alert': 'alerts',
    'block': 'blocks',
    'canvas': 'canvases',
    'coordinate': 'coordinates',
    'item': 'items',
    'lov': 'lovs',
    'menu': 'menus',
    'programunit': 'programunits',
    'property': 'properties',
    'recordgroup': 'recordgroups',
    'trigger': 'triggers',
    'window': 'windows',
    'visualattribute': 'visualattributes',
    'objectlibrary': 'objectlibraries',
    'formmodule': 'formmodules',
    'report': 'reports',
    'datasource': 'datasources',
    'graphic': 'graphics',
    'objectgroup': 'objectgroups',
    'moduleparameter': 'moduleparameters',
    'propertyclass': 'propertyclasses',
    'tabpage': 'tabpages',
    'radiobutton': 'radiobuttons',
    'checkbox': 'checkboxes',
    'radiogroup': 'radiogroups',
    'joincondition': 'joinconditions',
    'relation': 'relations',
    'detailblock': 'detailblocks',
    'masterblock': 'masterblocks',
    'lovvisualattribute': 'lovvisualattributes',
    'lovmap': 'lovmaps',
    'lovcolumn': 'lovcolumns',
    'lovcolumnmap': 'lovcolumnmaps',
    'lovcolumnproperty': 'lovcolumnproperties',
    'lovcolumntrigger': 'lovcolumntriggers',
    'lovcolumnwindow': 'lovcolumnwindows',
    'lovcolumnvisualattribute': 'lovcolumnvisualattributes',
    'lovproperty': 'lovproperties',
    'lovquery': 'lovqueries',
    'lovrecordgroup': 'lovrecordgroups',
    'lovwindow': 'lovwindows',
    'menuitemrole': 'menuitemroles',
    'menuitemcode': 'menuitemcodes',
    'menumodule': 'menumodules',
    'menumoduletype': 'menumoduletypes',
    'menumodulename': 'menumodulenames',
    'attachedlibrary': 'attachedlibraries'
};

/**
 * Extracts the main element and its content from an XML file
 * @param {string} content - The XML content
 * @returns {Object|null} - Object containing element type and content, or null if not found
 */
function extractMainElement(content) {
    // Find the first element after FormModule that's not just whitespace
    const match = content.match(/<FormModule[^>]*>[\s\S]*?<([A-Za-z]+)([^>]*(?:\/?>[\s\S]*?<\/\1>|\/>))/);
    if (match) {
        const elementType = match[1];
        const elementContent = match[2];
        // Reconstruct the full element
        const fullElement = `<${elementType}${elementContent}`;
        return {
            type: elementType.toLowerCase(),
            content: fullElement
        };
    }
    return null;
}

/**
 * Creates a directory if it doesn't exist
 * @param {string} dirPath - The directory path to create
 */
function ensureDirectoryExists(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

/**
 * Processes a single XML file
 * @param {string} filePath - Path to the XML file
 */
function processFile(filePath) {
    // Skip if it's in a subdirectory or if it's alert.xml
    if (filePath.includes('/alerts/') || path.basename(filePath) === 'alert.xml') {
        return;
    }

    console.log(`Processing ${filePath}...`);
    const content = fs.readFileSync(filePath, 'utf8');
    const extracted = extractMainElement(content);

    if (!extracted) {
        console.log(`Could not extract main element from ${filePath}`);
        return;
    }

    const targetDir = ELEMENT_DIRECTORIES[extracted.type];
    if (!targetDir) {
        console.log(`No directory mapping found for element type: ${extracted.type}`);
        return;
    }

    const targetDirPath = path.join(TEST_DATA_DIR, targetDir);
    ensureDirectoryExists(targetDirPath);

    const fileName = path.basename(filePath);
    const targetPath = path.join(targetDirPath, fileName);

    // Write the extracted element to the new file
    fs.writeFileSync(targetPath, extracted.content);
    console.log(`Created ${targetDir}/${fileName}`);

    // Delete the original file
    fs.unlinkSync(filePath);
    console.log(`Deleted original file ${fileName}`);
}

/**
 * Main function to reorganize test data
 */
function reorganizeTestData() {
    const files = fs.readdirSync(TEST_DATA_DIR);

    for (const file of files) {
        if (file.endsWith('.xml')) {
            const filePath = path.join(TEST_DATA_DIR, file);
            if (fs.statSync(filePath).isFile()) {
                processFile(filePath);
            }
        }
    }
}

// Run the reorganization
reorganizeTestData(); 