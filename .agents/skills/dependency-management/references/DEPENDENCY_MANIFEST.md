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

- **`requirements.txt`**: Core dependencies for general development, CI/CD, and MCP servers (lightweight, fast installation)
- **`requirements-finetuning.txt`**: Heavy ML/CUDA dependencies for model fine-tuning (PyTorch, transformers, etc.)

This split reduces CI/CD installation time and prevents dependency conflicts. For fine-tuning tasks, use `requirements-finetuning.txt`. For general development and testing, use `requirements.txt`.

---

## Unified Dependency Manifest (Example)

**Note:** The listings below represent an *example* of a complete dependency set used in a unified ML/AI architecture. They are intended to demonstrate how a complex project can be modeled into clear, strategic dependency categories. Your actual project's `requirements.txt` will vary.

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

| Library | Version | the project Usage |
| :--- | :--- | :--- |
| `langchain` | 1.0.5 | The primary orchestration framework for the **RAG system** and agentic workflows, connecting all RAG components. |
| `langchain-chroma`| 1.0.0 | The specific bridge connecting our RAG pipeline to the **ChromaDB vector store**, the physical layer of the **RAG system**. |
| `langchain-community`| 0.4.1 | Provides community components, including the `MarkdownHeaderTextSplitter` used to intelligently chunk our protocols and chronicles. |
| `langchain-nomic`| 1.0.0 | Integration for Nomic's high-quality text embedding models, enabling sovereign, on-device text vectorization. |
| `langchain-ollama`| 1.0.0 | The specific LangChain integration that allows the RAG pipeline to use our sovereign **Ollama** instance for answer generation. |
| `langchain-text-splitters`| 1.0.0 | Contains the specific text splitting algorithms used by the `ingest.py` script to prepare the Cognitive Genome for the Cortex. |
| `chromadb` | 1.3.4 | The client for the Chroma vector database, which serves as the persistent, local-first storage for the **RAG system**. |
| `nomic[local]` | 3.9.0 | The Nomic embedding library itself, allowing the **RAG system** to generate text embeddings without relying on external APIs. |

### Data Science & Machine Learning

| Library | Version | the project Usage |
| :--- | :--- | :--- |
| `numpy` | 1.26.2 | The fundamental package for numerical operations, underpinning nearly all ML libraries used in model training and data analysis. |
| `pandas` | 2.2.2 | Used for preparing, cleaning, and structuring the `JSONL` datasets for fine-tuning in **core ML training**. |
| `scikit-learn`| 1.7.1 | Used for calculating evaluation metrics to assess the performance of fine-tuned models and for classical ML tasks. |
| `scipy` | 1.16.1 | Core library for scientific and technical computing, a dependency for many data science and ML packages. |
| `stable_baselines3`| 2.7.0 | The Reinforcement Learning framework used to train **the maintenance agent** agent, enabling it to learn and propose improvements to the Genome. |
| `gymnasium` | 1.2.0 | The toolkit for building the RL "environment" that **the maintenance agent** operates in—a sandboxed version of our repository. |
| `optuna` | 4.4.0 | Hyperparameter optimization framework used to efficiently tune the training parameters for **core ML training**. |
| `pyarrow` | 19.0.0 | High-performance data library used by Pandas and ChromaDB for efficient in-memory data operations. |
| `ray` | 2.48.0 | A framework for distributed computing, planned for future use in scaling up **Gardener** training and multi-agent simulations. |
| `tenseal` | 0.3.16 | Library for Homomorphic Encryption, architected for the **secure sandbox** to enable privacy-preserving federated simulations. |
| `joblib` | 1.5.1 | Lightweight pipelining library used by scikit-learn for parallel processing and caching. |
| `threadpoolctl` | 3.6.0 | Controls the number of threads used by low-level libraries for parallel processing. |
| `networkx` | 3.5 | Library for creating, manipulating, and studying complex networks and graphs. |
| `sympy` | 1.14.0 | Computer algebra system for symbolic mathematics, used in scientific computing. |
| `mpmath` | 1.3.0 | Multi-precision floating-point arithmetic library, dependency for SymPy. |

### Observability & Monitoring

| Library | Version | the project Usage |
| :--- | :--- | :--- |
| `wandb` | 0.21.0 | Weights & Biases client for logging and visualizing the results of **core ML training** fine-tuning runs. |
| `tensorboard` | 2.19.0 | A visualization toolkit for inspecting ML experiments, especially during **Gardener** agent training. |
| `tensorboardX` | 2.6.4 | A library for PyTorch to interface with TensorBoard for logging. |
| `tensorboard-data-server` | 0.7.2 | Backend server for TensorBoard data serving. |
| `sentry-sdk` | 2.34.1 | SDK for the Sentry error tracking platform, planned for production-grade monitoring of the **AGORA**. |
| `seaborn` | 0.13.2 | High-level data visualization library for generating plots of benchmark results and training performance. |
| `matplotlib` | 3.10.5 | The foundational plotting library in Python, used by Seaborn. |
| `contourpy` | 1.3.3 | Contour plotting library for matplotlib. |
| `cycler` | 0.12.1 | Composable style cycles for matplotlib. |
| `fonttools` | 4.59.0 | Library for manipulating fonts, used by matplotlib. |
| `kiwisolver` | 1.4.8 | Fast implementation of the Cassowary constraint solver, used by matplotlib. |
| `pillow` | 10.4.0 | Python Imaging Library fork, used for image processing in matplotlib and other visualization tasks. |

