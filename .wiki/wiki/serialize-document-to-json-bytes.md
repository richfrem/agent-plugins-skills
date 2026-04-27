---
concept: serialize-document-to-json-bytes
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/operations.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.391492+00:00
cluster: import
content_hash: 22c245fa4c29cd48
---

# Serialize Document to JSON bytes

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/operations.py -->
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
        
        # 2. ChromaDB Client Initialization — local var ensures self.chroma_client is always typed non-None
        _client = None
        if self.chroma_host:
            print(f"🔗 Connecting to ChromaDB at {self.chroma_host}:{self.chroma_port}...")
            try:
                _client = chromadb.HttpClient(host=self.chroma_host, port=self.chroma_port)
                _client.heartbeat()  # raises immediately if server is offline
            except Exception as e:
                print(f"⚠️ Failed to connect to remote ChromaDB ({e}). Falling back to local persistent store.")
                _client = None

        if _client is None:
            # Fallback to persistent local storage if no host defined or host is offline
            db_path = (self.project_root / self.chroma_data_path).resolve()
            print(f"📁 Connecting to local persistent ChromaDB at {db_path}...")
            db_path.mkdir(parents=True, exist_ok=True)
            _client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )
        self.chroma_client = _client

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
     

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/vector-db-launch/scripts/operations.py -->
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

def _doc_to_bytes(doc:

*(combined content truncated)*

## See Also

- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-project-root-to-syspath]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/operations.py`
- **Indexed:** 2026-04-27T05:21:04.391492+00:00
