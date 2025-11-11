import openai
from mocks.mock_llm_service import MockLLMService
from config import USE_MOCK_LLM, OPENAI_API_KEY


class LLMService:
    def __init__(self):
        if USE_MOCK_LLM:
            self.client = MockLLMService()
        else:
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment variables when USE_MOCK_LLM is false.")
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def _generate_prompt(self, lang: str, summary_data: dict) -> str:
        client_name = summary_data.get('client_name', 'Client')
        currency = summary_data.get('currency', '')
        grand_total = summary_data.get('grand_total', 0.0)
        delivery_terms = summary_data.get('delivery_terms', 'Not specified')
        notes = summary_data.get('notes', 'No specific notes.')

        prompt = f"""
        Generate a {lang} email draft summarizing a quotation.
        The client is {client_name}.
        The grand total is {grand_total:.2f} {currency}.
        Delivery terms: {delivery_terms}.
        Special notes: {notes}

        Please create a professional email draft that includes these details. Make sure to use appropriate language for the chosen language (e.g., formal Arabic).
        """
        return prompt

    async def generate_email_draft(self, lang: str, summary_data: dict) -> str:
        prompt = self._generate_prompt(lang, summary_data)

        if USE_MOCK_LLM:
            # MockLLMService needs to be called directly
            response = self.client.generate_response(prompt)
            return response
        else:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes quotation details into professional email drafts."},
                    {"role": "user", "content": prompt}
                ],
                model="gpt-3.5-turbo" # Or gpt-4, depending on preference
            )
            return chat_completion.choices[0].message.content