### Development, Testing & Code Quality

| Library | Version | the project Usage |
| :--- | :--- | :--- |
| `pytest` | 8.4.1 | The framework for our automated test suite, ensuring the reliability of the **RAG system** and **agent infrastructure**. |
| `pytest-cov`| 6.2.1 | `pytest` plugin to measure code coverage, enforcing rigor in our development process. |
| `coverage` | 7.10.1 | Core coverage measurement library used by pytest-cov. |
| `black` | 25.1.0 | The uncompromising code formatter that maintains a consistent code style across the project, honoring the **clean code principles**. |
| `flake8` | 7.3.0 | A tool for checking Python code against style guides (PEP 8) and finding logical errors. |
| `GitPython` | 3.1.45 | Powers the **agent infrastructure's mechanical git operations**, allowing it to execute **atomic commits**. |
| `mypy_extensions` | 1.1.0 | Extensions for mypy type checking. |
| `pathspec` | 0.12.1 | Utility library for pattern matching of file paths, used by Black. |
| `platformdirs` | 4.3.8 | Platform-specific directory locations library. |
| `pycodestyle` | 2.14.0 | Python style guide checker, used by flake8. |
| `pyflakes` | 3.4.0 | Passive checker of Python programs, used by flake8. |
| `mccabe` | 0.7.0 | McCabe complexity checker, used by flake8. |

### Documentation Generation

| Library | Version | the project Usage |
| :--- | :--- | :--- |
| `Sphinx` | 8.2.3 | The primary tool for creating our formal, human-readable documentation. |
| `sphinx-rtd-theme`| 3.0.2 | The "Read the Docs" theme for Sphinx, providing a clean, modern look. |
| `docutils` | 0.21.2 | Core dependency for Sphinx, provides the reStructuredText parsing engine. |
| `Pygments` | 2.19.2 | Provides syntax highlighting for code blocks in documentation. |
| `Jinja2` | 3.1.6 | The templating engine used by Sphinx to generate HTML pages. |
| `alabaster` | 1.0.0 | Default theme for Sphinx documentation. |
| `babel` | 2.17.0 | Internationalization library used by Sphinx for localization. |
| `imagesize` | 1.4.1 | Library for getting image size from image files, used by Sphinx. |
| `packaging` | 25.0 | Core utilities for Python packages, used by Sphinx. |
| `requests` | 2.32.5 | HTTP library for downloading resources, used by Sphinx extensions. |
| `snowballstemmer` | 3.0.1 | Stemming library for search functionality in Sphinx. |
| `sphinxcontrib-applehelp` | 2.0.0 | Apple Help output support for Sphinx. |
| `sphinxcontrib-devhelp` | 2.0.0 | Devhelp output support for Sphinx. |
| `sphinxcontrib-htmlhelp` | 2.0.0 | HTML Help output support for Sphinx. |
| `sphinxcontrib-jquery` | 4.1 | jQuery support for Sphinx themes. |
| `sphinxcontrib-jsmath` | 1.0.1 | jsMath support for Sphinx. |
| `sphinxcontrib-qthelp` | 2.0.0 | Qt Help output support for Sphinx. |
| `sphinxcontrib-serializinghtml` | 2.0.0 | Serializing HTML output support for Sphinx. |

### Core Utilities & Dependencies

