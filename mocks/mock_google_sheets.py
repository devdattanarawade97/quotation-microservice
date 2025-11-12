import json
import os

class MockGoogleSheetsService:
    """
    A mock service for interacting with Google Sheets.

    This service simulates appending rows to a Google Sheet by storing data
    in a local JSON file.
    """
    def __init__(self, output_file='logs/mock_sheets_log.json'): # Changed path
        """
        Initializes the MockGoogleSheetsService.

        Loads existing data from the output JSON file if it exists and is valid.

        Args:
            output_file (str): The path to the JSON file where sheet data will be logged.
                               Defaults to 'logs/mock_sheets_log.json'.
        """
        self.output_file = output_file
        self.data = []
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = [] # Handle empty or malformed JSON
        print(f"[MOCK SHEETS] Initialized with {len(self.data)} existing entries.")

    def append_row(self, row_data: dict):
        """
        Simulates appending a new row of data to a Google Sheet.

        The `row_data` dictionary is appended to the internal list of data and
        then saved back to the configured JSON output file.

        Args:
            row_data (dict): A dictionary representing the row to be appended.
                             Keys are column headers, values are cell contents.
        """
        print(f"[MOCK SHEETS] Appending row: {row_data}")
        self.data.append(row_data)
        with open(self.output_file, 'w') as f:
            json.dump(self.data, f, indent=4)
        print(f"[MOCK SHEETS] Row saved to {self.output_file}.")

