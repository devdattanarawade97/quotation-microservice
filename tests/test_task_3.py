import os
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
# FIX: Corrected import path to include 'src' package
from src.services.rag_core import RAGCore, FAISS_AVAILABLE
# FIX: Corrected import path to include 'src' package
from src.services.llm_utils import get_mock_embedding, get_llm_response_rag

# Mock FAISS for tests if it's not available in the test environment
# This allows tests to run even if faiss-cpu isn't perfectly set up,
# though actual FAISS should be tested if possible.
@pytest.fixture(autouse=True)
def mock_faiss_import():
    if not FAISS_AVAILABLE:
        with patch('services.rag_core.faiss', new=MagicMock()) as mock_faiss:
            mock_faiss.IndexFlatL2.return_value = MagicMock()
            mock_faiss.IndexFlatL2.return_value.search.return_value = (np.array([[0.1]]), np.array([[0]]))
            yield
    else:
        yield


@pytest.fixture
def mock_data_dir(tmp_path):
    """Create temporary mock data files for testing."""
    data_path = tmp_path / "data"
    data_path.mkdir()

    doc1_en = data_path / "document1_en.txt"
    doc1_en.write_text("The quick brown fox jumps over the lazy dog. Fox is an animal.")

    doc2_ar = data_path / "document2_ar.txt"
    doc2_ar.write_text("القط السريع البني يقفز فوق الكلب الكسول. الكلب حيوان.", encoding='utf-8')
    
    return data_path

def test_rag_pipeline_english_query(mock_data_dir):
    """Test the RAG pipeline with an English query."""
    doc_paths = [
        os.path.join(mock_data_dir, "document1_en.txt"),
        os.path.join(mock_data_dir, "document2_ar.txt")
    ]

    rag_core = RAGCore(document_paths=doc_paths)

    query = "What is a fox?"
    response = rag_core.query(query_text=query, language="en")
   
    print(f"\n--- Test: English Query ---")
    print(f"Query: {query}")
    print(f"Answer: {response['answer']}")
    print(f"Citations: {response['citations']}")
    print(f"Retrieved Chunks: {response['retrieved_chunks']}")

    assert "answer" in response
    assert isinstance(response["answer"], str)
    assert len(response["answer"]) > 0
    assert "citations" in response
    assert isinstance(response["citations"], list)
    assert len(response["citations"]) > 0 # Expect at least one citation
    assert "document1_en.txt" in response["citations"]
    assert "English Answer:" in response["answer"]

def test_rag_pipeline_arabic_query(mock_data_dir):
    """Test the RAG pipeline with an Arabic query."""
    doc_paths = [
        os.path.join(mock_data_dir, "document1_en.txt"),
        os.path.join(mock_data_dir, "document2_ar.txt")
    ]

    rag_core = RAGCore(document_paths=doc_paths)

    query = "ما هو الكلب؟" # What is a dog?
    response = rag_core.query(query_text=query, language="ar")

    print(f"\n--- Test: Arabic Query ---")
    print(f"Query: {query}")
    print(f"Answer: {response['answer']}")
    print(f"Citations: {response['citations']}")
    print(f"Retrieved Chunks: {response['retrieved_chunks']}")

    assert "answer" in response
    assert isinstance(response["answer"], str)
    assert len(response["answer"]) > 0
    assert "citations" in response
    assert isinstance(response["citations"], list)
    assert len(response["citations"]) > 0 # Expect at least one citation
    assert "document2_ar.txt" in response["citations"]
    assert "الإجابة العربية:" in response["answer"]

def test_rag_no_relevant_context(mock_data_dir):
    """Test RAG pipeline when no relevant context is found."""
    doc_paths = [
        os.path.join(mock_data_dir, "document1_en.txt")
    ]

    rag_core = RAGCore(document_paths=doc_paths)

    query = "What is the capital of France?" # Irrelevant query
    response = rag_core.query(query_text=query, language="en", top_k=1)
    
    print(f"\n--- Test: No Relevant Context Query ---")
    print(f"Query: {query}")
    print(f"Answer: {response['answer']}")
    print(f"Citations: {response['citations']}")
    print(f"Retrieved Chunks: {response['retrieved_chunks']}")

    assert "answer" in response
    assert isinstance(response["answer"], str)
    assert "not directly answering" in response["answer"] or "cannot answer" in response["answer"]
    assert "citations" in response
    assert len(response["citations"]) >= 0 # Can be 0 if mock search is truly empty
