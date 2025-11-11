import time
import numpy as np
import hashlib
from typing import List, Optional

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

    # Simulate a basic RAG response by combining query and context in a simple way
    # In a real LLM, this prompt would be sent to the model.
    mock_answer_prefix = "English Answer: " if language == "en" else "الإجابة العربية: "

    # For a mock, just acknowledge the context and try to relate to the query simply
    if any(q_word.lower() in context_str.lower() for q_word in query.split()):
        response_content = f"Based on the documents, regarding '{query}', some related information is: '{context_str[:150]}...'"
        if language == "ar":
            response_content = f"بناءً على المستندات، بخصوص '{query}'، بعض المعلومات ذات الصلة هي: '{context_str[:150]}...'"
    else:
        response_content = f"I found some context, but it's not directly answering '{query}'. Context: '{context_str[:150]}'"
        if language == "ar":
            response_content = f"لقد وجدت بعض السياق، لكنه لا يجيب مباشرة على '{query}'. السياق: '{context_str[:150]}'"

    return mock_answer_prefix + response_content
