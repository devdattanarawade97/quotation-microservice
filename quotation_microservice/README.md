# Quotation Microservice

A FastAPI microservice that generates inspirational quotes using OpenAI's language models.

## Features

*   Generate quotes based on a specified topic and optional keywords.
*   Control quote length preference (short, medium, long).
*   RESTful API endpoint.
*   Containerized with Docker.

## Setup

1.  **Clone the repository (if applicable)**:
    ```bash
    git clone <repository-url>
    cd quotation_microservice
    ```

2.  **Create a virtual environment and install dependencies**:
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up OpenAI API Key**:
    Create a `.env` file in the `quotation_microservice` directory (or set directly in your environment) with your OpenAI API key:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
    You can copy `.env.example` as a template.

## Running the Microservice

### Locally

```bash
OPENAI_API_KEY=your_openai_api_key_here uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
(Replace `your_openai_api_key_here` with your actual key if not using a `.env` file).

Open your browser to `http://127.0.0.1:8000/docs` to see the API documentation.

### With Docker

1.  **Build the Docker image**:
    ```bash
    docker build -t quotation-microservice .
    ```

2.  **Run the Docker container**:
    ```bash
    docker run -d -p 8000:8000 --name quotation-app -e OPENAI_API_KEY=your_openai_api_key_here quotation-microservice
    ```
    (Replace `your_openai_api_key_here` with your actual key).

## API Endpoints

*   **GET `/`**: Welcome message.
*   **POST `/generate-quote`**: Generates an inspirational quote.
    *   **Request Body** (JSON):
        ```json
        {
            "topic": "happiness",
            "keywords": ["joy", "peace"],
            "length_preference": "medium" // "short", "medium", "long"
        }
        ```
    *   **Response Body** (JSON):
        ```json
        {
            "quote": "Happiness is not a destination, but a journey found in every moment of joy and peace."
        }
        ```

## Error Handling

*   `500 Internal Server Error`: If the OpenAI API key is missing or invalid, or if there's an issue communicating with the OpenAI API.

## Dependencies

*   FastAPI
*   Uvicorn
*   OpenAI Python Client
*   Pydantic Settings
*   Python Dotenv
