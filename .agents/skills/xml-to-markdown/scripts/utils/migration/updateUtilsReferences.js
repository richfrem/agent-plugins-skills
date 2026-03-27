/**
 * Migration Script: Update Utils References
 * ==========================================
 * 
 * Purpose:
 *   Updates import paths across the codebase when utility modules are moved
 *   to new locations. This handles refactoring of import statements.
 * 
 * Usage:
 *   node updateUtilsReferences.js
 * 
 * What it does:
 *   1. Scans all .js files in src directory
 *   2. Finds import statements matching old paths
 *   3. Replaces with new paths from IMPORT_UPDATES map
 *   4. Reports updated files count
 * 
 * @module updateUtilsReferences
 */

import fs from 'fs';
import path from 'path';
import { promisify } from 'util';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);

// Map of old imports to new imports
const IMPORT_UPDATES = {
  './xmlParser.js': './utils/xmlParser.js',
  './attributeUtils.js': './utils/attributeUtils.js',
  './codeUtils.js': './utils/codeUtils.js',
  './logger.js': './utils/logger.js',
  './outputUtils.js': './utils/outputUtils.js',
  '../xmlParser.js': '../utils/xmlParser.js',
  '../attributeUtils.js': '../utils/attributeUtils.js',
  '../codeUtils.js': '../utils/codeUtils.js',
  '../logger.js': '../utils/logger.js',
  '../outputUtils.js': '../utils/outputUtils.js',
};

// Function name updates (if any functions were renamed)
const FUNCTION_UPDATES = {
  'createMockParser': 'createMockParser',
  'createLoggerForEnvironment': 'createLoggerForEnvironment',
};

async function updateFile(filePath) {
  try {
    let content = await readFile(filePath, 'utf8');
    let modified = false;

    // Update imports
    for (const [oldImport, newImport] of Object.entries(IMPORT_UPDATES)) {
      const importRegex = new RegExp(`from ['"]${oldImport.replace('.', '\\.')}['"]`, 'g');
      if (importRegex.test(content)) {
        content = content.replace(importRegex, `from '${newImport}'`);
        modified = true;
      }
    }

    // Update function names
    for (const [oldName, newName] of Object.entries(FUNCTION_UPDATES)) {
      const functionRegex = new RegExp(`\\b${oldName}\\b`, 'g');
      if (functionRegex.test(content)) {
        content = content.replace(functionRegex, newName);
        modified = true;
      }
    }

    if (modified) {
      await writeFile(filePath, content);
      console.log(`Updated: ${filePath}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error);
    return false;
  }
}

async function findJsFiles(dir) {
  const files = await fs.promises.readdir(dir);
  const jsFiles = [];

  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = await fs.promises.stat(fullPath);

    if (stat.isDirectory()) {
      jsFiles.push(...(await findJsFiles(fullPath)));
    } else if (file.endsWith('.js')) {
      jsFiles.push(fullPath);
    }
  }

  return jsFiles;
}

async function main() {
  try {
    console.log('Starting utils reference update...');

    // Find all .js files in src directory
    const jsFiles = await findJsFiles(path.resolve('src'));

    let updatedCount = 0;
    let errorCount = 0;

    // Process each file
    for (const file of jsFiles) {
      try {
        const wasUpdated = await updateFile(file);
        if (wasUpdated) updatedCount++;
      } catch (error) {
        console.error(`Failed to process ${file}:`, error);
        errorCount++;
      }
    }

    console.log('\nUpdate complete!');
    console.log(`Files processed: ${jsFiles.length}`);
    console.log(`Files updated: ${updatedCount}`);
    console.log(`Errors encountered: ${errorCount}`);

  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

// Run the migration
main(); 