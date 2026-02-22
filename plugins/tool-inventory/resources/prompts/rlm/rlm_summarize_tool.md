Analyze this CLI tool source code and extract a high-fidelity JSON summary.
The summary must map to the project's "Gold Standard" header format.

PRIORITY: If the file contains a top-level docstring header (Gold Standard), extract details DIRECTLY from there.

File: {file_path}
Code:
{content}

Instructions:
1. "purpose": 1-2 sentence description of what the script actually does. Extract from "Purpose" if present.
2. "layer": Architectural layer (e.g., "Curate / Rlm", "Orchestrator").
3. "supported_object_types": Array of supported types mentioned in the header.
4. "usage": Array of exact executable commands including required flags.
5. "args": Array of CLI arguments with descriptions.
6. "inputs": Array of input files or APIs consumed.
7. "outputs": Array of output files or state changes.
8. "dependencies": List of other scripts or libraries this tool relies on.
9. "consumed_by": Known workflows or scripts that invoke this tool.
10. "key_functions": The 3-5 most critical classes or functions and their roles.

Format: Output ONLY the raw JSON object. Do not wrap in markdown code blocks. Ensure all strings are escaped.

{
  "purpose": "...",
  "layer": "...",
  "supported_object_types": ["..."],
  "usage": ["..."],
  "args": ["..."],
  "inputs": ["..."],
  "outputs": ["..."],
  "dependencies": ["..."],
  "consumed_by": ["..."],
  "key_functions": ["..."]
}

JSON:
