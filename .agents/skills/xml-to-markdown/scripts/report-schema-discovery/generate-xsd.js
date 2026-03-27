/**
 * tools/standalone/xml-to-markdown/report-schema-discovery/generate-xsd.js
 * =========================================================================
 * 
 * Purpose:
 *   Generates an XSD schema file from the report_schema.json discovery output.
 * 
 * Usage:
 *   node generate-xsd.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SCHEMA_FILE = path.join(__dirname, 'report_schema.json');
const OUTPUT_FILE = path.join(__dirname, '../../../../legacy-system/oracle-forms/OracleSchema/reports.xsd');

// XML Schema Header
const XSD_HEADER = `<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" elementFormDefault="qualified">
`;

const XSD_FOOTER = `</xs:schema>`;

function generateXSD() {
    console.log('Generating reports.xsd...');

    if (!fs.existsSync(SCHEMA_FILE)) {
        console.error(`Error: Schema file not found: ${SCHEMA_FILE}`);
        process.exit(1);
    }

    const schemaData = JSON.parse(fs.readFileSync(SCHEMA_FILE, 'utf8'));
    const elements = schemaData.elements;

    let xsd = XSD_HEADER;

    // Sort elements alphabetically
    const elementNames = Object.keys(elements).sort();

    for (const name of elementNames) {
        const el = elements[name];

        xsd += `  <!-- Element: ${name} (Count: ${el.count}) -->\n`;
        xsd += `  <xs:element name="${name}">\n`;
        xsd += `    <xs:complexType mixed="true">\n`;
        xsd += `      <xs:sequence>\n`;
        xsd += `        <xs:any minOccurs="0" maxOccurs="unbounded" processContents="skip"/>\n`;
        xsd += `      </xs:sequence>\n`;

        // Add attributes
        if (el.attributes && el.attributes.length > 0) {
            for (const attr of el.attributes) {
                xsd += `      <xs:attribute name="${attr}" type="xs:string" use="optional"/>\n`;
            }
        }

        xsd += `    </xs:complexType>\n`;
        xsd += `  </xs:element>\n\n`;
    }

    xsd += XSD_FOOTER;

    fs.writeFileSync(OUTPUT_FILE, xsd);
    console.log(`Generated XSD: ${OUTPUT_FILE}`);
    console.log(`Defined ${elementNames.length} elements.`);
}

generateXSD();
