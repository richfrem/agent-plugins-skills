Analyze this CLI tool source code and extract a high-fidelity JSON summary perfectly aligned with the Recursive Language Model (RLM) philosophy.

# RLM Core Philosophy: Summarize Once, Reuse Many
Your summary will be cached and read by other AI agents during future tasks. It must be dense and accurate enough to **entirely replace the need for an AI agent to read this source file again**, unless they are making direct, code-level modifications to it.

The summary is the agent's map: if the summary is good, the agent understands the terrain and doesn't have to scan the file. Only recurse to read the full file when strictly applicable.

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
