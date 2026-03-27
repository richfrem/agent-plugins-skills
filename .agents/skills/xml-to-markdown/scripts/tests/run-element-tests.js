import { execFile } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execFileAsync = promisify(execFile);

async function ensureDirectoryExists(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
}

async function runTest(testFile, outputDir) {
    const testName = path.basename(testFile);
    const outputFile = path.join(outputDir, `${testName}.log`);
    const summaryFile = path.join(outputDir, 'summary.log');

    console.log(`\n\n=== Running test: ${testName} ===\n`);
    try {
        // Use execFile for argument safety (prevents shell injection)
        const { stdout, stderr } = await execFileAsync(
            'node',
            ['--experimental-vm-modules', 'node_modules/jest/bin/jest.js', testFile],
            { shell: false }
        );
        
        // Write detailed output to individual test file
        fs.writeFileSync(outputFile, `=== Test Output for ${testName} ===\n\n${stdout}\n\n${stderr || ''}`);
        
        // Append summary to summary file
        fs.appendFileSync(summaryFile, 
            `\n=== ${testName} ===\n` +
            `Status: ${stderr ? 'FAILED' : 'PASSED'}\n` +
            `Time: ${new Date().toISOString()}\n\n`
        );

        console.log(stdout);
        if (stderr) console.error(stderr);
    } catch (error) {
        // Write error output to file
        fs.writeFileSync(outputFile, 
            `=== Test Error for ${testName} ===\n\n` +
            `Error: ${error.message}\n\n` +
            `${error.stdout || ''}\n${error.stderr || ''}`
        );
        
        // Append error summary
        fs.appendFileSync(summaryFile,
            `\n=== ${testName} ===\n` +
            `Status: ERROR\n` +
            `Error: ${error.message}\n` +
            `Time: ${new Date().toISOString()}\n\n`
        );

        console.error(`Error running test ${testName}:`, error.message);
    }
    console.log(`\n=== Finished test: ${testName} ===\n`);
}

async function main() {
    const testDir = 'tests/elements';
    const outputDir = 'test-output/elements';
    
    // Ensure output directory exists
    await ensureDirectoryExists(outputDir);
    
    // Clear previous summary
    const summaryFile = path.join(outputDir, 'summary.log');
    fs.writeFileSync(summaryFile, `Element Tests Summary - ${new Date().toISOString()}\n\n`);

    const files = fs.readdirSync(testDir)
        .filter(file => file.endsWith('.test.js'))
        .map(file => path.join(testDir, file));

    console.log(`Found ${files.length} test files to run\n`);
    fs.appendFileSync(summaryFile, `Total test files: ${files.length}\n\n`);

    for (const file of files) {
        await runTest(file, outputDir);
        // Wait for 1 second between tests
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    console.log(`\nAll tests completed. Results saved in ${outputDir}`);
    console.log(`Summary available at ${summaryFile}`);
}

main().catch(console.error);