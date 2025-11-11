import email
from email import policy
from email.message import EmailMessage
from typing import Dict, Any, List, Tuple

class EmailParser:
    def parse_email(self, raw_email_content: bytes) -> Dict[str, Any]:
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
