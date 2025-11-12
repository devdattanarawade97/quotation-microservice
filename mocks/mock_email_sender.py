import datetime # Added import for datetime

class MockEmailSenderService:
    """
    A mock service for sending emails.

    This service simulates sending emails by logging the email details (recipient,
    subject, body) to a specified output file, mimicking an auto-reply sample.
    """
    def __init__(self, output_file='data/auto_reply_sample.txt'): # Changed path
        """
        Initializes the MockEmailSenderService.

        Args:
            output_file (str): The path to the file where email samples will be saved.
                               Defaults to 'data/auto_reply_sample.txt'.
        """
        self.output_file = output_file
        print(f"[MOCK EMAIL] Initialized. Auto-reply samples will be saved to '{self.output_file}'.")

    def send_email(self, recipient: str, subject: str, body: str, is_html: bool = False):
        """
        Simulates sending an email.

        Logs the email's recipient, subject, body, and content type to the
        configured output file and prints details to the console.

        Args:
            recipient (str): The email address of the recipient.
            subject (str): The subject line of the email.
            body (str): The main content of the email.
            is_html (bool): True if the email body is HTML, False otherwise (plain text).
                            Defaults to False.
        """
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

