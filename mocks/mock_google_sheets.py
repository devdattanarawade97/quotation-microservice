import json
import os

class MockGoogleSheetsService:
    def __init__(self, output_file='mock_sheets_log.json'):
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
        print(f"[MOCK SHEETS] Appending row: {row_data}")
        self.data.append(row_data)
        with open(self.output_file, 'w') as f:
            json.dump(self.data, f, indent=4)
        print(f"[MOCK SHEETS] Row saved to {self.output_file}.")
