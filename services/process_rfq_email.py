import os
import datetime
from config import settings
from services.email_parser import EmailParser
from mocks.mock_llm_service import MockLLMService
from mocks.mock_google_sheets import MockGoogleSheetsService
from mocks.mock_salesforce_crm import MockSalesforceCRMService
from mocks.mock_google_drive import MockGoogleDriveService
from mocks.mock_email_sender import MockEmailSenderService
from mocks.mock_alert_sender import MockAlertSenderService

# Initialize services (using mocks based on config)
email_parser = EmailParser()
llm_service = MockLLMService() if settings.MOCK_LLM_ENABLED else None # Placeholder for real LLM
google_sheets_service = MockGoogleSheetsService() if settings.MOCK_GOOGLE_SHEETS_ENABLED else None # Placeholder for real Sheets
salesforce_crm_service = MockSalesforceCRMService() if settings.MOCK_SALESFORCE_ENABLED else None # Placeholder for real CRM
google_drive_service = MockGoogleDriveService() if settings.MOCK_GOOGLE_DRIVE_ENABLED else None # Placeholder for real Drive
email_sender_service = MockEmailSenderService() if settings.MOCK_EMAIL_SENDER_ENABLED else None # Placeholder for real Email Sender
alert_sender_service = MockAlertSenderService() if settings.MOCK_ALERT_SENDER_ENABLED else None # Placeholder for real Alert Sender

def process_rfq_email(raw_email_content: bytes):
    print("\n--- Processing Incoming RFQ Email ---")

    # 1. Parse Email
    parsed_email = email_parser.parse_email(raw_email_content)
    subject = parsed_email['subject']
    body_plain = parsed_email['body_plain']
    sender = parsed_email['sender']
    attachments = parsed_email['attachments']

    print(f"Parsed Email - Subject: {subject}, From: {sender}")

    # 2. Extract Fields using LLM (or mock)
    extracted_fields = llm_service.extract_fields(subject, body_plain) # This will call mock if enabled
    print(f"Extracted Fields: {extracted_fields}")

    # 3. Write Row to Google Sheets (or mock)
    if google_sheets_service:
        sheet_row = {
            "Timestamp": datetime.datetime.now().isoformat(),
            "Subject": subject,
            "Sender": sender,
            **extracted_fields
        }
        google_sheets_service.append_row(sheet_row)

    # 4. Create Opportunity in Salesforce (or mock)
    if salesforce_crm_service:
        opportunity_name = f"RFQ: {extracted_fields.get('product', 'Unknown Product')} from {extracted_fields.get('contact_person', 'Unknown Client')}"
        opportunity_data = {
            "Name": opportunity_name,
            "StageName": "Qualification",
            "CloseDate": (datetime.date.today() + datetime.timedelta(weeks=4)).isoformat(), # Estimate 4 weeks out
            "Description": f"RFQ for {extracted_fields.get('quantity', '')} {extracted_fields.get('product', '')}. Needed in {extracted_fields.get('location', '')} within {extracted_fields.get('delivery_time', '')}. Contact: {extracted_fields.get('contact_email', '')}",
            "Amount": None # Amount could be estimated by LLM or left blank for manual input
        }
        salesforce_crm_service.create_opportunity(opportunity_data)

    # 5. Archive Attachments to Drive (or mock)
    if google_drive_service and attachments:
        for attachment in attachments:
            google_drive_service.archive_attachment(attachment['filename'], attachment['payload'], target_folder_name=f"RFQ_{datetime.date.today().isoformat()}")

    # 6. Auto-reply to Client (AR/EN) (or mock)
    if email_sender_service and extracted_fields.get('contact_email'):
        reply_subject = f"Re: {subject}"
        reply_body_ar = """مرحباً [اسم العميل],\n\nشكراً لاستفسارك بخصوص [المنتج]. لقد استلمنا طلبك وسنتواصل معك قريباً.\n\nمع خالص التقدير،\nفريق العروف\n""".replace('[اسم العميل]', extracted_fields.get('contact_person', 'عميلنا العزيز')).replace('[المنتج]', extracted_fields.get('product', 'طلبك'))

        reply_body_en = f"""Hello {extracted_fields.get('contact_person', 'Valued Client')},\n\nThank you for your inquiry regarding {extracted_fields.get('product', 'your request')}. We have received your request and will get back to you shortly.\n\nBest regards,\nAlrouf Team\n"""

        # For simplicity, sending English auto-reply for now
        email_sender_service.send_email(extracted_fields['contact_email'], reply_subject, reply_body_en)

    # 7. Post Internal Alert (Slack/Teams) (or mock)
    if alert_sender_service:
        alert_message = f"New RFQ received: '{subject}' from {sender}. Fields extracted: {extracted_fields.get('product')}, {extracted_fields.get('quantity')}."
        alert_sender_service.send_alert(alert_message, channel="#rfq_alerts")

    print("--- RFQ Email Processing Complete ---\n")

# Example Usage with a mock email
if __name__ == "__main__":
    # The 'datetime' module is already imported at the top of the file.

    test_subject = "RFQ — Streetlight Poles"
    test_body = """Hello Alrouf, please quote 120 pcs streetlight model ALR-SL-90W. Needed in Dammam within 4 weeks. Attach specs. Regards, Eng. Omar, +9665XXXX, omar@client.com"""
    test_attachment_content = b"This is a dummy spec sheet content.\n" * 5 # 5 lines of dummy content

    # Create a mock raw email with an attachment
    mock_raw_email = email_parser.create_mock_email(
        subject=test_subject,
        body=test_body,
        sender="omar@client.com",
        attachments=[("specs.pdf", test_attachment_content)]
    )

    process_rfq_email(mock_raw_email)

    print("\n--- Verification of Mock Outputs ---")
    if settings.MOCK_GOOGLE_SHEETS_ENABLED: print(f"Check mock_sheets_log.json for Sheets output.")
    if settings.MOCK_SALESFORCE_ENABLED: print(f"Check crm_mock_log.json for CRM opportunity.")
    if settings.MOCK_GOOGLE_DRIVE_ENABLED: print(f"Check {google_drive_service.get_mock_folder_path()} for archived attachments.")
    if settings.MOCK_EMAIL_SENDER_ENABLED: print(f"Check auto_reply_sample.txt for client auto-reply.")
    if settings.MOCK_ALERT_SENDER_ENABLED: print(f"Check internal_alert_log.txt for internal alerts.")
