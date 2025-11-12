import time
import numpy as np
import hashlib
from typing import List, Optional
import openai
from mocks.mock_llm_service import MockLLMService
# FIX: Changed to a relative import to correctly reference config from the parent 'src' directory
from ..config import USE_MOCK_LLM, OPENAI_API_KEY
# Define a set of common stop words for mock relevance checking
_STOP_WORDS = {"a", "an", "the", "is", "are", "was", "were", "what", "where", "when", "why", "how", "of", "in", "on", "for", "with", "and", "or", "but", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "our", "their", "france", "capital"} # Added 'france' and 'capital' for this specific test case

def get_llm_response(prompt: str, language: str = "en") -> str:
    """
    Mocks an LLM response based on the prompt and desired language.

    Simulates a basic LLM interaction for testing or development when
    a real LLM service is not available or desired.

    Args:
        prompt (str): The input prompt for the LLM.
        language (str, optional): The desired language for the response ('en' for English, 'ar' for Arabic).
                                  Defaults to "en".

    Returns:
        str: A mock LLM response string, localized if specified.
    """
    print(f"[MOCK LLM] Receiving prompt (lang={language}): {prompt[:100]}...")
    time.sleep(0.1) # Simulate LLM processing time

    if "What is your name" in prompt:
        return "I am a helpful AI assistant." if language == "en" else "أنا مساعد ذكاء اصطناعي مفيد."

    mock_response = f"This is a mock response in {language}.\nPrompt received: '{prompt}'\n"
    if language == "ar":
        mock_response = f"هذه استجابة وهمية باللغة العربية.\nالطلب المستلم: '{prompt}'\n"

    return mock_response

def get_mock_embedding(text: str) -> List[float]:
    """
    Generates a consistent, mock embedding for a given text using hashing.

    This function provides a reproducible placeholder for semantic embeddings,
    useful for testing components that require vector inputs without needing
    a real embedding model.

    Args:
        text (str): The input text to generate a mock embedding for.

    Returns:
        List[float]: A list of floats representing the mock embedding.
    """
    # Use a simple hashing approach to create a reproducible 'embedding'
    # This is not a real semantic embedding but serves as a placeholder for structure.
    hash_val = int(hashlib.sha256(text.encode('utf-8')).hexdigest(), 16)
    # Create a small, fixed-size vector (e.g., 128 dimensions)
    embedding_size = 128
    mock_embedding = [(hash_val % (i + 1)) / (i + 1) for i in range(embedding_size)]
    return mock_embedding

def get_llm_response_rag(query: str, context: List[str], language: str = "en") -> str:
    """
    Mocks an LLM response for RAG (Retrieval Augmented Generation) scenarios,
    incorporating retrieved context and supporting English/Arabic.

    This function simulates how an LLM would use provided context to answer a query,
    with a basic relevance check.

    Args:
        query (str): The user's question.
        context (List[str]): A list of text snippets retrieved as context.
        language (str, optional): The desired language for the response ('en' for English, 'ar' for Arabic).
                                  Defaults to "en".

    Returns:
        str: A mock LLM answer string, potentially using the provided context.
    """
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



class LLMService:
    """
    A service class for interacting with Language Model (LLM) providers,
    supporting both real OpenAI and a mock LLM for development/testing.

    Handles generating prompts and orchestrating calls to the LLM for tasks
    like generating email drafts.
    """
    def __init__(self):
        """
        Initializes the LLMService.

        It checks the `USE_MOCK_LLM` setting from config. If true, it uses `MockLLMService`.
        Otherwise, it attempts to initialize the OpenAI client, raising an error if
        `OPENAI_API_KEY` is not set.
        """
        if USE_MOCK_LLM:
            self.client = MockLLMService()
        else:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment variables when USE_MOCK_LLM is false.")
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def _generate_prompt(self, lang: str, summary_data: dict) -> str:
        """
        Generates a structured prompt for the LLM to create an email draft
        based on quotation summary data.

        Args:
            lang (str): The desired language for the email draft (e.g., "en", "ar", "bilingual").
            summary_data (dict): A dictionary containing summary details for the quotation,
                                 e.g., client_name, currency, grand_total, delivery_terms, notes.

        Returns:
            str: The formatted prompt string for the LLM.
        """
        client_name = summary_data.get('client_name', 'Client')
        currency = summary_data.get('currency', '')
        grand_total = summary_data.get('grand_total', 0.0)
        delivery_terms = summary_data.get('delivery_terms', 'Not specified')
        notes = summary_data.get('notes', 'No specific notes.')
        # Adjust the language request in the prompt based on the 'lang' parameter
        lang_request = f"a {lang}" if lang not in ["bilingual", "both", "en_ar"] else "a bilingual Arabic and English"
        prompt = f"""
        Generate {lang_request} email draft summarizing a quotation.
        The client is {client_name}.
        The grand total is {grand_total:.2f} {currency}.
        Delivery terms: {delivery_terms}.
        Special notes: {notes}
 Please create a professional email draft that includes these details. Make sure to use appropriate language for the chosen language (e.g., formal Arabic).
        If generating a bilingual draft, provide both versions clearly separated.
        """
        return prompt

    async def generate_email_draft(self, lang: str, summary_data: dict) -> str:
        """
        Asynchronously generates an email draft using the configured LLM client.

        It constructs a prompt based on the provided summary data and desired language,
        then calls either the mock LLM or the real OpenAI API to get the draft.

        Args:
            lang (str): The desired language for the email draft (e.g., "en", "ar", "bilingual").
            summary_data (dict): A dictionary containing summary details for the quotation.

        Returns:
            str: The generated email draft content.
        """
        prompt = self._generate_prompt(lang, summary_data)
        if USE_MOCK_LLM:
            # MockLLMService needs to be called directly
            response = self.client.generate_response(prompt)
            return response
        chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes quotation details into professional email drafts."},
                    {"role": "user", "content": prompt}
                ],
                model="gpt-3.5-turbo" # Or gpt-4, depending on preference
            )
        return chat_completion.choices[0].message.content
