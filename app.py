import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(
    title="Quotation Microservice",
    description="A microservice to generate quotations using OpenAI.",
    version="1.0.0"
)

# --- Health Check Endpoint ---
@app.get("/", summary="Health Check", response_description="Returns a simple health message.")
async def read_root():
    return {"message": "Quotation Microservice is running!"}

# --- OpenAI Client Initialization ---
# The API key will be loaded from the OPENAI_API_KEY environment variable.
# Ensure this variable is set in your environment (e.g., .env file, Docker).
openai_client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    openai_client = OpenAI(api_key=api_key)
except ValueError as e:
    print(f"Error initializing OpenAI client: {e}")
    # In a real application, you might want to handle this more gracefully,
    # perhaps by making the /generate-quote endpoint unavailable if the client can't initialize.

# --- Request Body Model ---
class QuoteRequest(BaseModel):
    prompt: str

# --- Quote Generation Endpoint ---
@app.post("/generate-quote", summary="Generate a Quotation", response_description="Returns a generated quotation from OpenAI.")
async def generate_quote(request: QuoteRequest):
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized. Check OPENAI_API_KEY.")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Or another suitable model like gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates insightful and inspiring quotations based on user prompts."},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=150, # Limit the length of the quotation
            temperature=0.7 # Control creativity
        )
        quote = response.choices[0].message.content.strip()
        return {"quote": quote}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quote: {e}")
