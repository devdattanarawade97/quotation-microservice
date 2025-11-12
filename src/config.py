"""
This module manages the application's configuration settings.

It loads environment variables using `dotenv` and defines a `Config` class
to centralize access to various service-specific settings, including
API keys, mock toggles, and resource paths.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Global configuration variables, typically for LLM usage or general app state
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() == "true"

class Config:
    """
    Centralized configuration class for managing various application settings
    retrieved from environment variables.

    Attributes are categorized by the service they configure (General, LLM,
    Google Sheets, Salesforce, Google Drive, Email, Internal Alerts).
    Boolean flags (e.g., `_ENABLED`) allow for easy toggling of mock services.
    """
    # --- General Settings ---
    MOCK_MODE_ENABLED = os.getenv('MOCK_MODE_ENABLED', 'true').lower() == 'true'
    """Global flag to enable/disable mock mode for all services."""

    # --- LLM Settings ---
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    """API key for the Language Model service."""
    MOCK_LLM_ENABLED = os.getenv('MOCK_LLM_ENABLED', 'true').lower() == 'true'
    """Flag to enable/disable the mock LLM service."""

    # --- Google Sheets Settings ---
    GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 'credentials.json')
    """Path to the Google Sheets API credentials file."""
    RFQ_SHEET_ID = os.getenv('RFQ_SHEET_ID')
    """The ID of the Google Sheet used for RFQ data."""
    MOCK_GOOGLE_SHEETS_ENABLED = os.getenv('MOCK_GOOGLE_SHEETS_ENABLED', 'true').lower() == 'true'
    """Flag to enable/disable the mock Google Sheets service."""

    # --- Salesforce (CRM) Settings ---
    SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME')
    """Salesforce username for API access."""
    SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD')
    """Salesforce password for API access."""
    SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN')
    """Salesforce security token for API access."""
    MOCK_SALESFORCE_ENABLED = os.getenv('MOCK_SALESFORCE_ENABLED', 'true').lower() == 'true'
    """Flag to enable/disable the mock Salesforce CRM service."""

    # --- Google Drive Settings ---
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    """The ID of the Google Drive folder for archiving attachments."""
    MOCK_GOOGLE_DRIVE_ENABLED = os.getenv('MOCK_GOOGLE_DRIVE_ENABLED', 'true').lower() == 'true'
    """Flag to enable/disable the mock Google Drive service."""

    # --- Email Settings (for auto-reply) ---
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    """The email address used to send automated replies."""
    SENDER_EMAIL_PASSWORD = os.getenv('SENDER_EMAIL_PASSWORD') # Or app-specific password
    """The password or app-specific password for the sender email account."""
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    """The SMTP server hostname for sending emails."""
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    """The SMTP server port for sending emails."""
    MOCK_EMAIL_SENDER_ENABLED = os.getenv('MOCK_EMAIL_SENDER_ENABLED', 'true').lower() == 'true'
    """Flag to enable/disable the mock email sender service."""

    # --- Internal Alert Settings (Slack/Teams) ---
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    """Webhook URL for Slack alerts."""
    TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')
    """Webhook URL for Microsoft Teams alerts."""
    MOCK_ALERT_SENDER_ENABLED = os.getenv('MOCK_ALERT_SENDER_ENABLED', 'true').lower() == 'true'
    """Flag to enable/disable the mock internal alert sender service."""

# Instantiate config
settings = Config()
"""An instance of the Config class, providing easy access to application settings."""

