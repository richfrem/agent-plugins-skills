/**
 * Detects the type of module from the parsed XML result
 * 
 * XML Structure:
 * <Module>
 *   <FormModule>...</FormModule>    - For form modules
 *   <MenuModule>...</MenuModule>    - For menu modules
 *   <ObjectLibrary>...</ObjectLibrary> - For object libraries
 *   <PLSQLModule>...</PLSQLModule>  - For PL/SQL modules
 *   <ReportModule>...</ReportModule> - For report modules
 * </Module>
 * 
 * @param {Object} result - The parsed XML result containing the module structure
 * @returns {Object} An object containing:
 *   - moduleType: The type of module detected ('FormModule', 'MenuModule', 'ObjectLibrary', etc.)
 *   - module: The module object containing its properties and elements
 * @throws {Error} If the module type cannot be determined or if the XML structure is invalid
 */
function detectModuleType(result) {
    if (!result || typeof result !== 'object') {
        throw new Error('Invalid input: result must be an object');
    }

    if (!result.Module) {
        throw new Error('Error: Root element <Module> not found in XML structure');
    }

    const moduleTypes = [
        'FormModule',
        'MenuModule',
        'ObjectLibrary',
        'PLSQLModule',
        'ReportModule'
    ];

    for (const type of moduleTypes) {
        if (result.Module[type]) {
            return {
                moduleType: type,
                module: result.Module[type]
            };
        }
    }

    throw new Error(`Error: Unknown module type. Expected one of: ${moduleTypes.join(', ')}`);
}

module.exports = { detectModuleType }; 