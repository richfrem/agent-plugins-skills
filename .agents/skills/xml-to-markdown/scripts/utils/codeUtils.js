/**
 * tools/standalone/xml-to-markdown/src/utils/codeUtils.js
 * ========================================================
 * 
 * Purpose:
 *   PL/SQL and SQL code formatting utilities. Handles entity decoding,
 *   whitespace normalization, and syntax-aware indentation.
 * 
 * Exports:
 *   - cleanCode(): Decode entities, normalize whitespace
 *   - formatCode(): Add indentation
 *   - formatCodeWithSyntax(): Wrap in markdown code fence
 *   - formatSQL(): SQL-specific formatting
 *   - formatPLSQL(): PL/SQL-specific formatting
 * 
 * @module codeUtils
 */

/**
 * Gets the code and type from an XML element
 * @param {Object} element - The XML element to get code and type from
 * @returns {Object} Object containing code and type
 */
export function getElementCodeAndType(element) {
    if (!element || typeof element !== 'object') {
        return { code: null, type: null };
    }

    const code = element._ || null;
    const type = element._attributes?.Type || null;

    return { code, type };
}

/**
 * Extracts PL/SQL code from a node
 * @param {Object} node - The node containing PL/SQL code
 * @returns {string} Extracted and cleaned PL/SQL code
 */
export function extractCode(node) {
    if (!node || !node.ProgramUnit) return '';

    const programUnit = Array.isArray(node.ProgramUnit) ? node.ProgramUnit[0] : node.ProgramUnit;
    if (!programUnit || !programUnit.Text) return '';

    const text = Array.isArray(programUnit.Text) ? programUnit.Text[0] : programUnit.Text;
    return cleanCode(text);
}

/**
 * Cleans and formats code
 * @param {string} code - The code to clean
 * @returns {string} Cleaned and formatted code
 */


/**
 * Decodes XML/HTML entities and cleans up code formatting.
 * Handles named entities, numeric decimal and hex entities, and whitespace normalization.
 */
export function cleanCode(code) {
    if (!code) return '';

    // Decode named HTML/XML entities
    const namedEntities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
        '&nbsp;': ' '
    };

    for (const [entity, char] of Object.entries(namedEntities)) {
        code = code.replace(new RegExp(entity, 'g'), char);
    }

    // Decode numeric decimal entities (e.g., &#10;)
    code = code.replace(/&#(\d+);/g, (_, dec) => String.fromCharCode(dec));

    // Decode numeric hexadecimal entities (e.g., &#x9;)
    code = code.replace(/&#x([0-9a-fA-F]+);/g, (_, hex) =>
        String.fromCharCode(parseInt(hex, 16))
    );

    // Normalize line endings to Unix-style
    code = code.replace(/\r\n?/g, '\n');

    // Trim leading/trailing whitespace
    code = code.trim();

    // Collapse multiple blank lines to a maximum of one
    code = code.replace(/\n{3,}/g, '\n\n');

    return code;
}



/**
 * Formats code with proper indentation
 * @param {string} code - The code to format
 * @param {number} indentLevel - The indentation level
 * @returns {string} Formatted code
 */
export function formatCode(code, indentLevel = 0) {
    if (!code) return '';

    const indent = '  '.repeat(indentLevel);
    return code.split('\n').map(line => `${indent}${line}`).join('\n');
}

/**
 * Formats code with syntax highlighting in markdown
 * @param {string} code - The code to format
 * @param {string} language - The language for syntax highlighting (e.g., 'sql', 'plsql', 'javascript')
 * @returns {string} The formatted code in a markdown code block
 */
export function formatCodeWithSyntax(code, language = 'text') {
    if (!code) return '';

    const cleanedCode = cleanCode(code);
    return `\`\`\`${language}\n${cleanedCode}\n\`\`\`\n`;
}

/**
 * Formats SQL code with proper indentation
 * @param {string} code - The SQL code to format
 * @returns {string} - Formatted SQL code
 */
export function formatSQL(code) {
    if (!code) return '';

    const cleanedCode = cleanCode(code);
    const lines = cleanedCode.split('\n');
    let formattedLines = [];
    let indentLevel = 0;

    for (let line of lines) {
        line = line.trim();
        if (!line) continue;

        // Handle SQL-specific indentation
        if (line.match(/^(FROM|WHERE|GROUP BY|HAVING|ORDER BY|JOIN|LEFT JOIN|RIGHT JOIN|INNER JOIN|OUTER JOIN|UNION|UNION ALL|INTERSECT|MINUS)\b/i)) {
            indentLevel = 1;
        } else if (line.match(/^(AND|OR)\b/i)) {
            indentLevel = 2;
        } else if (line.match(/^SELECT\b/i)) {
            indentLevel = 0;
        }

        // Add indentation
        formattedLines.push('    '.repeat(indentLevel) + line);
    }

    return formattedLines.join('\n');
}

/**
 * Formats PL/SQL code with proper indentation
 * @param {string} code - The PL/SQL code to format
 * @returns {string} - Formatted PL/SQL code
 */
export function formatPLSQL(code) {
    if (!code) return '';

    const cleanedCode = cleanCode(code);
    const lines = cleanedCode.split('\n');
    let formattedLines = [];
    let indentLevel = 0;

    for (let line of lines) {
        line = line.trim();
        if (!line) continue;

        // Handle PL/SQL-specific indentation
        if (line.match(/^(END|ELSE|ELSIF|EXCEPTION|WHEN|THEN)\b/i)) {
            indentLevel = Math.max(0, indentLevel - 1);
        }

        // Add indentation
        formattedLines.push('    '.repeat(indentLevel) + line);

        if (line.match(/^(BEGIN|IF|ELSE|ELSIF|LOOP|WHILE|FOR|CASE)\b/i)) {
            indentLevel++;
        }
    }

    return formattedLines.join('\n');
} 