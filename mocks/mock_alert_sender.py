import datetime

class MockAlertSenderService:
    def __init__(self, output_file='internal_alert_log.txt'):
        self.output_file = output_file
        print(f"[MOCK ALERT] Initialized. Internal alerts will be logged to '{self.output_file}'.")

    def send_alert(self, message: str, channel: str = "#general"):
        timestamp = datetime.datetime.now().isoformat()
        alert_message = f"[{timestamp}] [MOCK ALERT - {channel}] {message}"
        print(alert_message)
        with open(self.output_file, 'a') as f:
            f.write(alert_message + "\n")
        print(f"[MOCK ALERT] Alert logged to {self.output_file}.")
