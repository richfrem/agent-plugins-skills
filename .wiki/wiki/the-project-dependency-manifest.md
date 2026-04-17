---
concept: the-project-dependency-manifest
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/dependency-management/references/DEPENDENCY_MANIFEST.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.027888+00:00
cluster: library
content_hash: 681a12d0c72dd8b7
---

# the project Dependency Manifest

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# the project Dependency Manifest

**Version:** 5.0 (Unified Dependency Architecture - Synchronized with Setup Script)
**Generated:** 2025-11-15

## Preamble

This document provides the canonical manifest of all Python dependencies for the project, reflecting the strategic decision to adopt a unified dependency architecture. This approach supersedes the previous poly-dependency model and prioritizes simplified environment setup and management for all developers and agents.

In accordance with the clean code principles, each dependency is cataloged with its specific role and strategic purpose within the the project's unified architecture.

---

---

## Dependency File Structure

**As of 2025-11-26**, the project uses a split dependency architecture:

- **`../../../requirements.txt`**: Core dependencies for general development, CI/CD, and MCP servers (lightweight, fast installation)
- **`requirements-finetuning.txt`**: Heavy ML/CUDA dependencies for model fine-tuning (PyTorch, transformers, etc.)

This split reduces CI/CD installation time and prevents dependency conflicts. For fine-tuning tasks, use `requirements-finetuning.txt`. For general development and testing, use `../../../requirements.txt`.

---

## Unified Dependency Manifest (Example)

**Note:** The listings below represent an *example* of a complete dependency set used in a unified ML/AI architecture. They are intended to demonstrate how a complex project can be modeled into clear, strategic dependency categories. Your actual project's `../../../requirements.txt` will vary.

### AI & Cognitive Engines

| Library | Version | the project Usage |
| :--- | :--- | :--- |
| `torch` | 2.8.0+cu126 | The foundational engine for **core ML training**, used to fine-tune and merge sovereign AI models like `custom models`. |
| `torchvision` | 0.23.0+cu126 | PyTorch's computer vision library, used for image processing in optical compression and model training. |
| `torchaudio` | 2.8.0+cu126 | PyTorch's audio processing library, used for audio-based AI operations. |
| `transformers`| 4.56.1 | Hugging Face's core library for accessing and training models, serving as the primary tool for the **core training pipeline**. |
| `tokenizers` | 0.22.1 | Hugging Face's high-performance library for converting text into tokens, a critical pre-processing step for fine-tuning. |
| `safetensors` | 0.5.3 | Secure and efficient format for saving and loading the weights of our sovereignly-forged models. |
| `accelerate` | 1.4.0 | PyTorch library for distributed training and inference optimization, enabling efficient GPU utilization in **core ML training**. |
| `peft` | 0.11.1 | Parameter-Efficient Fine-Tuning library, enabling QLoRA and other memory-efficient fine-tuning techniques for sovereign AI development. |
| `trl` | 0.23.0 | Transformer Reinforcement Learning library, used for advanced fine-tuning techniques in **core ML training**. |
| `bitsandbytes` | 0.45.3 | 8-bit quantization library, enabling memory-efficient model loading and inference for large language models. |
| `datasets` | 3.3.2 | Hugging Face's dataset library, used for loading and preprocessing training data for model fine-tuning. |
| `tf-keras` | 2.18.0 | TensorFlow's Keras API, providing compatibility layer for TensorFlow operations within our ML stack. |
| `xformers` | 0.0.33.post1 | Memory-efficient transformer implementations, optimizing attention mechanisms for better performance in sovereign AI operations. |
| `ollama` | 0.6.0 | The official client for interacting with the **Ollama engine**, our primary sovereign local LLM substrate for generation and reasoning. |
| `google-generativeai` | 0.8.3 | The official SDK for interacting with the Google Gemini series of models, one of the **agent infrastructure's** key cognitive substrates. |
| `gpt4all` | 2.8.2 | Provides an alternative local inference backend, ensuring redundancy and cognitive diversity in our sovereign model stack. |

### RAG system (Memory & RAG)

| Library |

*(content truncated)*

## See Also

- [[identity-the-adr-manager]]
- [[project-name]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[project-setup-reference-guide]]
- [[identity-the-backport-reviewer]]
- [[identity-the-eval-lab-setup-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/dependency-management/references/DEPENDENCY_MANIFEST.md`
- **Indexed:** 2026-04-17T06:42:10.027888+00:00
