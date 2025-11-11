from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

# Initialize FastAPI app
app = FastAPI(
    title="Quotation Microservice",
    description="A microservice to generate inspirational quotes using OpenAI."
)

# Pydantic model for request body
class QuoteRequest(BaseModel):
    topic: str
    keywords: list[str] = []
    length_preference: str = "medium" # e.g., 'short', 'medium', 'long'

# Initialize OpenAI client
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    client = OpenAI(api_key=api_key)
except ValueError as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None # Set client to None to handle errors later

@app.post("/generate-quote", summary="Generate an inspirational quote")
async def generate_quote(request: QuoteRequest):
    """Generates an inspirational quote based on the provided topic, keywords, and length preference."""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized. Check API key.")

    # Construct the prompt for OpenAI
    prompt_parts = [
        f"Generate an inspirational quote about the topic: {request.topic}."
    ]
    if request.keywords:
        prompt_parts.append(f"Incorporate these keywords: {', '.join(request.keywords)}.")
    
    prompt_parts.append(f"The quote should be {request.length_preference} in length. Ensure the output is only the quote itself, without any introductory or concluding remarks.")

    full_prompt = " ".join(prompt_parts)

    try:
        # Call OpenAI API
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or gpt-4, depending on availability and cost
            messages=[
                {"role": "system", "content": "You are a wise philosopher and poet, expert in crafting concise and impactful inspirational quotes."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )

        quote = chat_completion.choices[0].message.content.strip()
        return {"quote": quote}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quote: {e}")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to the Quotation Microservice. Visit /docs for API documentation."}
