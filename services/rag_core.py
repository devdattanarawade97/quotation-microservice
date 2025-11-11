import os
import time
import numpy as np
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Mock FAISS for planning, actual FAISS will be imported if installed
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    FAISS_AVAILABLE = False
    print("Warning: FAISS not installed. Using mock vector search. Please install faiss-cpu or faiss-gpu.")

from services.llm_utils import get_mock_embedding, get_llm_response_rag

class RAGCore:
    def __init__(self, document_paths: List[str], chunk_size: int = 500, chunk_overlap: int = 50):
        self.document_paths = document_paths
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        self.documents = [] # List of {'text': ..., 'source': ...}
        self.chunks = []    # List of {'text': ..., 'source': ...}
        self.embeddings = []
        self.index = None
        self.source_map = {}

        self._initialize_pipeline()

    def _initialize_pipeline(self):
        start_time = time.time()
        print("\n--- RAG Pipeline Initialization ---")

        # Ingest
        print("Ingesting documents...")
        self.documents = self.load_documents()
        print(f"Loaded {len(self.documents)} documents.")

        # Chunk
        print("Chunking documents...")
        self.chunks = self.chunk_documents(self.documents)
        print(f"Created {len(self.chunks)} chunks.")

        # Embed
        print("Generating embeddings...")
        self.embeddings = self.get_embeddings(self.chunks)
        print(f"Generated {len(self.embeddings)} embeddings.")

        # Index
        print("Building FAISS index...")
        self.index = self.build_faiss_index(self.embeddings)
        print("FAISS index built.")

        end_time = time.time()
        print(f"Pipeline initialized in {end_time - start_time:.2f} seconds.\n")

    def load_documents(self) -> List[Dict[str, str]]:
        loaded_docs = []
        for path in self.document_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    loaded_docs.append({'text': content, 'source': os.path.basename(path)})
            except Exception as e:
                print(f"Error loading {path}: {e}")
        return loaded_docs

    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        all_chunks = []
        for doc in documents:
            texts = self.text_splitter.split_text(doc['text'])
            for i, text in enumerate(texts):
                chunk_id = f"{doc['source']}_chunk_{i}"
                self.source_map[chunk_id] = doc['source'] # Map chunk_id to original source
                all_chunks.append({'text': text, 'source': doc['source'], 'chunk_id': chunk_id})
        return all_chunks

    def get_embeddings(self, chunks: List[Dict[str, str]]) -> np.ndarray:
        embeddings_list = []
        for chunk in chunks:
            embeddings_list.append(get_mock_embedding(chunk['text']))
        return np.array(embeddings_list).astype('float32') # FAISS requires float32

    def build_faiss_index(self, embeddings: np.ndarray):
        if not FAISS_AVAILABLE:
            print("FAISS not available. Returning mock index.")
            return None # Or implement a simple numpy search

        if embeddings.shape[0] == 0:
            print("No embeddings to build an index.")
            return None

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension) # L2 distance index
        index.add(embeddings)
        return index

    def query(self, query_text: str, language: str = "en", top_k: int = 3) -> Dict[str, Any]:
        query_embedding = np.array([get_mock_embedding(query_text)]).astype('float32')

        if self.index is None or not FAISS_AVAILABLE:
            print("FAISS index not available or built. Performing mock search.")
            # Fallback to simple similarity if FAISS isn't there or if index is empty
            # For a mock, just return a random chunk
            if self.chunks:
                retrieved_chunks_info = [self.chunks[np.random.randint(0, len(self.chunks))]]
            else:
                retrieved_chunks_info = []
            distances = [0.0] * len(retrieved_chunks_info)
        else:
            # Perform search
            distances, indices = self.index.search(query_embedding, top_k)
            retrieved_chunks_info = [self.chunks[i] for i in indices[0] if i < len(self.chunks)]
            distances = distances[0]

        context_texts = [chunk['text'] for chunk in retrieved_chunks_info]
        citations = list(set([chunk['source'] for chunk in retrieved_chunks_info]))

        llm_start_time = time.time()
        answer = get_llm_response_rag(query_text, context_texts, language=language)
        llm_end_time = time.time()

        # Mock latency/cost report
        latency_ms = (time.time() - llm_start_time) * 1000 # Placeholder for actual calculation
        cost_usd = 0.001 * len(query_text) / 1000 # Placeholder for actual calculation

        return {
            "answer": answer,
            "citations": citations,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "retrieved_chunks": [chunk['text'] for chunk in retrieved_chunks_info]
        }

