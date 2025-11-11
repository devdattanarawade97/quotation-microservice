from fastapi.testclient import TestClient
from app import app
from unittest.mock import patch

# Patch config for testing to ensure mock LLM is used
@patch('config.USE_MOCK_LLM', True)
@patch('config.OPENAI_API_KEY', None)
def test_create_quote_success():
    client = TestClient(app)
    request_payload = {
        "client": {"name": "Gulf Eng.", "contact": "omar@client.com", "lang": "en"},
        "currency": "SAR",
        "items": [
            {"sku": "ALR-SL-90W", "qty": 120, "unit_cost": 240.0, "margin_pct": 22},
            {"sku": "ALR-OBL-12V", "qty": 40, "unit_cost": 95.5, "margin_pct": 18}
        ],
        "delivery_terms": "DAP Dammam, 4 weeks",
        "notes": "Client asked for spec compliance with Tarsheed."
    }

    response = client.post("/quote", json=request_payload)
    assert response.status_code == 200
    response_data = response.json()

    # Test calculations
    assert response_data["client_name"] == "Gulf Eng."
    assert response_data["currency"] == "SAR"
    assert len(response_data["line_items"]) == 2
    assert response_data["line_items"][0]["sku"] == "ALR-SL-90W"
    # 240 * (1 + 0.22) * 120 = 240 * 1.22 * 120 = 35136
    assert response_data["line_items"][0]["price_per_line"] == 35136.0
    assert response_data["line_items"][1]["sku"] == "ALR-OBL-12V"
    # 95.5 * (1 + 0.18) * 40 = 95.5 * 1.18 * 40 = 4504.4
    assert response_data["line_items"][1]["price_per_line"] == 4504.4

    # Grand total = 35136 + 4504.4 = 39640.4
    assert response_data["grand_total"] == 39640.4
    assert "DAP Dammam" in response_data["delivery_terms"]

    # Test mock LLM response
    assert "Mock LLM response for English" in response_data["email_draft_en"]
    assert "Mock LLM response for Arabic" in response_data["email_draft_ar"]
    assert "Gulf Eng." in response_data["email_draft_en"]
    assert "39640.40 SAR" in response_data["email_draft_en"]
    assert "DAP Dammam, 4 weeks" in response_data["email_draft_en"]
    assert "Tarsheed" in response_data["email_draft_en"]
    
@patch('config.USE_MOCK_LLM', True)
@patch('config.OPENAI_API_KEY', None)
def test_create_quote_empty_items():
    client = TestClient(app)
    request_payload = {
        "client": {"name": "Test Client", "contact": "test@client.com", "lang": "en"},
        "currency": "USD",
        "items": [],
        "delivery_terms": "FOB Port",
        "notes": ""
    }
    response = client.post("/quote", json=request_payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["grand_total"] == 0.0
    assert len(response_data["line_items"]) == 0
    assert "Mock LLM response for English" in response_data["email_draft_en"]
