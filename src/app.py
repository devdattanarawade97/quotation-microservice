from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from services.llm_utils import LLMService

app = FastAPI(
    title="Quotation Microservice",
    description="API for generating quotations and email drafts."
)

# --- Pydantic Models for Request ---
class Client(BaseModel):
    name: str
    contact: str
    lang: str = "en"  # 'en' for English, 'ar' for Arabic

class Item(BaseModel):
    sku: str
    qty: int = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)
    margin_pct: float = Field(..., ge=0, le=100) # Percentage from 0 to 100

class QuoteRequest(BaseModel):
    client: Client
    currency: str
    items: List[Item]
    delivery_terms: str
    notes: Optional[str] = None

# --- Pydantic Models for Response ---
class LineItemResponse(BaseModel):
    sku: str
    qty: int
    unit_cost: float
    margin_pct: float
    price_per_line: float

class QuoteResponse(BaseModel):
    client_name: str
    currency: str
    line_items: List[LineItemResponse]
    grand_total: float
    delivery_terms: str
    notes: Optional[str]
    email_draft_en: str
    email_draft_ar: str

# --- LLM Service Instance ---
llm_service = LLMService()

@app.post("/quote", response_model=QuoteResponse)
async def create_quote(request: QuoteRequest):
    line_items_response = []
    grand_total = 0.0

    for item in request.items:
        # price per line = unit_cost × (1 + margin_pct%) × qty
        margin_multiplier = 1 + (item.margin_pct / 100)
        price_per_line = round(item.unit_cost * margin_multiplier * item.qty, 2)
        grand_total += price_per_line

        line_items_response.append(LineItemResponse(
            sku=item.sku,
            qty=item.qty,
            unit_cost=item.unit_cost,
            margin_pct=item.margin_pct,
            price_per_line=price_per_line
        ))

    grand_total = round(grand_total, 2)

    # Prepare data for LLM
    summary_data = {
        "client_name": request.client.name,
        "currency": request.currency,
        "grand_total": grand_total,
        "delivery_terms": request.delivery_terms,
        "notes": request.notes
    }

    # Generate email drafts using the LLM service
    email_draft_en = await llm_service.generate_email_draft(lang="English", summary_data=summary_data)
    email_draft_ar = await llm_service.generate_email_draft(lang="Arabic", summary_data=summary_data)

    return QuoteResponse(
        client_name=request.client.name,
        currency=request.currency,
        line_items=line_items_response,
        grand_total=grand_total,
        delivery_terms=request.delivery_terms,
        notes=request.notes,
        email_draft_en=email_draft_en,
        email_draft_ar=email_draft_ar
    )

