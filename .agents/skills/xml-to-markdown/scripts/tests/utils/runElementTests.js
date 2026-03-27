import { testAlertProcessor } from '../elements/alert.test.js';
import { testAttachedLibraryProcessor } from '../elements/attachedLibrary.test.js';
import { testBlockProcessor } from '../elements/block.test.js';
import { testCanvasProcessor } from '../elements/canvas.test.js';
import { testCheckboxProcessor } from '../elements/checkBox.test.js';
import { testCoordinateProcessor } from '../elements/coordinate.test.js';
import { testDataSourceProcessor } from '../elements/dataSource.test.js';
import { testDataSourceArgumentProcessor } from '../elements/dataSourceArgument.test.js';
import { testDataSourceColumnProcessor } from '../elements/dataSourceColumn.test.js';
import { testFormProcessor } from '../elements/form.test.js';
import { testFormModuleProcessor } from '../elements/formModule.test.js';
import { testGraphicProcessor } from '../elements/graphic.test.js';
import { testGraphicsProcessor } from '../elements/graphics.test.js';
import { testItemProcessor } from '../elements/item.test.js';
import { testLovProcessor } from '../elements/lov.test.js';
import { testLovColumnMapProcessor } from '../elements/lovColumnMap.test.js';
import { testLovColumnPropertyProcessor } from '../elements/lovColumnProperty.test.js';
import { testLovColumnTriggerProcessor } from '../elements/lovColumnTrigger.test.js';
import { testLovColumnVisualAttributeProcessor } from '../elements/lovColumnVisualAttribute.test.js';
import { testLovColumnWindowProcessor } from '../elements/lovColumnWindow.test.js';
import { testLovGroupProcessor } from '../elements/lovGroup.test.js';
import { testLovItemProcessor } from '../elements/lovItem.test.js';
import { testLovMapProcessor } from '../elements/lovMap.test.js';
import { testLovPropertyProcessor } from '../elements/lovProperty.test.js';
import { testLovQueryProcessor } from '../elements/lovQuery.test.js';
import { testLovRecordGroupProcessor } from '../elements/lovRecordGroup.test.js';
import { testLovTriggerProcessor } from '../elements/lovTrigger.test.js';
import { testLovVisualAttributeProcessor } from '../elements/lovVisualAttribute.test.js';
import { testLovWindowProcessor } from '../elements/lovWindow.test.js';
import { testMenuProcessor } from '../elements/menu.test.js';
import { testMenuItemCodeProcessor } from '../elements/menuItemCode.test.js';
import { testMenuItemRoleProcessor } from '../elements/menuItemRole.test.js';
import { testMenuModuleProcessor } from '../elements/menuModule.test.js';
import { testMenuModuleNameProcessor } from '../elements/menuModuleName.test.js';
import { testMenuModuleTypeProcessor } from '../elements/menuModuleType.test.js';
import { testModuleParameterProcessor } from '../elements/moduleParameter.test.js';
import { testObjectGroupProcessor } from '../elements/objectGroup.test.js';
import { testObjectLibraryProcessor } from '../elements/objectLibrary.test.js';
import { testProgramUnitProcessor } from '../elements/programUnit.test.js';
import { testPropertyProcessor } from '../elements/property.test.js';
import { testPropertyClassProcessor } from '../elements/propertyClass.test.js';
import { testRadioButtonProcessor } from '../elements/radioButton.test.js';
import { testRadioGroupProcessor } from '../elements/radioGroup.test.js';
import { testRecordGroupProcessor } from '../elements/recordGroup.test.js';
import { testRelationProcessor } from '../elements/relation.test.js';
import { testReportProcessor } from '../elements/report.test.js';
import { testTabPageProcessor } from '../elements/tabPage.test.js';
import { testTriggerProcessor } from '../elements/trigger.test.js';
import { testVisualAttributeProcessor } from '../elements/visualAttribute.test.js';
import { testWindowProcessor } from '../elements/window.test.js';

/**
 * Runs all element processor tests
 */
async function runAllElementTests() {
    try {
        console.log('Starting all element processor tests...');
        
        // Run all test processors
        await Promise.all([
            testAlertProcessor(),
            testAttachedLibraryProcessor(),
            testBlockProcessor(),
            testCanvasProcessor(),
            testCheckboxProcessor(),
            testCoordinateProcessor(),
            testDataSourceProcessor(),
            testDataSourceArgumentProcessor(),
            testDataSourceColumnProcessor(),
            testFormProcessor(),
            testFormModuleProcessor(),
            testGraphicProcessor(),
            testGraphicsProcessor(),
            testItemProcessor(),
            testLovProcessor(),
            testLovColumnMapProcessor(),
            testLovColumnPropertyProcessor(),
            testLovColumnTriggerProcessor(),
            testLovColumnVisualAttributeProcessor(),
            testLovColumnWindowProcessor(),
            testLovGroupProcessor(),
            testLovItemProcessor(),
            testLovMapProcessor(),
            testLovPropertyProcessor(),
            testLovQueryProcessor(),
            testLovRecordGroupProcessor(),
            testLovTriggerProcessor(),
            testLovVisualAttributeProcessor(),
            testLovWindowProcessor(),
            testMenuProcessor(),
            testMenuItemCodeProcessor(),
            testMenuItemRoleProcessor(),
            testMenuModuleProcessor(),
            testMenuModuleNameProcessor(),
            testMenuModuleTypeProcessor(),
            testModuleParameterProcessor(),
            testObjectGroupProcessor(),
            testObjectLibraryProcessor(),
            testProgramUnitProcessor(),
            testPropertyProcessor(),
            testPropertyClassProcessor(),
            testRadioButtonProcessor(),
            testRadioGroupProcessor(),
            testRecordGroupProcessor(),
            testRelationProcessor(),
            testReportProcessor(),
            testTabPageProcessor(),
            testTriggerProcessor(),
            testVisualAttributeProcessor(),
            testWindowProcessor()
        ]);
        
        console.log('All element processor tests completed successfully!');
    } catch (error) {
        console.error('Error running element processor tests:', error);
        process.exit(1);
    }
}

/**
 * Runs a specific test file
 * @param {string} testFile - The path to the test file to run
 */
async function runSpecificTest(testFile) {
    const testModule = await import(testFile);
    const testFunction = Object.values(testModule)[0];
    if (typeof testFunction === 'function') {
        await testFunction();
    } else {
        console.error(`No test function found in ${testFile}`);
        process.exit(1);
    }
}

// If this file is run directly, run all tests
if (process.argv[1] === import.meta.url) {
    runAllElementTests();
}

export { runAllElementTests, runSpecificTest }; 