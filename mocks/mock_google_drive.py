import os
import shutil

class MockGoogleDriveService:
    """
    A mock service for interacting with Google Drive functionalities.

    This service simulates archiving attachments to a local folder structure,
    mimicking Google Drive's behavior for testing purposes.
    """
    def __init__(self, drive_folder_path='mock_drive_folder'):
        """
        Initializes the MockGoogleDriveService.

        Creates a local directory to act as the mock Google Drive folder.

        Args:
            drive_folder_path (str): The path to the local directory that will
                                     simulate the Google Drive folder.
                                     Defaults to 'mock_drive_folder'.
        """
        self.drive_folder_path = drive_folder_path
        os.makedirs(self.drive_folder_path, exist_ok=True)
        print(f"[MOCK DRIVE] Initialized. Mock drive folder: {self.drive_folder_path}")

    def archive_attachment(self, file_name: str, file_content: bytes, target_folder_name: str = "RFQ_Attachments") -> str:
        """
        Simulates archiving an attachment to a specified folder within the mock drive.

        Creates the target folder if it doesn't exist and writes the file content
        to a new file within that folder.

        Args:
            file_name (str): The name of the file to archive.
            file_content (bytes): The binary content of the file.
            target_folder_name (str): The name of the subfolder within the
                                      mock drive to save the attachment.
                                      Defaults to "RFQ_Attachments".

        Returns:
            str: The full path where the attachment was saved.
        """
        target_path = os.path.join(self.drive_folder_path, target_folder_name)
        os.makedirs(target_path, exist_ok=True)
        
        destination_path = os.path.join(target_path, file_name)
        with open(destination_path, 'wb') as f:
            f.write(file_content)
        print(f"[MOCK DRIVE] Archived attachment '{file_name}' to '{destination_path}'.")
        return destination_path

    def get_mock_folder_path(self):
        """
        Returns the path to the mock Google Drive folder.

        Returns:
            str: The absolute path to the mock drive folder.
        """
        return self.drive_folder_path

