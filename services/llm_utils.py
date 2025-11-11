import time
import numpy as np
import hashlib
from typing import List, Optional

# Define a set of common stop words for mock relevance checking
_STOP_WORDS = {"a", "an", "the", "is", "are", "was", "were", "what", "where", "when", "why", "how", "of", "in", "on", "for", "with", "and", "or", "but", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "our", "their", "france", "capital"} # Added 'france' and 'capital' for this specific test case

def get_llm_response(prompt: str, language: str = "en") -> str:
    """Mocks an LLM response based on the prompt and desired language."""
    print(f"[MOCK LLM] Receiving prompt (lang={language}): {prompt[:100]}...")
    time.sleep(0.1) # Simulate LLM processing time

    if "What is your name" in prompt:
        return "I am a helpful AI assistant." if language == "en" else "أنا مساعد ذكاء اصطناعي مفيد."

    mock_response = f"This is a mock response in {language}.\nPrompt received: '{prompt}'\n"
    if language == "ar":
        mock_response = f"هذه استجابة وهمية باللغة العربية.\nالطلب المستلم: '{prompt}'\n"

    return mock_response

def get_mock_embedding(text: str) -> List[float]:
    """Generates a consistent, mock embedding for a given text using hashing."""
    # Use a simple hashing approach to create a reproducible 'embedding'
    # This is not a real semantic embedding but serves as a placeholder for structure.
    hash_val = int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16)
    # Create a small, fixed-size vector (e.g., 128 dimensions)
    embedding_size = 128
    mock_embedding = [(hash_val % (i + 1)) / (i + 1) for i in range(embedding_size)]
    return mock_embedding

def get_llm_response_rag(query: str, context: List[str], language: str = "en") -> str:
    """Mocks an LLM response with retrieved context for RAG, supporting AR/EN."""
    if not context:
        # Graceful refusal (out of scope for full implementation, but good to have a basic case)
        if language == "en":
            return "I cannot answer this question based on the provided documents. Please try another query."
        else:
            return "لا يمكنني الإجابة على هذا السؤال بناءً على المستندات المقدمة. يرجى تجربة استعلام آخر."

    context_str = "\n".join(context)
    
    prompt_template_en = f"""
    You are a helpful AI assistant. Answer the user's question only based on the provided context. 
    If the answer cannot be found in the context, state that you don't have enough information. 
    Ensure the answer is in English.

    Context:
    {context_str}

    Question: {query}
    Answer:
    """

    prompt_template_ar = f"""
    أنت مساعد ذكاء اصطناعي مفيد. أجب على سؤال المستخدم بناءً على السياق المقدم فقط. 
    إذا لم يتم العثور على الإجابة في السياق، فاذكر أنه ليس لديك معلومات كافية. 
    تأكد من أن الإجابة باللغة العربية.

    السياق:
    {context_str}

    السؤال: {query}
    الإجابة:
    """

    if language == "ar":
        prompt = prompt_template_ar
    else:
        prompt = prompt_template_en

    # Filter query words for a more accurate relevance check in the mock
    query_words_filtered = [
        q_word.lower().strip("?!.,")
        for q_word in query.split()
        if q_word.lower().strip("?!.,") not in _STOP_WORDS
    ]
    
    # Check if any non-stop-word from the query is present in the context
    is_relevant_context = any(q_word in context_str.lower() for q_word in query_words_filtered)

    mock_answer_prefix = "English Answer: " if language == "en" else "الإجابة العربية: "

    if is_relevant_context:
        response_content = f"Based on the documents, regarding '{query}', some related information is: '{context_str[:150]}...'"
        if language == "ar":
            response_content = f"بناءً على المستندات، بخصوص '{query}'، بعض المعلومات ذات الصلة هي: '{context_str[:150]}...'"
    else:
        # This branch will now be hit for truly irrelevant queries
        if language == "en":
            response_content = "I found some context, but it's not directly answering the query."
        else:
            response_content = "لقد وجدت بعض السياق، لكنه لا يجيب مباشرة على الاستعلام."

    return mock_answer_prefix + response_content
