import os
import time
import json
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
try:
    from langchain.storage import LocalFileStore, EncoderBackedStore
except ImportError:
    try:
        from langchain_classic.storage.file_system import LocalFileStore
        from langchain_classic.storage.encoder_backed import EncoderBackedStore
    except ImportError:
        from langchain_community.storage import LocalFileStore, EncoderBackedStore

def _doc_to_bytes(doc: Document) -> bytes:
    data = {"page_content": doc.page_content, "metadata": doc.metadata}
    return json.dumps(data).encode("utf-8")

def _bytes_to_doc(b: bytes) -> Document:
    data = json.loads(b.decode("utf-8"))
    return Document(page_content=data.get("page_content", ""), metadata=data.get("metadata", {}))

class VectorDBOperations:
    """
    Core domain logic for Vector DB operations.
    """
    def __init__(
        self,
        project_root: str,
        child_collection: str = "vector_child_v1",
        parent_collection: str = "vector_parent_v1",
        chroma_host: str = "",
        chroma_port: int = 8110,
        chroma_data_path: str = ".vector_data"
    ):
        self.project_root = Path(project_root)
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.chroma_data_path = chroma_data_path
        self.child_collection_name = child_collection
        self.parent_collection_name = parent_collection
        
        _client = None
        if self.chroma_host:
            print(f"[CON] Connecting to ChromaDB at {self.chroma_host}:{self.chroma_port}...")
            try:
                _client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
                _client.heartbeat()
            except Exception as e:
                print(f"[WARN] Failed to connect to remote ChromaDB ({e}). Falling back to local.")
                _client = None

        if _client is None:
            db_path = (self.project_root / self.chroma_data_path).resolve()
            print(f"[DIR] Connecting to local persistent ChromaDB at {db_path}...")
            db_path.mkdir(parents=True, exist_ok=True)
            _client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )
        self.chroma_client = _client

        print("[MODEL] Loading Nomic embeddings model...")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="nomic-ai/nomic-embed-text-v1.5",
            model_kwargs={'device': 'cpu', 'trust_remote_code': True},
            encode_kwargs={'normalize_embeddings': True}
        )

        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.child_collection_name,
            embedding_function=self.embedding_model
        )

        docstore_path = self.project_root / self.chroma_data_path / self.parent_collection_name
        docstore_path.mkdir(parents=True, exist_ok=True)
        underlying_store = LocalFileStore(str(docstore_path))
        self.store = EncoderBackedStore(
            store=underlying_store,
            key_encoder=lambda x: x,
            value_serializer=_doc_to_bytes,
            value_deserializer=_bytes_to_doc
        )

    def purge(self):
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
            import shutil
            shutil.rmtree(docstore_path)
            print(f"[PURGE] Removed parent store: {docstore_path}")
        docstore_path.mkdir(parents=True, exist_ok=True)

    def ingest_documents(self, documents: List[Document]) -> dict:
        if not documents:
            return {"chunks": 0, "parents": 0}

        child_docs_to_add = []
        parent_count = 0

        for doc in documents:
            parent_chunks = self.parent_splitter.split_documents([doc])
            for parent_chunk in parent_chunks:
                parent_id = str(uuid4())
                parent_count += 1
                self.store.mset([(parent_id, parent_chunk)])
                sub_docs = self.child_splitter.split_documents([parent_chunk])
                for sub_doc in sub_docs:
                    sub_doc.metadata["parent_id"] = parent_id
                    child_docs_to_add.append(sub_doc)

        batch_size = 5000
        total_children = len(child_docs_to_add)
        for i in range(0, total_children, batch_size):
            batch = child_docs_to_add[i:i + batch_size]
            self.vectorstore.add_documents(batch)

        return {"chunks": total_children, "parents": parent_count}

    def query(self, query_text: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results = self.vectorstore.similarity_search_with_score(query_text, k=max_results)
        formatted_results = []
        seen_parents = set()

        for doc, score in results:
            parent_id = doc.metadata.get("parent_id")
            final_content = doc.page_content
            has_parent = False
            
            if parent_id:
                if parent_id in seen_parents:
                    continue
                seen_parents.add(parent_id)
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

    def get_stats(self) -> Dict[str, Any]:
        try:
            collection = self.chroma_client.get_collection(name=self.child_collection_name)
            child_count = collection.count()
            docstore_path = self.project_root / self.chroma_data_path / self.parent_collection_name
            parent_count = sum(1 for _ in docstore_path.glob("*")) if docstore_path.exists() else 0
            return {
                "child_count": child_count, 
                "parent_count": parent_count,
                "status": "healthy"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
