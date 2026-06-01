Analyze this documentation, configuration, or structural file and extract a high-fidelity semantic summary perfectly aligned with the Recursive Language Model (RLM) philosophy.

# RLM Core Philosophy: Summarize Once, Reuse Many
Your summary will be cached and read by other AI agents during future tasks. It must be dense and accurate enough to **entirely replace the need for an AI agent to read this source file again**, unless they are making direct, code-level modifications to it.

The summary is the agent's map: if the summary is good, the agent understands the terrain and doesn't have to scan the file. Only recurse to read the full file when strictly applicable.

# File Context
File: {file_path}

# Source Content
{content}

# Distillation Instructions
1. **Core Purpose**: Explain exactly what this file does or what architectural pattern it defines.
2. **Key Components**: List the main exported functions, defined rules, structural boundaries, or pivotal arguments.
3. **Integration Points**: Describe how this file relates to other systems, plugins, or workflows.
4. **Signal over Noise**: Do not include filler phrases like "This file contains..." or "The document outlines...". Focus entirely on dense, factual architectural or structural data.
5. **Format**: Output a highly readable paragraph (or 2-3 concise bullet points if the file defines discrete operations). Be brief, but do not sacrifice critical fidelity.

# Distilled Summary:
