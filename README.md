
# Repo Pilot Project Documentation

## Project Overview
Welcome to the Repo Pilot project documentation! This system is designed as a sophisticated automation hub, demonstrating capabilities across multiple critical business functions. It handles everything from automating Request for Quotation (RFQ) processing, generating dynamic quotations, to maintaining a robust Retrieval Augmented Generation (RAG) knowledge base for both English and Arabic content. The project leverages Python, FastAPI, and integrates with Large Language Models (LLMs) for intelligent data processing and response generation, utilizing mock services for development and testing flexibility.

## Directory Structure
Our project follows a standard and professional directory structure to enhance maintainability, scalability, and clarity.

```
.
├── .gitignore             # Standard file: Specifies intentionally untracked files to ignore.
├── README.md              # Project documentation/overview (this file).
├── Dockerfile             # Essential for containerization.
├── requirements.txt       # Python dependencies.
├── src/                   # Core application source code
│   ├── __init__.py        # Makes 'src' a Python package.
│   ├── app.py             # Main application entry point / FastAPI app.
│   ├── config.py          # Application configuration.
│   ├── services/          # Business logic and external integrations
│   │   ├── __init__.py
│   │   ├── email_parser.py
│   │   ├── llm_utils.py
│   │   ├── process_rfq_email.py
│   │   ├── rag_core.py
│   │   └── rag_service.py
│   └── utils/             # (Optional) For general utility functions not specific to a service
│       └── ...
├── tests/                 # All unit, integration, and end-to-end tests
│   ├── __init__.py
│   ├── test_app.py
│   ├── test_task_1.py
│   └── test_task_3.py
├── data/                  # Static data, templates, or input files
│   ├── auto_reply_sample.txt
│   ├── document1_en.txt
│   └── document2_ar.txt
├── docs/                  # Project-specific documentation, guides, or generated reports
│   ├── Repo-Pilot-Response-readme-doc-2025-11-12.docx
│   ├── Repo-Pilot-Response-test-2025-11-12.docx
│   ├── Repo-Pilot-Response-test-doc-2025-11-12.docx
│   ├── Task 1 — RFQ → CRM Automation-2025-11-12.docx
│   ├── Task 2 — Quotation Microservice (Python + OpenAI)-2025-11-12.docx
│   └── Task 3 — RAG Knowledge Base-2025-11-12.docx
├── logs/                  # Application runtime logs
│   ├── crm_mock_log.json
│   ├── internal_alert_log.txt
│   ├── mock_sheets_log.json
│   └── test_output.log
├── mocks/                 # Mock implementations for external services or data
│   ├── mock_alert_sender.py
│   ├── mock_email_sender.py
│   ├── mock_google_drive.py
│   ├── mock_google_sheets.py
│   ├── mock_llm_service.py
│   └── mock_salesforce_crm.py
├── mock_drive_folder/     # Specific mock data for Google Drive interactions
│   └── RFQ_2025-11-11/
│       └── specs.pdf
```

### Rationale for Key Changes:

*   **`src/`:** This is a common practice for larger projects. It clearly separates the primary source code from configuration, tests, documentation, and other project-level files.
*   **`tests/`:** Consolidating all tests into one place makes them easy to find and run.
*   **`docs/`:** Provides a clear home for all project documentation, keeping it distinct from source code.
*   **`logs/`:** A dedicated directory for logs is crucial for monitoring and debugging, preventing clutter in the root directory.
*   **`data/`:** For any static data files, samples, or templates that the application might use.
*   **Root Level:** Only essential project configuration files like `Dockerfile` and `requirements.txt` (and common ones like `.gitignore`, `README.md`) remain at the top level.

## Task 1: RFQ → CRM Automation

### Explanation:
This system is designed to automatically process incoming Request for Quotation (RFQ) emails, extract important information from them, and then use that information to update various business systems, send replies, and trigger internal notifications. Essentially, it's automating the initial steps of handling an RFQ.

#### 1. `services/email_parser.py`: The Email Translator
*   **What it does:** This file contains a class called `EmailParser` which acts like an email translator.
    *   `parse_email` method: Its main job is to take a raw, unreadable email (like the ones mail servers deal with) and break it down into understandable pieces: the subject, who sent it, the plain text body, the HTML body (if any), and any attachments. It turns a complex email into a neat dictionary of information.
    *   `create_mock_email` method: This is a utility function specifically used for testing. It can build a fake email from scratch (with a subject, body, sender, and attachments) so that the `parse_email` method and the rest of the system can be tested without needing a real email server.
*   **Data Flow:**
    *   **Input to `parse_email`:** Raw email content (bytes).
    *   **Output from `parse_email`:** A Python dictionary containing structured email data (subject, sender, bodyplain, bodyhtml, attachments). This dictionary is then used by `app.py`.
    *   **Input to `create_mock_email`:** Structured data like subject, body, sender, attachment details.
    *   **Output from `create_mock_email`:** Raw email content (bytes), which mimics a real incoming email for testing.

