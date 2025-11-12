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

# FIX: Changed to a relative import to correctly reference llm_utils within the same 'services' package
from .llm_utils import get_mock_embedding, get_llm_response_rag

class RAGCore:
    """
    Core class for Retrieval Augmented Generation (RAG) functionality.

    Manages document ingestion, chunking, embedding, indexing (using FAISS if available),
    and querying to retrieve relevant context for an LLM.
    """
    def __init__(self, document_paths: List[str], chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initializes the RAGCore pipeline.

        Args:
            document_paths (List[str]): A list of file paths to the documents to be ingested.
            chunk_size (int, optional): The maximum size of text chunks. Defaults to 500.
            chunk_overlap (int, optional): The overlap between consecutive text chunks. Defaults to 50.
        """
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
        """
        Initializes the entire RAG pipeline: loads documents, chunks them,
        generates embeddings, and builds the FAISS index.
        """
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
        """
        Loads text content from the specified document paths.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, each containing
                                  'text' (content) and 'source' (filename) of a document.
        """
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
        """
        Splits loaded documents into smaller, overlapping chunks.

        Args:
            documents (List[Dict[str, str]]): A list of documents, each with 'text' and 'source'.

        Returns:
            List[Dict[str, str]]: A list of document chunks, each with 'text', 'source', and 'chunk_id'.
        """
        all_chunks = []
        for doc in documents:
            texts = self.text_splitter.split_text(doc['text'])
            for i, text in enumerate(texts):
                chunk_id = f"{doc['source']}_chunk_{i}"
                self.source_map[chunk_id] = doc['source'] # Map chunk_id to original source
                all_chunks.append({'text': text, 'source': doc['source'], 'chunk_id': chunk_id})
        return all_chunks

    def get_embeddings(self, chunks: List[Dict[str, str]]) -> np.ndarray:
        """
        Generates mock embeddings for each text chunk.

        Args:
            chunks (List[Dict[str, str]]): A list of text chunks.

        Returns:
            np.ndarray: A NumPy array of float32 embeddings.
        """
        embeddings_list = []
        for chunk in chunks:
            embeddings_list.append(get_mock_embedding(chunk['text']))
        return np.array(embeddings_list).astype('float32') # FAISS requires float32

    def build_faiss_index(self, embeddings: np.ndarray):
        """
        Builds a FAISS index from the generated embeddings.

        If FAISS is not available or if there are no embeddings, a mock index (None) is returned.

        Args:
            embeddings (np.ndarray): A NumPy array of float32 embeddings.

        Returns:
            faiss.IndexFlatL2 or None: The built FAISS index or None if FAISS is not available.
        """
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
        """
        Executes a RAG query: retrieves relevant chunks, then generates an LLM answer.

        Performs a vector search on the FAISS index (or mock search) to find top_k
        most relevant chunks, then passes these chunks as context to the LLM to
        formulate an answer.

        Args:
            query_text (str): The user's query string.
            language (str, optional): The desired language for the LLM response ('en' or 'ar').
                                      Defaults to "en".
            top_k (int, optional): The number of top relevant chunks to retrieve. Defaults to 3.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - "answer" (str): The LLM-generated answer.
                - "citations" (List[str]): A list of source filenames for the retrieved context.
                - "latency_ms" (float): Mock latency for LLM processing in milliseconds.
                - "cost_usd" (float): Mock cost for LLM processing in USD.
                - "retrieved_chunks" (List[str]): The text content of the retrieved chunks.
        """
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
