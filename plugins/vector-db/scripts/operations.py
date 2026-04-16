#!/usr/bin/env python3
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
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size, 
            chunk_overlap=parent_chunk_overlap, 
            separators=["\n\n", "\n", " ", ""]
        )

        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.child_collection_name,
            embedding_function=self.embedding_model
        )

        self.store = self._init_parent_store()

    def _init_chroma_client(self) -> Any:
        """Initializes either an HTTP or Persistent Chroma client based on config."""
        if self.chroma_host:
            print(f"[CON] Connecting to ChromaDB at {self.chroma_host}:{self.chroma_port}...")
            try:
                client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
                client.heartbeat()
                return client
            except Exception as e:
                print(f"[WARN] Failed to connect to remote ChromaDB ({e}). Falling back to local.")

        db_path = (self.project_root / self.chroma_data_path).resolve()
        print(f"[DIR] Connecting to local persistent ChromaDB at {db_path}...")
        db_path.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(db_path), settings=Settings(anonymized_telemetry=False))

    def _init_parent_store(self) -> EncoderBackedStore:
        """Sets up the filesystem-backed parent document store."""
        docstore_path = self.project_root / self.chroma_data_path / self.parent_collection_name
        docstore_path.mkdir(parents=True, exist_ok=True)
        underlying_store = LocalFileStore(str(docstore_path))
        return EncoderBackedStore(
            store=underlying_store,
            key_encoder=lambda x: x,
            value_serializer=_doc_to_bytes,
            value_deserializer=_bytes_to_doc
        )

    def purge(self) -> None:
        """Wipes both child collections and parent storage to start from shell."""
        try:
            self.chroma_client.delete_collection(name=self.child_collection_name)
            print(f"[PURGE] Removed child collection: {self.child_collection_name}")
        except Exception:
            pass
            
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.child_collection_name,
            embedding_function=self.embedding_model
        )

        docstore_path = self.project_root / self.chroma_data_path / self.parent_collection_name
        if docstore_path.exists():
            shutil.rmtree(docstore_path)
            print(f"[PURGE] Removed parent store: {docstore_path}")
        docstore_path.mkdir(parents=True, exist_ok=True)

    def ingest_documents(self, documents: List[Document]) -> Dict[str, int]:
        """
        Splits and ingests a batch of documents into the multi-vector system.

        Args:
            documents: List of raw documents to process.

        Returns:
            Dictionary containing 'chunks' and 'parents' counts.
        """
        if not documents:
            return {"chunks": 0, "parents": 0}

        child_docs: List[Document] = []
        parent_count = 0

        for doc in documents:
            for parent_chunk in self.parent_splitter.split_documents([doc]):
                parent_id = str(uuid4())
                parent_count += 1
                self.store.mset([(parent_id, parent_chunk)])
                
                # Link child chunks to parent ID
                for child_doc in self.child_splitter.split_documents([parent_chunk]):
                    child_doc.metadata["parent_id"] = parent_id
                    child_docs.append(child_doc)

        # Batch write to Chroma
        batch_size = 5000
        for i in range(0, len(child_docs), batch_size):
            self.vectorstore.add_documents(child_docs[i:i + batch_size])

        return {"chunks": len(child_docs), "parents": parent_count}

    def query(self, query_text: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic search and recovers original high-context parents.

        Args:
            query_text: The search query string.
            max_results: Max number of context results to return.

        Returns:
            List of result dictionaries with content and metadata.
        """
        # Load local model and client before search
        results = self.vectorstore.similarity_search_with_score(query_text, k=max_results)
        formatted_results = []
        seen_parents = set()

        for doc, score in results:
            parent_id = doc.metadata.get("parent_id")
            if parent_id in seen_parents:
                continue
            
            seen_parents.add(parent_id)
            final_content = doc.page_content
            has_parent = False
            
            if parent_id:
                parent_docs = self.store.mget([parent_id])
                if parent_docs and parent_docs[0]:
                    final_content = parent_docs[0].page_content
                    doc.metadata.update(parent_docs[0].metadata)
                    has_parent = True
            
            formatted_results.append({
                "content": final_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": float(score),
                "parent_id_matched": parent_id if has_parent else None,
                "has_rlm_context": doc.metadata.get("has_rlm_context", False)
            })
        return formatted_results

    def is_indexed(self, rel_path: str) -> bool:
        """Checks if a file has already been successfully indexed in the child collection."""
        # Normalize to forward slashes to match DB convention
        safe_path = str(rel_path).replace("\\", "/")
        try:
            results = self.chroma_client.get_collection(name=self.child_collection_name).get(
                where={"source": safe_path},
                limit=1
            )
            return len(results["ids"]) > 0
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Returns health status and counts for the Vector collections."""
        try:
            collection = self.chroma_client.get_collection(name=self.child_collection_name)
            docstore_path = self.project_root / self.chroma_data_path / self.parent_collection_name
            return {
                "child_count": collection.count(), 
                "parent_count": sum(1 for _ in docstore_path.glob("*")) if docstore_path.exists() else 0,
                "status": "healthy"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
