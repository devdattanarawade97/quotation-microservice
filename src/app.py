from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
# FIX: Added Tuple to the import from typing
from typing import List, Optional, Tuple
# FIX: Changed to a relative import to correctly reference llm_utils within the 'src' package
from .services.llm_utils import LLMService
import asyncio

# --- Pydantic Models for Request and Response ---
class ClientInfo(BaseModel):
    name: str
    contact: str
    lang: str = "en" # Default language for client communication

class LineItem(BaseModel):
    sku: str
    qty: int = Field(..., gt=0) # Quantity must be greater than 0
    unit_cost: float = Field(..., gt=0) # Unit cost must be greater than 0
    margin_pct: float = Field(default=20.0, ge=0, le=100) # Margin percentage between 0 and 100

class QuoteRequest(BaseModel):
    client: ClientInfo
    currency: str = "SAR"
    items: List[LineItem] = Field(..., min_length=0) # Allow empty items list
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None

class QuoteLineItemResponse(BaseModel):
    sku: str
    qty: int
    unit_cost: float
    margin_pct: float
    price_per_unit: float
    price_per_line: float

class QuoteResponse(BaseModel):
    client_name: str
    client_contact: str
    client_lang: str
    currency: str
    line_items: List[QuoteLineItemResponse]
    subtotal: float
    grand_total: float
    delivery_terms: Optional[str]
    notes: Optional[str]
    email_draft_en: Optional[str] # Field for English email draft
    email_draft_ar: Optional[str] # Field for Arabic email draft

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Quotation Microservice",
    description="Generates quotations and email drafts based on provided product data.",
    version="0.1.0",
)

# Initialize LLMService outside the route function to reuse the client
llm_service = LLMService()

# --- Utility Functions ---
def calculate_line_item_prices(item: LineItem) -> Tuple[float, float]:
    """Calculates price per unit and price per line with margin."""
    price_per_unit = item.unit_cost * (1 + item.margin_pct / 100)
    price_per_line = price_per_unit * item.qty
    return round(price_per_unit, 2), round(price_per_line, 2)

# --- API Endpoints ---
@app.post("/quote", response_model=QuoteResponse)
async def create_quote(request: QuoteRequest):
    """
    Generates a detailed quotation including line item calculations and
    an LLM-powered email draft for the client.
    """
    if not request.items:
        # Handle cases with no items, setting totals to 0 and providing generic email drafts
        summary_data = {
            "client_name": request.client.name,
            "currency": request.currency,
            "grand_total": 0.0,
            "delivery_terms": request.delivery_terms if request.delivery_terms else "Not specified",
            "notes": request.notes if request.notes else "No specific notes."
        }
        # Generate bilingual email draft for empty items
        email_draft_bilingual = await llm_service.generate_email_draft("bilingual", summary_data)

        return QuoteResponse(
            client_name=request.client.name,
            client_contact=request.client.contact,
            client_lang=request.client.lang,
            currency=request.currency,
            line_items=[],
            subtotal=0.0,
            grand_total=0.0,
            delivery_terms=request.delivery_terms,
            notes=request.notes,
            email_draft_en=email_draft_bilingual, # Both fields get the bilingual draft
            email_draft_ar=email_draft_bilingual
        )

    line_items_response = []
    subtotal = 0.0

    for item in request.items:
        price_per_unit, price_per_line = calculate_line_item_prices(item)
        line_items_response.append(
            QuoteLineItemResponse(
                sku=item.sku,
                qty=item.qty,
                unit_cost=item.unit_cost,
                margin_pct=item.margin_pct,
                price_per_unit=price_per_unit,
                price_per_line=price_per_line,
            )
        )
        subtotal += price_per_line

    grand_total = round(subtotal, 2)

    # Prepare data for LLM
    summary_data = {
        "client_name": request.client.name,
        "currency": request.currency,
        "grand_total": grand_total,
        "delivery_terms": request.delivery_terms if request.delivery_terms else "Not specified",
        "notes": request.notes if request.notes else "No specific notes."
    }

    # Asynchronously generate email drafts
    # Request a bilingual draft, as the mock LLM is set up to provide it
    email_draft_bilingual = await llm_service.generate_email_draft("bilingual", summary_data)


    return QuoteResponse(
        client_name=request.client.name,
        client_contact=request.client.contact,
        client_lang=request.client.lang,
        currency=request.currency,
        line_items=line_items_response,
        subtotal=subtotal,
        grand_total=grand_total,
        delivery_terms=request.delivery_terms,
        notes=request.notes,
        email_draft_en=email_draft_bilingual, # Both fields receive the same bilingual mock draft
        email_draft_ar=email_draft_bilingual
    )

