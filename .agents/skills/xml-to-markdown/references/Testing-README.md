# Testing Guide

**Note:** This guide applies to the xml-to-markdown conversion tool located at `tools/standalone/xml-to-markdown/`. All paths below are relative to that folder.

This document outlines how to run and write tests for the Oracle Forms XML Parser project.

## Requirements

- Node.js (version 14 or higher)
- npm (comes with Node.js)
- Jest (testing framework)

## Installation

1. Clone the repository
2. Change directory to the conversion project:

```bash
cd tools/standalone/xml-to-markdown
```

3. Install dependencies:

```bash
npm install
```

## Running Tests

### Running All Tests

To run all tests in the project:

```bash
npm test
```

This will execute all test files in the `tests/` directory using the correct configuration for ES modules.

### Running Element-Specific Tests

Each XML element has its own processor and corresponding test file. To test a specific element:

1. Navigate to the elements test directory:

```bash
cd tests/elements
```

2. Run the specific element test:

```bash
npm test {ElementName}.test.js
```

For example:

```bash
# Test the Module processor
npm test Module.test.js

# Test the FormModule processor
npm test FormModule.test.js

# Test the Block processor
npm test Block.test.js
```

Available element tests include:

- Module.test.js
- FormModule.test.js
- MenuModule.test.js
- ObjectLibrary.test.js
- Block.test.js
- Item.test.js
- Trigger.test.js
- And many more (see tests/elements directory)

### Running Multiple Element Tests

To run tests for multiple elements:

```bash
# Run tests for all Module-related elements
npm test Module*.test.js

# Run tests for all Form-related elements
npm test Form*.test.js
```

### Watch Mode

To run tests in watch mode (tests re-run when files change):

```bash
npm test -- --watch
```

## Test Structure

Tests are organized in the `tests/` directory, mirroring the structure of the `src/` directory:

```
xml-to-markdown/
  tests/
    ├── elements/
    │   ├── Module.test.js
    │   ├── FormModule.test.js
    │   ├── Block.test.js
    │   └── ...
    └── modules/
        └── elementProcessor.test.js
```

Each processor in `src/processors/elements/` has a corresponding test file in `tests/elements/`.

## Test Data

Test XML files are located in the `test-data/` directory. These files contain sample Oracle Forms XML structures used in tests.

## Writing Tests

Example test structure using ES modules:

```javascript
import { processElement } from "../../src/processors/elements/elementProcessor.js";
import { runElementTest } from "../../src/utils/test/testUtils.js";

describe("Element Processor", () => {
  const getAttributes = (element) => element.$ || {};
  const getElementCodeAndType = () => ({ code: "", type: "" });
  const formatCode = (code) => code;
  const log = console.log;

  test("Process element test data", async () => {
    await runElementTest(
      "ElementName",
      (element, attrs, logFn, output) =>
        processElement(
          element,
          attrs,
          getElementCodeAndType,
          formatCode,
          logFn,
          output
        ),
      getAttributes,
      log
    );
  });
});
```

## Best Practices

1. Each test file should focus on testing one processor
2. Use descriptive test names that explain the scenario being tested
3. Set up and tear down test data in `beforeEach` and `afterEach` blocks
4. Mock dependencies when appropriate
5. Test both valid and invalid inputs
6. Test edge cases and error conditions
7. Always use ES module syntax (import/export) instead of CommonJS (require/module.exports)

## Debugging Tests

To debug tests:

1. Add console.log statements in your tests:

```javascript
console.log("Output:", mockOutput);
```

2. Run Jest with verbose output:

```bash
npm test -- --verbose
```

3. Run a specific test with debugging:

```bash
node --inspect-brk --experimental-vm-modules node_modules/.bin/jest --runInBand tests/elements/Module.test.js
```

## Common Issues

1. **Test fails with "Cannot use import statement outside a module"**

   - Make sure you're using `npm test` instead of `npx jest`
   - Verify that package.json has `"type": "module"`
   - Check that jest.config.js is properly configured for ES modules

2. **Test fails due to missing XML file**

   - Ensure all required test XML files are present in `test-data/`
   - Check file paths are correct

3. **Processor function not found**

   - Verify the import path is correct and includes the .js extension
   - Check that the function is properly exported from the processor file

4. **Unexpected test output**
   - Compare the actual output with expected output
   - Check if the test data matches the expected format
   - Verify the processor is handling the input correctly

## Adding New Tests

When adding a new processor:

1. Create a new test file in `tests/elements/` using ES module syntax
2. Add corresponding test XML data in `test-data/`
3. Follow the existing test patterns
4. Run tests to verify the new processor works correctly
5. Update batch processing tests if necessary

## CI/CD Integration

Tests are automatically run in the CI/CD pipeline. Ensure all tests pass locally before pushing changes:

```bash
npm test
```

For any questions or issues, please open a GitHub issue or contact the maintainers.
