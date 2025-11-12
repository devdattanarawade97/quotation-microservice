import json
import re
from typing import Dict, Any

class MockLLMService:
    """
    A mock service simulating a Large Language Model (LLM) for text extraction and generation.

    This service provides predefined or simple regex-based responses for extracting fields
    from text and generating mock email drafts.
    """
    def __init__(self):
        """
        Initializes the MockLLMService with predefined mock responses.
        """
        self.mock_responses = {
            "RFQ — Streetlight Poles": {
                "product": "streetlight model ALR-SL-90W",
                "quantity": "120 pcs",
                "location": "Dammam",
                "delivery_time": "4 weeks",
                "contact_person": "Eng. Omar",
                "contact_email": "omar@client.com",
                "contact_phone": "+9665XXXX"
            }
        }
    
    def extract_fields(self, subject: str, body: str) -> Dict[str, Any]:
        """
        Simulates an LLM extracting key fields from an email subject and body.

        For specific subjects (e.g., "RFQ — Streetlight Poles"), it uses regex
        to parse the body and return structured data. Otherwise, it returns
        default "N/A" values.

        Args:
            subject (str): The subject line of the email.
            body (str): The body content of the email.

        Returns:
            Dict[str, Any]: A dictionary containing extracted fields like product,
                            quantity, location, contact info, etc.
        """
        print(f"[MOCK LLM] Extracting fields for subject: '{subject}'")
        if "RFQ — Streetlight Poles" in subject:
            # Updated regex patterns for more accurate extraction
            product_match = re.search(r'quote \d+ pcs (.*?)(?:\. Needed in|\n)', body, re.IGNORECASE)
            quantity_match = re.search(r'quote (\d+ pcs)', body, re.IGNORECASE)
            location_match = re.search(r'Needed in (\w+) within', body, re.IGNORECASE)
            delivery_match = re.search(r'within (\d+ weeks)', body, re.IGNORECASE)
            # Improved regex for contact person, looking before email/phone
            contact_name_match = re.search(r'Regards,\s*(.*?)(?:,\s*\+9665|\s*,\s*\S+@\S+\.\S+|\n|$)', body, re.IGNORECASE)
            contact_email_match = re.search(r'(\S+@\S+\.\S+)', body)
            contact_phone_match = re.search(r'\+9665(\d{8})', body) # Assuming 8 digits after +9665

            return {
                "product": product_match.group(1).strip() if product_match else "N/A",
                "quantity": quantity_match.group(1) if quantity_match else "N/A",
                "location": location_match.group(1) if location_match else "N/A",
                "delivery_time": delivery_match.group(1) if delivery_match else "N/A",
                "contact_person": contact_name_match.group(1).strip() if contact_name_match else "N/A",
                "contact_email": contact_email_match.group(1) if contact_email_match else "N/A",
                "contact_phone": contact_phone_match.group(0) if contact_phone_match else "N/A" # Keep full matched phone for clarity
            }
        
        print("[MOCK LLM] No specific mock response found for this subject. Returning empty dict.")
        return {
            "product": "N/A",
            "quantity": "N/A",
            "location": "N/A",
            "delivery_time": "N/A",
            "contact_person": "N/A",
            "contact_email": "N/A",
            "contact_phone": "N/A"
        }

    def generate_response(self, prompt: str) -> str:
        """
        Generates a mock response based on the prompt, simulating an LLM email draft.
        This version always generates a single, combined bilingual (English and Arabic) draft.

        It parses key information (client name, grand total, delivery terms, notes)
        from the prompt to construct a semi-realistic, formatted email draft.

        Args:
            prompt (str): The prompt text used to guide the LLM's response generation.

        Returns:
            str: A combined bilingual (English and Arabic) mock email draft.
        """
        print(f"[MOCK LLM] Generating mock bilingual response for prompt:\n---\n{prompt}\n---")

        # Extract summary data from prompt for more realistic mock
        client_name_match = re.search(r'The client is (.*?)\.', prompt)
        client_name = client_name_match.group(1) if client_name_match else "Client"

        grand_total_match = re.search(r'The grand total is (\d+\.\d{2} \w+)\.', prompt)
        grand_total = grand_total_match.group(1) if grand_total_match else "0.00 CUR"

        delivery_terms_match = re.search(r'Delivery terms: (.*?)\.', prompt)
        delivery_terms = delivery_terms_match.group(1) if delivery_terms_match else "Not specified"

        notes_match = re.search(r'Special notes: (.*?)(?:\n|$)', prompt, re.DOTALL)
        notes = notes_match.group(1).strip() if notes_match else "No specific notes."

        # Construct the mock response with both English and Arabic content
        english_part = (
            f"Mock LLM response for English:\n\n"
            f"Dear {client_name},\n\n"
            f"Please find below the summary of your quotation:\n"
            f"Grand Total: {grand_total}\n"
            f"Delivery Terms: {delivery_terms}\n"
            f"Notes: {notes}\n\n"
            f"We look forward to your business.\n"
            f"Sincerely,\n"
            f"Quotation Team"
        )

        arabic_part = (
            f"استجابة نموذج اللغة الكبيرة الوهمية للغة العربية:\n\n"
            f"عزيزي {client_name},\n\n"
            f"تجدون أدناه ملخص عرض الأسعار الخاص بكم:\n"
            f"الإجمالي الكلي: {grand_total}\n"
            f"شروط التسليم: {delivery_terms}\n"
            f"ملاحظات خاصة: {notes}\n\n"
            f"نتطلع إلى عملكم معنا.\n"
            f"مع خالص التقدير،\n"
            f"فريق عروض الأسعار"
        )

        # Combine both into a single bilingual draft with a clear separator
        bilingual_draft = f"{english_part}\n\n---\n\n{arabic_part}"

        return bilingual_draft

