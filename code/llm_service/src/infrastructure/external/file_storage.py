import os
import aiofiles
from typing import Optional
from ...domain.value_objects import FileData

class FileStorageService:
    """Service for file storage operations"""
    
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    async def save_file(self, file_data: FileData) -> str:
        """Save file to storage"""
        file_path = os.path.join(self.upload_folder, file_data.filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data.content)
        
        return file_path
    
    async def read_file(self, filename: str) -> Optional[bytes]:
        """Read file from storage"""
        file_path = os.path.join(self.upload_folder, filename)
        
        if not os.path.exists(file_path):
            return None
        
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()
    
    def delete_file(self, filename: str) -> bool:
        """Delete file from storage"""
        file_path = os.path.join(self.upload_folder, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
