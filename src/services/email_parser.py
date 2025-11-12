import email
from email import policy
from email.message import EmailMessage
from typing import Dict, Any, List, Tuple

class EmailParser:
    """
    A utility class for parsing raw email content and creating mock emails.
    """
    def parse_email(self, raw_email_content: bytes) -> Dict[str, Any]:
        """
        Parses raw email content (bytes) into a structured dictionary.

        Extracts the subject, sender, plain body, HTML body, and attachments.

        Args:
            raw_email_content (bytes): The raw byte content of an email.

        Returns:
            Dict[str, Any]: A dictionary containing parsed email components:
                - "subject" (str): The email subject.
                - "sender" (str): The email sender.
                - "body_plain" (str): The plain text body of the email.
                - "body_html" (str): The HTML body of the email.
                - "attachments" (List[Dict[str, Any]]): A list of dictionaries,
                  each representing an attachment with 'filename', 'content_type', and 'payload'.
        """
        msg = email.message_from_bytes(raw_email_content, policy=policy.default)
        
        subject = msg['subject'] or ''
        sender = msg['from'] or ''
        
        body_plain = ""
        body_html = ""
        attachments = []

        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = part.get_content_disposition()

            if content_disposition == 'attachment':
                filename = part.get_filename()
                if filename:
                    attachments.append({
                        'filename': filename,
                        'content_type': content_type,
                        'payload': part.get_payload(decode=True)
                    })
            elif content_type == 'text/plain' and not content_disposition:
                body_plain = part.get_payload(decode=True).decode()
            elif content_type == 'text/html' and not content_disposition:
                body_html = part.get_payload(decode=True).decode()

        return {
            "subject": subject,
            "sender": sender,
            "body_plain": body_plain,
            "body_html": body_html,
            "attachments": attachments
        }

    def create_mock_email(self, subject: str, body: str, sender: str = 'test@example.com', attachments: List[Tuple[str, bytes]] = None) -> bytes:
        """
        Creates a mock raw email in bytes format.

        This function can be used to simulate incoming emails for testing purposes,
        including subject, body, sender, and optional attachments.

        Args:
            subject (str): The subject of the mock email.
            body (str): The plain text body of the mock email.
            sender (str, optional): The sender's email address. Defaults to 'test@example.com'.
            attachments (List[Tuple[str, bytes]], optional): A list of (filename, content_bytes) tuples for attachments.
                Defaults to None.

        Returns:
            bytes: The raw byte content of the created mock email.
        """
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = 'alrouf@example.com'

        msg.set_content(body)

        if attachments:
            for filename, content in attachments:
                maintype, subtype = 'application', 'octet-stream'
                if '.' in filename:
                    ext = filename.split('.')[-1]
                    if ext == 'pdf':
                        maintype, subtype = 'application', 'pdf'
                    elif ext in ['jpg', 'jpeg', 'png', 'gif']: # Basic image types
                        maintype, subtype = 'image', ext
                
                msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)
        
        return msg.as_bytes(policy=policy.default)

