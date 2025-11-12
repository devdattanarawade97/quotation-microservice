import datetime

class MockAlertSenderService:
    """
    A mock service for sending internal alerts.

    This service simulates an alert notification system by logging alert messages
    to a specified output file and printing them to the console.
    """
    def __init__(self, output_file='logs/internal_alert_log.txt'): # Changed path
        """
        Initializes the MockAlertSenderService.

        Args:
            output_file (str): The path to the file where alerts will be logged.
                               Defaults to 'logs/internal_alert_log.txt'.
        """
        self.output_file = output_file
        print(f"[MOCK ALERT] Initialized. Internal alerts will be logged to '{self.output_file}'.")

    def send_alert(self, message: str, channel: str = "#general"):
        """
        Simulates sending an alert.

        Logs the alert message with a timestamp and channel to the configured
        output file and prints it to the console.

        Args:
            message (str): The content of the alert message.
            channel (str): The channel to which the alert is sent (e.g., "#general").
                           Defaults to "#general".
        """
        timestamp = datetime.datetime.now().isoformat()
        alert_message = f"[{timestamp}] [MOCK ALERT - {channel}] {message}"
        print(alert_message)
        with open(self.output_file, 'a') as f:
            f.write(alert_message + "\n")
        print(f"[MOCK ALERT] Alert logged to {self.output_file}.")

