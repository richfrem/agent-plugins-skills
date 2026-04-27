---
concept: attempt-to-handle-langchain-version-differences-for-storage
source: plugin-code
source_file: vector-db/scripts/operations.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.432334+00:00
cluster: import
content_hash: 4b707d295d37da81
---

# Attempt to handle LangChain version differences for storage

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
operations.py
=====================================

Purpose:
    Core domain logic for Vector DB operations, including parent-child splitting,
    embedding generation, and multi-vector retrieval.

Layer: Retrieve / Curate

Usage:
    from operations import VectorDBOperations
"""

import os
import time
import json
import shutil
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Any, Optional, Tuple

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Attempt to handle LangChain version differences for storage
try:
    from langchain.storage import LocalFileStore, EncoderBackedStore
except ImportError:
    try:
        from langchain_classic.storage.file_system import LocalFileStore
        from langchain_classic.storage.encoder_backed import EncoderBackedStore
    except ImportError:
        from langchain_community.storage import LocalFileStore, EncoderBackedStore

def _doc_to_bytes(doc: Document) -> bytes:
    """Serializes a Document to a UTF-8 JSON byte string."""
    data = {"page_content": doc.page_content, "metadata": doc.metadata}
    return json.dumps(data).encode("utf-8")

def _bytes_to_doc(b: bytes) -> Document:
    """Deserializes a Document from a UTF-8 JSON byte string."""
    data = json.loads(b.decode("utf-8"))
    return Document(page_content=data.get("page_content", ""), metadata=data.get("metadata", {}))


class VectorDBOperations:
    """
    Manages the lifecycle of the Vector Database and its multi-vector storage.
    """

    def __init__(
        self,
        project_root: str,
        child_collection: str = "vector_child_v1",
        parent_collection: str = "vector_parent_v1",
        chroma_host: str = "",
        chroma_port: int = 8110,
        chroma_data_path: str = ".vector_data",
        embedding_model: str = "nomic-ai/nomic-embed-text-v1.5",
        parent_chunk_size: int = 2000,
        parent_chunk_overlap: int = 200,
        child_chunk_size: int = 400,
        child_chunk_overlap: int = 50,
        device: str = "cpu"
    ) -> None:
        """
        Initializes the Vector DB operation environment.

        Args:
            project_root: Root directory of the project.
            child_collection: Name of the fine-grained search collection.
            parent_collection: Name of the context-rich parent storage.
            chroma_host: Optional host for remote Chroma server.
            chroma_port: Optional port for remote Chroma server.
            chroma_data_path: Local path for persistent database storage.
            embedding_model: Name of the model to use for embeddings.
            parent_chunk_size: Size of parent context chunks.
            parent_chunk_overlap: Overlap for parent chunks.
            child_chunk_size: Size of child search chunks.
            child_chunk_overlap: Overlap for child chunks.
            device: Hardware device to use ('cpu' or 'cuda').
        """
        self.project_root = Path(project_root)
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.chroma_data_path = chroma_data_path
        self.child_collection_name = child_collection
        self.parent_collection_name = parent_collection
        
        self.chroma_client = self._init_chroma_client()
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': device, 'trust_remote_code': True},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Splitters for Parent-Child architecture
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size, 
            chunk_overlap=child_chunk_overlap, 
            separators=["\n\n", "\n", " ", ""]
        )
 

*(content truncated)*

## See Also

- [[pre-parse-for---headless-to-set-non-interactive-backend-before-pyplot-import]]
- [[try-to-import-rlm-for-code-context-injection]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/scripts/operations.py`
- **Indexed:** 2026-04-27T05:21:04.432334+00:00
