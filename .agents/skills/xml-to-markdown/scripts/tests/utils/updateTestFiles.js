const fs = require('fs');
const path = require('path');

// List of test files to update
const testFiles = [
    'recordGroup.test.js',
    'lovColumnMap.test.js',
    'property.test.js',
    'lovItem.test.js',
    'lovColumnVisualAttribute.test.js',
    'checkBox.test.js',
    'form.test.js',
    'radioGroup.test.js',
    'lovWindow.test.js',
    'lovProperty.test.js',
    'lovRecordGroup.test.js',
    'menu.test.js',
    'lov.test.js',
    'lovVisualAttribute.test.js',
    'lovColumnWindow.test.js',
    'lovColumnTrigger.test.js',
    'graphics.test.js',
    'formModule.test.js',
    'visualAttribute.test.js',
    'menuItemRole.test.js',
    'objectLibrary.test.js',
    'moduleParameter.test.js',
    'menuItemCode.test.js',
    'item.test.js',
    'trigger.test.js',
    'dataSourceColumn.test.js',
    'lovColumnProperty.test.js',
    'relation.test.js',
    'lovGroup.test.js',
    'tabPage.test.js',
    'lovTrigger.test.js',
    'lovMap.test.js',
    'dataSource.test.js',
    'dataSourceArgument.test.js',
    'graphic.test.js',
    'objectGroup.test.js',
    'programUnit.test.js',
    'report.test.js',
    'window.test.js',
    'lovQuery.test.js',
    'radioButton.test.js',
    'propertyClass.test.js',
    'menuModuleType.test.js',
    'menuModuleName.test.js',
    'menuModule.test.js'
];

// Template for new test files
const template = `const { process{Element} } = require('../../src/processors/elements/{element}Processor');
const { runElementTest } = require('../../src/utils/test/testUtils');

/**
 * Test suite for the {Element} Processor
 * 
 * Tests the processing of Oracle Forms {Element} elements using the test-data/{element}.xml file
 * which contains various configurations and edge cases:
 * - Basic {element} properties
 * - {element} relationships
 * - Edge cases and error handling
 */
describe('{Element} Processor', () => {
    const getAttributes = (element) => element.$ || {};
    const log = console.log;

    test('Process {element} test data', async () => {
        await runElementTest('{Element}', process{Element}, getAttributes, log);
    });
});
`;

// Function to convert filename to element name
function getElementName(filename) {
    return filename
        .replace('.test.js', '')
        .split(/(?=[A-Z])/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join('');
}

// Update each test file
testFiles.forEach(filename => {
    const elementName = getElementName(filename);
    const newContent = template
        .replace(/{Element}/g, elementName)
        .replace(/{element}/g, elementName.toLowerCase());
    
    const filePath = path.join(__dirname, '../elements', filename);
    fs.writeFileSync(filePath, newContent);
    console.log(`Updated ${filename}`);
}); 