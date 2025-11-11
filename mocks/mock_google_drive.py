import os
import shutil

class MockGoogleDriveService:
    def __init__(self, drive_folder_path='mock_drive_folder'):
        self.drive_folder_path = drive_folder_path
        os.makedirs(self.drive_folder_path, exist_ok=True)
        print(f"[MOCK DRIVE] Initialized. Mock drive folder: {self.drive_folder_path}")

    def archive_attachment(self, file_name: str, file_content: bytes, target_folder_name: str = "RFQ_Attachments") -> str:
        target_path = os.path.join(self.drive_folder_path, target_folder_name)
        os.makedirs(target_path, exist_ok=True)
        
        destination_path = os.path.join(target_path, file_name)
        with open(destination_path, 'wb') as f:
            f.write(file_content)
        print(f"[MOCK DRIVE] Archived attachment '{file_name}' to '{destination_path}'.")
        return destination_path

    def get_mock_folder_path(self):
        return self.drive_folder_path
