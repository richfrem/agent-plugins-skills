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
    # Serialize Document to JSON bytes
    data = {"page_content": doc.page_content, "metadata": doc.metadata}
    return json.dumps(data).encode("utf-8")

def _bytes_to_doc(b: bytes) -> Document:
    # Deserialize JSON bytes to Document
    data = json.loads(b.decode("utf-8"))
    return Document(page_content=data.get("page_content", ""), metadata=data.get("metadata", {}))

class VectorDBOperations:
    """
    Core domain logic for Vector DB operations.
    Implements Network-bound ChromaDB connections and Parent-Child MultiVector retrieval.
    
    All configuration is received via constructor parameters — no .env dependency.
    Use VectorConfig to load settings from vector_profiles.json and pass them here.
    """
    def __init__(
        self,
        project_root: str,
        child_collection: str = "knowledge_child_v5",
        parent_collection: str = "knowledge_parent_v5",
        chroma_host: str = "",
        chroma_port: int = 8110,
        chroma_data_path: str = ".vector_data"
    ):
        self.project_root = Path(project_root)
        
        # 1. Store configuration (received from VectorConfig / caller)
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        self.chroma_data_path = chroma_data_path
        self.child_collection_name = child_collection
        self.parent_collection_name = parent_collection
        
        # 2. ChromaDB Client Initialization
        if self.chroma_host:
            print(f"🔗 Connecting to ChromaDB at {self.chroma_host}:{self.chroma_port}...")
            self.chroma_client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
        else:
            # Fallback to persistent local storage if no host defined
            db_path = (self.project_root / self.chroma_data_path).resolve()
            print(f"📁 Connecting to local persistent ChromaDB at {db_path}...")
            db_path.mkdir(parents=True, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )

        # 3. Embeddings (Nomic-v1.5 per architecture spec)
        print("🔄 Loading Nomic embeddings model...")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="nomic-ai/nomic-embed-text-v1.5",
            model_kwargs={'device': 'cpu', 'trust_remote_code': True},
            encode_kwargs={'normalize_embeddings': True}
        )

        # 4. Text Splitters (MultiVector Parent-Child setup)
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            separators=["\\n\\n", "\\n", " ", ""]
        )
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\\n\\n", "\\n", " ", ""]
        )

        # 5. Connect VectorStore
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.child_collection_name,
            embedding_function=self.embedding_model
        )

        # 6. Initialize Parent File Store (Byte Store with Document Encoder)
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
        """Purge existing child collection and parent store entirely."""
        try:
            self.chroma_client.delete_collection(name=self.child_collection_name)
            print(f"🗑️ Purged child collection: {self.child_collection_name}")
        except Exception:
            pass
            
        # Recreate child collection
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.child_collection_name,
            embedding_function=self.embedding_model
        )

        # Purge parent store
        docstore_path = self.project_root / self.chroma_data_path / self.parent_collection_name
        if docstore_path.exists():
            import shutil
            shutil.rmtree(docstore_path)
            print(f"🗑️ Purged parent store: {docstore_path}")
        docstore_path.mkdir(parents=True, exist_ok=True)

    def ingest_documents(self, documents: List[Document]) -> dict:
        """
        Manually processes a list of Documents via the Parent-Child approach.
        1. Splits full file into parent chunks.
        2. Saves parent chunks to FileStore.
        3. Splits parent chunks into child chunks.
        4. Injects parent_id into child metadata.
        5. Saves child chunks to Chroma.
        """
        if not documents:
            return {"chunks": 0, "parents": 0}

        child_docs_to_add = []
        parent_count = 0

        for doc in documents:
            # Step 1: Split into 2000-char parent blocks
            parent_chunks = self.parent_splitter.split_documents([doc])
            
            for parent_chunk in parent_chunks:
                parent_id = str(uuid4())
                parent_count += 1
                
                # Step 2: Save to Key-Value Store
                self.store.mset([(parent_id, parent_chunk)])

                # Step 3: Split into 400-char child blocks for precision search
                sub_docs = self.child_splitter.split_documents([parent_chunk])
                
                # Step 4: Link child back to parent
                for sub_doc in sub_docs:
                    sub_doc.metadata["parent_id"] = parent_id
                    child_docs_to_add.append(sub_doc)

        # Step 5: Save children to Chroma in batches to prevent payload limits
        batch_size = 5000
        total_children = len(child_docs_to_add)
        for i in range(0, total_children, batch_size):
            batch = child_docs_to_add[i:i + batch_size]
            self.vectorstore.add_documents(batch)

        return {"chunks": total_children, "parents": parent_count}

    def query(self, query_text: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Performs semantic search against Child vectors, but returns the full Parent document content.
        """
        # Search the small precision chunks
        results = self.vectorstore.similarity_search_with_score(query_text, k=max_results)
        
        formatted_results = []
        seen_parents = set()

        for doc, score in results:
            parent_id = doc.metadata.get("parent_id")
            
            final_content = doc.page_content
            has_parent = False
            
            if parent_id:
                # Deduplicate overlapping parents so the LLM doesn't get redundant context
                if parent_id in seen_parents:
                    continue
                seen_parents.add(parent_id)

                # Fetch the full 2000-char parent wrapper
                parent_docs = self.store.mget([parent_id])
                if parent_docs and parent_docs[0]:
                    final_content = parent_docs[0].page_content
                    # Update metadata with parent metadata (which retains the actual file source)
                    doc.metadata.update(parent_docs[0].metadata)
                    has_parent = True
            
            formatted_results.append({
                "content": final_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": score,
                "parent_id_matched": parent_id if has_parent else None,
                "has_rlm_context": doc.metadata.get("has_rlm_context", False)
            })

        return formatted_results

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics for both logic layers."""
        try:
            collection = self.chroma_client.get_collection(name=self.child_collection_name)
            child_count = collection.count()
            
            docstore_path = self.project_root / self.chroma_data_path / self.parent_collection_name
            parent_count = sum(1 for _ in docstore_path.glob("*")) if docstore_path.exists() else 0
            
            return {
                "child_collection": self.child_collection_name, 
                "child_chunks": child_count, 
                "parent_store": self.parent_collection_name,
                "parent_documents": parent_count,
                "status": "healthy"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
