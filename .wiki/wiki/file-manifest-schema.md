---
concept: file-manifest-schema
source: plugin-code
source_file: context-bundler/assets/resources/file-manifest-schema.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.307136+00:00
cluster: description
content_hash: 32f1f0cb3069935c
---

# File Manifest Schema

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/context-bundler/assets/resources/file-manifest-schema.json -->
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Context Bundler Manifest",
    "description": "Schema for defining a bundle of files for context generation.",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Title of the generated context document."
        },
        "description": {
            "type": "string",
            "description": "Optional description included at the top of the bundle."
        },
        "excludes": {
            "type": "array",
            "description": "Optional list of glob patterns to exclude from recursive directory bundling (e.g., ['*.svg', 'tests/*']).",
            "items": {
                "type": "string"
            }
        },
        "files": {
            "type": "array",
            "description": "List of files to include in the bundle. IMPORTANT: The first file MUST be the prompt/instruction file.",
            "items": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file or directory to include."
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note or annotation about this file."
                    }
                },
                "required": [
                    "path"
                ]
            }
        }
    },
    "required": [
        "title",
        "files"
    ]
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/context-bundler/assets/resources/file-manifest-schema.json -->
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Context Bundler Manifest",
    "description": "Schema for defining a bundle of files for context generation.",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Title of the generated context document."
        },
        "description": {
            "type": "string",
            "description": "Optional description included at the top of the bundle."
        },
        "excludes": {
            "type": "array",
            "description": "Optional list of glob patterns to exclude from recursive directory bundling (e.g., ['*.svg', 'tests/*']).",
            "items": {
                "type": "string"
            }
        },
        "files": {
            "type": "array",
            "description": "List of files to include in the bundle. IMPORTANT: The first file MUST be the prompt/instruction file.",
            "items": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file or directory to include."
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note or annotation about this file."
                    }
                },
                "required": [
                    "path"
                ]
            }
        }
    },
    "required": [
        "title",
        "files"
    ]
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/red-team-bundler/assets/resources/file-manifest-schema.json -->
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Context Bundler Manifest",
    "description": "Schema for defining a bundle of files for context generation.",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Title of the generated context document."
        },
        "description": {
            "type": "string",
            "description": "Optional description included at the top of the bundle."
        },
        "excludes": {
            "type": "array",
            "description": "Optional list of glob patterns to exclude from recursive directory bundling (e.g., ['*.svg', 'tests/*']).",
            "items": {
                "type": "string"
            }
        },
        "files": {
            "type": "array",
            "description": "List of files to include in the bundle. IMPORTANT: The first file MUST be the prompt/instruction file.",
            "items": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file or directory to include."
                    },
                    "note": {
                        "type": "string",
                        "description": "Optional note or annotation about this file."
                    }
                },
                "required": [
           

*(combined content truncated)*

## See Also

- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[file-manifest]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[audit-a-single-file]]
- [[distiller-manifest]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `context-bundler/assets/resources/file-manifest-schema.json`
- **Indexed:** 2026-04-27T05:21:04.307136+00:00