| Library | Version | the project Usage |
| :--- | :--- | :--- |
| `python-dotenv`| 1.2.1 | Secures the Forge by loading critical secrets like API keys from `.env` files. |
| `PyYAML` | 6.0.2 | Used for parsing configuration files (e.g., `model_card.yaml`) and other structured data. |
| `pydantic` | 2.11.7 | The core data validation library used extensively by LangChain and our own data schemas to ensure type safety and structural integrity. |
| `pydantic_core` | 2.33.2 | Core validation logic for Pydantic. |
| `annotated-types` | 0.7.0 | Reusable constraint types for Pydantic. |
| `SQLAlchemy` | 2.0.42 | A powerful SQL toolkit used as a backend dependency by `langchain` and `chromadb`. |
| `alembic` | 1.16.4 | A database migration tool for SQLAlchemy, used by our dependencies to manage their internal database schemas. |
| `Mako` | 1.3.10 | Templating library used by Alembic for migration files. |
| `httpx` | 0.28.1 | The modern asynchronous HTTP client used by the `ollama` and `google-generativeai` SDKs for all API requests. |
| `httpcore` | 1.0.9 | Core HTTP functionality for httpx. |
| `h11` | 0.16.0 | HTTP/1.1 protocol implementation for httpcore. |
| `anyio` | 4.9.0 | Asynchronous networking library, dependency for httpx. |
| `sniffio` | 1.3.1 | Sniff out which async library is being used, dependency for httpx. |
| `requests` | 2.32.5 | A robust, synchronous HTTP client used as a fallback or by various libraries for API communication. |
| `urllib3` | 2.5.0 | HTTP client library, dependency for requests. |
| `certifi` | 2025.7.14 | Collection of root certificates for validating SSL certificates. |
| `charset-normalizer` | 3.4.2 | Universal character encoding detector, used by requests. |
| `idna` | 3.10 | Internationalized Domain Names in Applications, used by requests. |
| `protobuf` | 5.29.5 | Google's data interchange format, used by grpcio and various ML libraries. |
| `grpcio` | 1.74.0 | gRPC Python library for high-performance RPC framework. |
| `absl-py` | 2.3.1 | Abseil Python libraries, dependency for TensorFlow/PyTorch ecosystems. |
| `six` | 1.17.0 | Python 2/3 compatibility library. |
| `typing_extensions` | 4.14.1 | Backported type hints for older Python versions. |
| `typing-inspection` | 0.4.1 | Runtime type inspection utilities. |
| `attrs` | 25.3.0 | Classes without boilerplate, used by various libraries. |
| `jsonschema` | 4.25.0 | JSON Schema validation library. |
| `jsonschema-specifications` | 2025.4.1 | JSON Schema specifications. |
| `referencing` | 0.36.2 | Cross-references for JSON Schema. |
| `rpds-py` | 0.26.0 | Python bindings for rpds, used by jsonschema. |
| `click` | 8.2.1 | Command line interface creation kit. |
| `colorlog` | 6.9.0 | Colored formatter for Python logging. |
| `filelock` | 3.18.0 | Platform independent file locking. |
| `fsspec` | 2025.3.0 | Filesystem abstraction layer. |
| `gitdb` | 4.0.12 | Git object database, dependency for GitPython. |
| `smmap` | 5.0.2 | Sliding memory map, dependency for gitdb. |
| `huggingface-hub` | 0.36.0 | Client library for Hugging Face Hub. |
| `hf-xet` | 1.1.5 | Hugging Face Xet filesystem. |
| `iniconfig` | 2.1.0 | Brain-dead simple config-ini parsing, used by pytest. |
| `Markdown` | 3.8.2 | Python implementation of Markdown. |
| `MarkupSafe` | 3.0.2 | Safely add untrusted strings to HTML/XML markup. |
| `msgpack` | 1.1.1 | MessagePack serializer. |
| `pluggy` | 1.6.0 | Command line argument parsing library. |
| `python-dateutil` | 2.9.0.post0 | Extensions to the standard Python datetime module. |
| `pytz` | 2025.2 | World timezone definitions. |
| `regex` | 2025.7.34 | Alternative regular expression module. |
| `roman-numerals-py` | 3.1.0 | Roman numerals conversion library. |
| `setuptools` | 80.9.0 | Build system for Python packages. |
| `tqdm` | 4.67.1 | Fast, extensible progress bar for Python. |
| `tzdata` | 2025.2 | Timezone data for Python. |
| `Werkzeug` | 3.1.3 | WSGI utility library, dependency for various web frameworks. |
| `cloudpickle` | 3.1.1 | Extended pickling support for Python objects. |
| `Farama-Notifications` | 0.0.4 | Notification system for Farama Foundation projects. |
| `pyparsing` | 3.2.3 | Alternative approach to creating parsers in Python. |

---

## Strategic Dependency Management

### Version Pinning Strategy

All dependencies are explicitly version-pinned to ensure **reproducible builds** and prevent unexpected breaking changes. This aligns with the **atomic commit principles** by guaranteeing that the the project's cognitive infrastructure remains stable across deployments.

**Synchronization Status:** This manifest is now fully synchronized with the `setup_cuda_env.py` script outputs, ensuring that automated setup and manual installation produce identical environments.

### Dependency Categories

1. **Core Infrastructure**: LangChain, ChromaDB, Ollama - The backbone of our cognitive architecture
2. **AI/ML Stack**: PyTorch, Transformers, PEFT, TRLoRA, BitsAndBytes - Sovereign model training and inference with memory optimization
3. **Data Processing**: Pandas, NumPy, PyArrow - Dataset preparation and analysis
4. **Observability**: Weights & Biases, TensorBoard - Experiment tracking and monitoring
5. **Development**: pytest, Black, flake8 - Code quality and testing
6. **Documentation**: Sphinx, Pygments - Technical documentation generation

### Future Considerations

- **Dependency Auditing**: Regular security audits of all dependencies
- **License Compliance**: Ensuring all dependencies align with our sovereign software principles
- **Performance Optimization**: Monitoring and optimizing dependency load times
- **Alternative Sources**: Planning for local/offline package repositories

---

*This manifest is automatically maintained through our unified dependency management system. Updates are coordinated through the **agent infrastructure** to ensure architectural coherence.*