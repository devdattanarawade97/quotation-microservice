class MockEmailSenderService:
    def __init__(self, output_file='auto_reply_sample.txt'):
        self.output_file = output_file
        print(f"[MOCK EMAIL] Initialized. Auto-reply samples will be saved to '{self.output_file}'.")

    def send_email(self, recipient: str, subject: str, body: str, is_html: bool = False):
        print(f"[MOCK EMAIL] Sending email to: {recipient}")
        print(f"[MOCK EMAIL] Subject: {subject}")
        print(f"[MOCK EMAIL] Body:\n---\n{body}\n---")

        with open(self.output_file, 'a') as f:
            f.write(f"--- NEW AUTO-REPLY ({datetime.datetime.now().isoformat()}) ---\n")
            f.write(f"To: {recipient}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Content-Type: {'text/html' if is_html else 'text/plain'}\n")
            f.write(f"Body:\n{body}\n\n")
        print(f"[MOCK EMAIL] Auto-reply sample saved to {self.output_file}.")

import datetime # Added import for datetime