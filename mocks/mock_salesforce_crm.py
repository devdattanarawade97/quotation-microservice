import json
import os
import datetime

class MockSalesforceCRMService:
    """
    A mock service for interacting with Salesforce CRM functionalities.

    This service simulates creating and logging CRM opportunities by storing data
    in a local JSON file.
    """
    def __init__(self, output_file='logs/crm_mock_log.json'): # Changed path
        """
        Initializes the MockSalesforceCRMService.

        Loads existing opportunities from the output JSON file if it exists and is valid.

        Args:
            output_file (str): The path to the JSON file where CRM opportunities
                               will be logged. Defaults to 'logs/crm_mock_log.json'.
        """
        self.output_file = output_file
        self.opportunities = []
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r') as f:
                    self.opportunities = json.load(f)
            except json.JSONDecodeError:
                self.opportunities = [] # Handle empty or malformed JSON
        print(f"[MOCK SALESFORCE] Initialized with {len(self.opportunities)} existing opportunities.")

    def create_opportunity(self, opportunity_data: dict) -> dict:
        """
        Simulates creating a new CRM opportunity in Salesforce.

        Generates a mock ID, timestamps, and appends the new opportunity data
        to the internal list, then saves it to the configured JSON output file.

        Args:
            opportunity_data (dict): A dictionary containing the data for the
                                     new opportunity (e.g., "Name", "Amount", etc.).

        Returns:
            dict: The newly created opportunity dictionary, including mock ID
                  and timestamps.
        """
        print(f"[MOCK SALESFORCE] Creating opportunity: {opportunity_data}")
        # Simulate Salesforce ID and timestamps
        new_opportunity = {
            "Id": f"006xxxxxxxxxxxxxxx{len(self.opportunities) + 1}",
            "Name": opportunity_data.get("Name"),
            "StageName": opportunity_data.get("StageName", "Prospecting"),
            "CloseDate": opportunity_data.get("CloseDate", datetime.date.today().isoformat()),
            "Amount": opportunity_data.get("Amount"),
            "Description": opportunity_data.get("Description"),
            "CreatedDate": datetime.datetime.now().isoformat(),
            **opportunity_data # Include all provided data
        }
        self.opportunities.append(new_opportunity)
        with open(self.output_file, 'w') as f:
            json.dump(self.opportunities, f, indent=4)
        print(f"[MOCK SALESFORCE] Opportunity '{new_opportunity['Name']}' created and logged to {self.output_file}.")
        return new_opportunity

