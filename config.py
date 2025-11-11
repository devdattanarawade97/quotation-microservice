import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # --- General Settings ---
    MOCK_MODE_ENABLED = os.getenv('MOCK_MODE_ENABLED', 'true').lower() == 'true'
    
    # --- LLM Settings ---
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    MOCK_LLM_ENABLED = os.getenv('MOCK_LLM_ENABLED', 'true').lower() == 'true'

    # --- Google Sheets Settings ---
    GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 'credentials.json')
    RFQ_SHEET_ID = os.getenv('RFQ_SHEET_ID')
    MOCK_GOOGLE_SHEETS_ENABLED = os.getenv('MOCK_GOOGLE_SHEETS_ENABLED', 'true').lower() == 'true'

    # --- Salesforce (CRM) Settings ---
    SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME')
    SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD')
    SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN')
    MOCK_SALESFORCE_ENABLED = os.getenv('MOCK_SALESFORCE_ENABLED', 'true').lower() == 'true'
    
    # --- Google Drive Settings ---
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    MOCK_GOOGLE_DRIVE_ENABLED = os.getenv('MOCK_GOOGLE_DRIVE_ENABLED', 'true').lower() == 'true'

    # --- Email Settings (for auto-reply) ---
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_EMAIL_PASSWORD = os.getenv('SENDER_EMAIL_PASSWORD') # Or app-specific password
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    MOCK_EMAIL_SENDER_ENABLED = os.getenv('MOCK_EMAIL_SENDER_ENABLED', 'true').lower() == 'true'
    
    # --- Internal Alert Settings (Slack/Teams) ---
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')
    MOCK_ALERT_SENDER_ENABLED = os.getenv('MOCK_ALERT_SENDER_ENABLED', 'true').lower() == 'true'

# Instantiate config
settings = Config()
