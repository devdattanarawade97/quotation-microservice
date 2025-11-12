import os
import time
from services.rag_core import RAGCore
from services.llm_utils import get_llm_response # For general chat, if needed

def main():
    """
    Main function to run the RAG Knowledge Base CLI application.

    This function sets up the RAG pipeline, loads documents, and enters
    an interactive loop to allow users to ask questions and receive
    answers augmented with retrieved context from the documents.
    """
    print("Starting RAG Knowledge Base CLI...")

    # Define document paths
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.join(script_dir, "../../data") # Adjusted path to correctly reach 'data' directory
    document_paths = [
        os.path.join(data_dir, "document1_en.txt"),
        os.path.join(data_dir, "document2_ar.txt")
    ]

    # Ensure data directory exists and documents are present (for robustness)
    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found at {data_dir}")
        print("Please ensure data/document1_en.txt and data/document2_ar.txt exist.")
        return
    for path in document_paths:
        if not os.path.exists(path):
            print(f"Error: Document not found: {path}")
            print("Please ensure data/document1_en.txt and data/document2_ar.txt exist.")
            return

    # Initialize RAGCore
    try:
        rag_core = RAGCore(document_paths=document_paths)
    except Exception as e:
        print(f"Failed to initialize RAGCore: {e}")
        print("Please ensure all required libraries (faiss-cpu, langchain-text-splitters, numpy) are installed.")
        return

    print("\nEntering Q&A loop. Type 'exit' to quit.")
    while True:
        query = input("\nEnter your question (e.g., 'What is a brown fox?' or 'ما هو الثعلب البني؟'): ")
        if query.lower() == 'exit':
            break

        language_input = input("Enter desired answer language (en/ar, default en): ").lower()
        language = "ar" if language_input == "ar" else "en"

        start_time = time.time()
        response = rag_core.query(query_text=query, language=language)
        end_time = time.time()

        print("\n--- Answer ---")
        print(response["answer"])
        print("\n--- Citations ---")
        if response["citations"]:
            for citation in response["citations"]:
                print(f"- {citation}")
        else:
            print("No relevant citations found.")
        
        print("\n--- Report ---")
        print(f"Total Query Time: {(end_time - start_time):.2f} seconds")
        print(f"LLM Latency (mock): {response['latency_ms']:.2f} ms")
        print(f"LLM Cost (mock): ${response['cost_usd']:.4f}")
        print(f"Retrieved Chunks Count: {len(response['retrieved_chunks'])}")

if __name__ == "__main__":
    main()

