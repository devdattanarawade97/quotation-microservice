import os
import datetime
from src.config import settings
from src.services.email_parser import EmailParser
from mocks.mock_llm_service import MockLLMService
from mocks.mock_google_sheets import MockGoogleSheetsService
from mocks.mock_salesforce_crm import MockSalesforceCRMService
from mocks.mock_google_drive import MockGoogleDriveService
from mocks.mock_email_sender import MockEmailSenderService
from mocks.mock_alert_sender import MockAlertSenderService

# Initialize services (using mocks based on config)
# In a real test suite, these would often be passed as fixtures
# For this example, we'll initialize them once for the test function.
email_parser = EmailParser()
llm_service = MockLLMService()
google_sheets_service = MockGoogleSheetsService()
salesforce_crm_service = MockSalesforceCRMService()
google_drive_service = MockGoogleDriveService()
email_sender_service = MockEmailSenderService()
alert_sender_service = MockAlertSenderService()

def run_rfq_processing_logic(raw_email_content: bytes):
    """
    Encapsulates the core RFQ processing logic.
    This function will be called by the test.
    """
    print("\n--- Processing Incoming RFQ Email ---")

    # 1. Parse Email
    parsed_email = email_parser.parse_email(raw_email_content)
    subject = parsed_email['subject']
    body_plain = parsed_email['body_plain']
    sender = parsed_email['sender']
    attachments = parsed_email['attachments']

    print(f"Parsed Email - Subject: {subject}, From: {sender}")

    # 2. Extract Fields using LLM (or mock)
    extracted_fields = llm_service.extract_fields(subject, body_plain)
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
        # Use the extracted fields for a more personalized reply
        contact_person = extracted_fields.get('contact_person', 'عميلنا العزيز')
        product_name_ar = extracted_fields.get('product', 'طلبك')
        product_name_en = extracted_fields.get('product', 'your request')

        reply_body_ar = f"""مرحباً {contact_person},\n\nشكراً لاستفسارك بخصوص {product_name_ar}. لقد استلمنا طلبك وسنتواصل معك قريباً.\n\nمع خالص التقدير،\nفريق العروف\n"""
        reply_body_en = f"""Hello {contact_person},\n\nThank you for your inquiry regarding {product_name_en}. We have received your request and will get back to you shortly.\n\nBest regards,\nAlrouf Team\n"""

        # For simplicity, sending English auto-reply for now
        email_sender_service.send_email(extracted_fields['contact_email'], reply_subject, reply_body_en)

    # 7. Post Internal Alert (Slack/Teams) (or mock)
    if alert_sender_service:
        alert_message = f"New RFQ received: '{subject}' from {sender}. Fields extracted: {extracted_fields.get('product')}, {extracted_fields.get('quantity')}."
        alert_sender_service.send_alert(alert_message, channel="#rfq_alerts")

    print("--- RFQ Email Processing Complete ---\n")
    return extracted_fields # Return extracted fields for assertions


def test_process_rfq_email_workflow():
    """
    Tests the end-to-end RFQ email processing workflow using mock services.
    """
    # Create a mock raw email with an attachment
    test_subject = "RFQ — Streetlight Poles"
    test_body = """Hello Alrouf, please quote 120 pcs streetlight model ALR-SL-90W. Needed in Dammam within 4 weeks. Attach specs. Regards, Eng. Omar, +9665XXXX, omar@client.com"""
    test_attachment_content = b"This is a dummy spec sheet content.\n" * 5

    mock_raw_email = email_parser.create_mock_email(
        subject=test_subject,
        body=test_body,
        sender="omar@client.com",
        attachments=[("specs.pdf", test_attachment_content)]
    )

    # Execute the processing logic
    extracted_fields = run_rfq_processing_logic(mock_raw_email)

    # --- Assertions to verify the workflow ---
    print("\n--- Verification of Mock Outputs with Assertions ---")

    # Verify LLM extraction
    assert extracted_fields["product"] == "streetlight model ALR-SL-90W"
    assert extracted_fields["quantity"] == "120 pcs"
    assert extracted_fields["contact_person"] == "Eng. Omar"
    assert extracted_fields["contact_email"] == "omar@client.com"
    
    # Verify Google Sheets interaction (check if at least one entry exists and its content)
    if settings.MOCK_GOOGLE_SHEETS_ENABLED:
        # Load the mock sheets log and check the last entry
        import json
        with open(google_sheets_service.output_file, 'r') as f:
            sheet_data = json.load(f)
        assert len(sheet_data) > 0
        last_entry = sheet_data[-1]
        assert last_entry["Subject"] == test_subject
        assert last_entry["Sender"] == "omar@client.com"
        assert last_entry["product"] == "streetlight model ALR-SL-90W"
        assert last_entry["contact_person"] == "Eng. Omar"
        print(f"✅ Sheets output verified in {google_sheets_service.output_file}.")

    # Verify Salesforce CRM interaction
    if settings.MOCK_SALESFORCE_ENABLED:
        # Load the mock CRM log and check the last entry
        import json
        with open(salesforce_crm_service.output_file, 'r') as f:
            crm_data = json.load(f)
        assert len(crm_data) > 0
        last_opportunity = crm_data[-1]
        expected_opportunity_name = f"RFQ: streetlight model ALR-SL-90W from Eng. Omar"
        assert last_opportunity["Name"] == expected_opportunity_name
        assert "Qualification" in last_opportunity["StageName"]
        print(f"✅ CRM opportunity verified in {salesforce_crm_service.output_file}.")

    # Verify Google Drive attachment archiving
    if settings.MOCK_GOOGLE_DRIVE_ENABLED:
        today_folder = f"RFQ_{datetime.date.today().isoformat()}"
        archived_path = os.path.join(google_drive_service.get_mock_folder_path(), today_folder, "specs.pdf")
        assert os.path.exists(archived_path)
        with open(archived_path, 'rb') as f:
            content = f.read()
        assert content == test_attachment_content
        print(f"✅ Archived attachment verified in {archived_path}.")

    # Verify Email Sender auto-reply
    if settings.MOCK_EMAIL_SENDER_ENABLED:
        with open(email_sender_service.output_file, 'r') as f:
            email_content = f.read()
        assert "To: omar@client.com" in email_content
        assert f"Subject: Re: {test_subject}" in email_content
        assert "Hello Eng. Omar" in email_content # Assert personalized greeting
        assert "inquiry regarding streetlight model ALR-SL-90W" in email_content # Assert product name
        print(f"✅ Auto-reply sample verified in {email_sender_service.output_file}.")

    # Verify Alert Sender internal alert
    if settings.MOCK_ALERT_SENDER_ENABLED:
        with open(alert_sender_service.output_file, 'r') as f:
            alert_content = f.read()
        assert "New RFQ received: 'RFQ — Streetlight Poles' from omar@client.com." in alert_content
        assert "Fields extracted: streetlight model ALR-SL-90W, 120 pcs." in alert_content
        assert "#rfq_alerts" in alert_content
        print(f"✅ Internal alert verified in {alert_sender_service.output_file}.")