#### 2. `src/app.py`: The RFQ Processing Orchestrator
This is the central brain of the system, specifically the `process_rfq_email` function. It takes the parsed email information and directs it to different "mock" services (which simulate real-world services like Google Sheets, Salesforce, etc., for development and testing).

Here's the step-by-step data flow within the `process_rfq_email` function:

1.  **Parse Email:**
    *   **What happens:** The `process_rfq_email` function first calls `email_parser.parse_email()` (from `src/services/email_parser.py`) to convert the incoming raw email into a structured dictionary.
    *   **Data Flow:**
        *   **Input:** `raw_email_content` (the entire email as bytes).
        *   **Output:** `parsed_email` dictionary (containing subject, sender, bodyplain, attachments, etc.).
2.  **Extract Fields using LLM (Large Language Model):**
    *   **What happens:** The system then sends the subject and bodyplain of the email to a (mock) LLM service to intelligently pull out specific details like product name, quantity, location, contact person, etc.
    *   **Data Flow:**
        *   **Input:** `subject` and `bodyplain` from the `parsed_email`.
        *   **Processed by:** `mocks/mock_llm_service.py` (which simulates a real LLM).
        *   **Output:** `extracted_fields` dictionary (e.g., `{'product': 'Streetlight Poles', 'quantity': '120 pcs', ...}`).
3.  **Write Row to Google Sheets:**
    *   **What happens:** If the mock Google Sheets service is enabled, the parsed and extracted information is formatted into a new row and added to a spreadsheet.
    *   **Data Flow:**
        *   **Input:** `subject`, `sender`, and `extracted_fields`.
        *   **Processed by:** `mocks/mock_google_sheets.py`.
        *   **Output/Effect:** A new entry is added to `logs/mock_sheets_log.json`, simulating writing a row to a Google Sheet.
4.  **Create Opportunity in Salesforce CRM:**
    *   **What happens:** If the mock Salesforce CRM service is enabled, a new sales opportunity is created in the CRM system using the extracted details.
    *   **Data Flow:**
        *   **Input:** `extracted_fields` (to build the opportunity name and description).
        *   **Processed by:** `mocks/mock_salesforce_crm.py`.
        *   **Output/Effect:** A new entry is added to `logs/crm_mock_log.json`, simulating the creation of a CRM opportunity.
5.  **Archive Attachments to Google Drive:**
    *   **What happens:** If there are attachments in the email and the mock Google Drive service is enabled, these attachments are saved into a specific folder structure on Google Drive.
    *   **Data Flow:**
        *   **Input:** `filename` and `payload` (the actual content of the attachment) from the `parsed_email['attachments']`.
        *   **Processed by:** `mocks/mock_google_drive.py`.
        *   **Output/Effect:** Files are created within the `mock_drive_folder/RFQYYYY-MM-DD/` directory, simulating archiving to Google Drive.
6.  **Auto-reply to Client:**
    *   **What happens:** If the mock email sender is enabled and a `contact_email` was extracted, an automated "Thank you for your inquiry" email is sent back to the client.
    *   **Data Flow:**
        *   **Input:** `contact_email` (from `extracted_fields`), `subject` (from parsed email), and a pre-defined reply body.
        *   **Processed by:** `mocks/mock_email_sender.py`.
        *   **Output/Effect:** The content of the auto-reply is saved to `data/auto_reply_sample.txt`, simulating sending an email.
7.  **Post Internal Alert (Slack/Teams):**
    *   **What happens:** If the mock alert sender is enabled, a notification about the new RFQ is sent to an internal channel (like a Slack or Teams channel) so that the team is aware.
    *   **Data Flow:**
        *   **Input:** A formatted `alert_message` using `subject`, `sender`, and `extracted_fields`.
        *   **Processed by:** `mocks/mock_alert_sender.py`.
        *   **Output/Effect:** The alert message is appended to `logs/internal_alert_log.txt`, simulating an internal alert.

#### 3. Supporting Files:
*   `src/config.py`: This file holds important settings. Crucially, it has flags like `MOCK_LLM_ENABLED`, `MOCK_GOOGLE_SHEETS_ENABLED`, etc., which determine whether the `app.py` script uses the mock services or would, in a real setup, connect to actual external services.
*   `mocks/` directory: This folder contains all the "fake" versions of real services (LLM, Google Sheets, Salesforce, Google Drive, Email Sender, Alert Sender). They are designed to mimic the behavior of the real services by writing logs to local files instead of interacting with external APIs. This is essential for developing and testing the `app.py` logic without needing actual API keys or live accounts.
*   `requirements.txt`: Lists all the Python libraries (like `email`) needed for this project to run.
*   `Dockerfile`: Instructions for building a containerized version of this application, making it easy to deploy consistently.
*   `if __name__ == "__main__":` block in `src/app.py`: This block provides a runnable example. It creates a mock email using `email_parser.create_mock_email()` and then calls `process_rfq_email()` with this mock email, demonstrating the entire flow. It also prints messages to guide you on where to look for the output of the mock services (e.g., `logs/mock_sheets_log.json`, `logs/crm_mock_log.json`).

