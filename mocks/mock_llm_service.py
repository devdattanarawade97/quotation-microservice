import json
import re
from typing import Dict, Any

class MockLLMService:
    def __init__(self):
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
        print(f"[MOCK LLM] Extracting fields for subject: '{subject}'")
        # Use a simple regex or direct lookup for mock extraction based on example email
        if "RFQ — Streetlight Poles" in subject:
            # Example extraction logic based on the provided email sample
            product_match = re.search(r'quote (\d+ pcs .*?)', body, re.IGNORECASE)
            quantity_match = re.search(r'quote (\d+ pcs)', body, re.IGNORECASE)
            location_match = re.search(r'Needed in (\w+) within', body, re.IGNORECASE)
            delivery_match = re.search(r'within (\d+ weeks)', body, re.IGNORECASE)
            contact_name_match = re.search(r'Regards, (.*?)(?:, \+9665|$) ', body)
            contact_email_match = re.search(r'(\S+@\S+\.\S+)', body)
            contact_phone_match = re.search(r'\+9665(\d+)', body)

            return {
                "product": product_match.group(1).replace(quantity_match.group(1), '').strip() if product_match and quantity_match else "N/A",
                "quantity": quantity_match.group(1) if quantity_match else "N/A",
                "location": location_match.group(1) if location_match else "N/A",
                "delivery_time": delivery_match.group(1) if delivery_match else "N/A",
                "contact_person": contact_name_match.group(1).strip() if contact_name_match else "N/A",
                "contact_email": contact_email_match.group(1) if contact_email_match else "N/A",
                "contact_phone": f"({contact_phone_match.group(0)})" if contact_phone_match else "N/A" # Reconstruct full number for clarity
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
