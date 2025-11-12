"""
This module implements a FastAPI microservice for generating quotations and email drafts.

It handles client requests for quotations, calculates line item prices including margins,
and uses an LLM service to generate professional email drafts in English and Arabic.
Pydantic models are used for request validation and response serialization.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
# FIX: Added Tuple to the import from typing
from typing import List, Optional, Tuple
# FIX: Changed to a relative import to correctly reference llm_utils within the 'src' package
from .services.llm_utils import LLMService
import asyncio

# --- Pydantic Models for Request and Response ---
class ClientInfo(BaseModel):
    """
    Pydantic model for client information.
    """
    name: str = Field(..., description="The name of the client company or contact person.")
    contact: str = Field(..., description="The contact email address or phone number of the client.")
    lang: str = Field("en", description="The preferred language for client communication (e.g., 'en', 'ar'). Defaults to 'en'.")

class LineItem(BaseModel):
    """
    Pydantic model for a single line item in a quotation request.
    """
    sku: str = Field(..., description="The Stock Keeping Unit (SKU) or product identifier.")
    qty: int = Field(..., gt=0, description="The quantity of the item requested. Must be greater than 0.")
    unit_cost: float = Field(..., gt=0, description="The base cost of a single unit of the item. Must be greater than 0.")
    margin_pct: float = Field(default=20.0, ge=0, le=100, description="The desired profit margin percentage for the item (0-100). Defaults to 20.0.")

class QuoteRequest(BaseModel):
    """
    Pydantic model for the incoming quotation request payload.
    """
    client: ClientInfo = Field(..., description="Information about the client requesting the quote.")
    currency: str = Field("SAR", description="The currency for the quotation (e.g., 'SAR', 'USD'). Defaults to 'SAR'.")
    items: List[LineItem] = Field(..., min_length=0, description="A list of line items included in the quotation. Can be empty.")
    delivery_terms: Optional[str] = Field(None, description="Optional delivery terms for the quotation (e.g., 'DAP Dammam, 4 weeks').")
    notes: Optional[str] = Field(None, description="Optional special notes or client requirements for the quotation.")

class QuoteLineItemResponse(BaseModel):
    """
    Pydantic model for a single line item in the quotation response,
    including calculated prices.
    """
    sku: str = Field(..., description="The Stock Keeping Unit (SKU) or product identifier.")
    qty: int = Field(..., description="The quantity of the item.")
    unit_cost: float = Field(..., description="The base cost of a single unit.")
    margin_pct: float = Field(..., description="The profit margin percentage applied.")
    price_per_unit: float = Field(..., description="The final price per unit after applying margin.")
    price_per_line: float = Field(..., description="The total price for this line item (price_per_unit * qty).")

class QuoteResponse(BaseModel):
    """
    Pydantic model for the comprehensive quotation response returned by the API.
    """
    client_name: str = Field(..., description="The name of the client.")
    client_contact: str = Field(..., description="The contact information for the client.")
    client_lang: str = Field(..., description="The preferred language for the client.")
    currency: str = Field(..., description="The currency of the quotation.")
    line_items: List[QuoteLineItemResponse] = Field(..., description="A list of processed line items with calculated prices.")
    subtotal: float = Field(..., description="The sum of all line item prices before any potential overall discounts/taxes.")
    grand_total: float = Field(..., description="The final total amount of the quotation.")
    delivery_terms: Optional[str] = Field(None, description="The delivery terms specified in the request.")
    notes: Optional[str] = Field(None, description="Any special notes included in the request.")
    email_draft_en: Optional[str] = Field(None, description="The generated English email draft summarizing the quotation.")
    email_draft_ar: Optional[str] = Field(None, description="The generated Arabic email draft summarizing the quotation.")

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
    """
    Calculates the final price per unit and total price per line item, including the specified margin.

    Args:
        item (LineItem): A Pydantic LineItem object containing SKU, quantity, unit cost, and margin percentage.

    Returns:
        Tuple[float, float]: A tuple containing two floats:
                             - The calculated price per unit (after margin).
                             - The calculated total price for the line item (price_per_unit * qty).
    """
    price_per_unit = item.unit_cost * (1 + item.margin_pct / 100)
    price_per_line = price_per_unit * item.qty
    return round(price_per_unit, 2), round(price_per_line, 2)

# --- API Endpoints ---
@app.post("/quote", response_model=QuoteResponse)
async def create_quote(request: QuoteRequest):
    """
    Generates a detailed quotation and an LLM-powered email draft for the client.

    This endpoint accepts a `QuoteRequest` payload, calculates the prices for
    each line item based on unit cost and margin, sums them up for a grand total,
    and then uses an LLM service to generate a summary email draft for the client
    in both English and Arabic.

    Args:
        request (QuoteRequest): The incoming request containing client info, currency,
                                line items, delivery terms, and notes.

    Returns:
        QuoteResponse: A comprehensive response object containing all calculated
                       quotation details and the generated email drafts.

    Raises:
        HTTPException: If any required data is missing or invalid (handled by Pydantic).
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