In summary, this system automates the intake and initial processing of RFQ emails, saving manual effort and ensuring timely responses and updates across different business functions, all powered by a modular design and testable with mock services.

## Task 3: RAG Knowledge Base (AR/EN)

### Key Components for RAG:
Before we dive in, let's identify the key players from your workspace structure for the RAG feature:
*   `src/services/rag_core.py`: This is the brain of the RAG system, orchestrating all the steps.
*   `data/` folder: This is where your knowledge documents (`document1_en.txt`, `document2_ar.txt`, etc.) are stored. This is the information RAG will learn from.
*   `src/services/llm_utils.py`: This file helps `rag_core.py` interact with the Language Model (LLM) for both understanding text (creating embeddings) and generating answers.
*   `src/config.py`: This file holds important settings, such as whether to use a mock LLM or a real one.
*   `mocks/mock_llm_service.py`: A stand-in LLM service used for testing or when a real LLM isn't configured, typically accessed via `llm_utils.py`.

### Explanation of RAG Data Flow:
RAG stands for Retrieval Augmented Generation. Think of it as giving an intelligent assistant (like ChatGPT) access to a library of specific documents, so it can answer your questions using only information from those documents, rather than just its general knowledge.

There are two main phases for the RAG feature: Preparation (building the knowledge base) and Querying (asking questions).

#### Phase 1: Preparation (Building the Knowledge Base)
This phase happens typically once when the RAG system starts up or when new documents are added.

1.  **Loading Documents (`src/services/rag_core.py` reads `data/` files):**
    *   The `RAGCore` in `src/services/rag_core.py` is told which document files (e.g., `document1_en.txt`, `document2_ar.txt`) to use.
    *   It goes to the `data/` folder, opens these files, and reads their entire content. Each document is stored internally with its text and original filename (source).
2.  **Chunking Documents (`src/services/rag_core.py`):**
    *   Long documents are too big for the LLM to process at once. So, `rag_core.py` breaks each document into smaller, manageable pieces called "chunks." These chunks often overlap slightly to ensure no important context is lost between them.
3.  **Generating Embeddings (`src/services/rag_core.py` uses `src/services/llm_utils.py`):**
    *   For each small text chunk, `rag_core.py` asks `src/services/llm_utils.py` to convert the text into a numerical representation called an "embedding."
    *   An embedding is like a unique numerical fingerprint for each piece of text. Texts with similar meanings will have similar numerical fingerprints.
    *   `src/services/llm_utils.py` might use a real LLM provider (like OpenAI) or, for testing, it might use `mocks/mock_llm_service.py` (depending on settings in `src/config.py`) to generate these embeddings.
4.  **Building the Search Index (`src/services/rag_core.py`):**
    *   All these numerical embeddings are then organized into a special, highly efficient search structure, often called a FAISS index (though a simpler mock might be used if FAISS isn't installed).
    *   This index is like a super-fast library catalog for your embeddings, allowing the system to quickly find chunks that are numerically similar (and thus semantically similar) to a given query.

#### Phase 2: Querying (Asking Questions)
This phase happens every time a user asks a question to the RAG system.

5.  **User Query (`src/app.py` -> `src/services/rag_core.py`):**
    *   A user submits a question (e.g., "What are the key specifications for RFQ 2025-11-11?") to your application. This query would eventually be passed to the `query` method of the `RAGCore` in `src/services/rag_core.py`.
6.  **Embed the Query (`src/services/rag_core.py` uses `src/services/llm_utils.py`):**
    *   Just like with the document chunks, `rag_core.py` sends the user's question to `src/services/llm_utils.py` to convert it into its own numerical embedding (fingerprint).
7.  **Retrieve Relevant Chunks (`src/services/rag_core.py` searches the index):**
    *   `rag_core.py` uses the numerical embedding of the user's question to search its pre-built FAISS index.
    *   It finds the "top K" (e.g., 3 or 5) document chunks whose embeddings are most similar to the query's embedding. These are the pieces of information most likely to contain the answer. It also identifies the original source documents for these chunks (citations).
8.  **Augment and Generate Answer (`src/services/rag_core.py` uses `src/services/llm_utils.py`):**
    *   `rag_core.py` takes the original user question AND the retrieved relevant document chunks and sends both to `src/services/llm_utils.py`.
    *   `src/services/llm_utils.py` then sends this combined information to the underlying Language Model (again, either real or mock, based on `src/config.py` and `mocks/mock_llm_service.py`).
    *   The LLM uses this specific context from your documents to generate an informed answer to the user's question.
9.  **Return Answer and Citations (`src/services/rag_core.py` -> `src/app.py`):**
    *   `rag_core.py` receives the LLM's answer and then sends it back, along with the identified source documents (citations), to the part of your application that initiated the query (likely `src/app.py`).

In summary, the RAG feature in `src/services/rag_core.py` acts as a smart librarian. It first reads and organizes all your `data/` documents into an easily searchable format. Then, when asked a question, it quickly finds the most relevant passages from your documents and gives them to an LLM (via `src/services/llm_utils.py`) to generate a precise answer, citing its sources.

## Task 2: Quotation Microservice (Python + OpenAI)

### Data Flow and Components:

1.  **Request Initiation (`src/app.py`):**
    *   A user sends a request to the `/quote` endpoint of the FastAPI application, defined in `src/app.py`.
    *   This request contains information about the client, currency, a list of items (SKU, quantity, unit cost, margin), delivery terms, and optional notes. This data is structured according to the `QuoteRequest` model within `src/app.py`.
2.  **Quote Calculation (`src/app.py`):**
    *   `src/app.py` receives the incoming request.
    *   It then iterates through each item provided in the request to calculate the `price_per_line` (unit cost adjusted by margin and quantity) and accumulates these to determine the `grand_total` for the entire quote.
3.  **Preparing for LLM (`src/app.py`):**
    *   After calculating the totals, `src/app.py` gathers summary data relevant for generating email drafts. This includes the client's name, currency, grand total, delivery terms, and any special notes.
4.  **Calling the LLM Service (`src/app.py` -> `src/services/llm_utils.py`):**
    *   `src/app.py` instantiates an `LLMService` object from `src/services/llm_utils.py`.
    *   It then calls the `generate_email_draft` method of this service twice, once for an English draft and once for an Arabic draft, passing the summary data and the desired language.
5.  **LLM Service Processing (`src/services/llm_utils.py`):**
    *   Inside `src/services/llm_utils.py`, the `LLMService` prepares a detailed prompt based on the `summary_data` and the requested language.
    *   It checks the `src/config.py` file to see if `USE_MOCK_LLM` is enabled.
        *   **If `USE_MOCK_LLM` is `True`:** The service interacts with `mocks/mock_llm_service.py`. This mock service simulates the behavior of a real Language Model (LLM) for testing or development purposes, returning a predefined or templated response.
        *   **If `USE_MOCK_LLM` is `False`:** The service uses the actual OpenAI API. It retrieves the `OPENAI_API_KEY` from `src/config.py` to authenticate and send the generated prompt to OpenAI's language model (e.g., GPT-3.5 Turbo or GPT-4). The LLM then generates the email draft based on the prompt.
6.  **Receiving LLM Response (`src/services/llm_utils.py` -> `src/app.py`):**
    *   The `LLMService` receives the generated email drafts (English and Arabic) from either the mock service or the actual OpenAI API.
    *   It then returns these draft texts back to `src/app.py`.
7.  **Final Response (`src/app.py`):**
    *   `src/app.py` combines all the calculated quote details (client name, currency, line items, grand total, delivery terms, notes) with the received English and Arabic email drafts into a final `QuoteResponse` object.
    *   This `QuoteResponse` is then sent back to the user as the output of the `/quote` endpoint.

In essence, `src/app.py` handles the initial request, calculates the numerical aspects of the quote, and orchestrates the call to `src/services/llm_utils.py` for generating text-based components (email drafts). `src/services/llm_utils.py` acts as an intermediary, constructing prompts and communicating with an LLM (either real or mocked), while `src/config.py` provides necessary configuration like API keys or mock flags.

## Getting Started

To get started with the Repo Pilot project:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd repo-pilot
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure:** Review `src/config.py` to set up API keys or enable/disable mock services as needed.
4.  **Run the application:**
    ```bash
    python src/app.py
    ```
    (Note: For a FastAPI application, you might use `uvicorn src.app:app --reload` if configured as such.)
5.  **Explore endpoints:** Use tools like `curl`, Postman, or your browser to interact with the FastAPI endpoints (`/quote`, etc.) or run the `if __name__ == "__main__":` block in `src/app.py` for RFQ automation demonstration.

## Configuration

The `src/config.py` file is central to configuring the project. It allows you to:
*   Enable/disable mock services (e.g., `MOCK_LLM_ENABLED`, `MOCK_GOOGLE_SHEETS_ENABLED`) for testing and development without relying on external APIs.
*   Set API keys for actual external services (e.g., `OPENAI_API_KEY`) when running in a production-like environment.


$env:PYTHONPATH = (Get-Location).Path
pytest ./tests/test_task_1.py -v -s