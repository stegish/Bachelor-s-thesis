from abc import ABC, abstractmethod
from typing import List
from ..value_objects import FileData
import pandas as pd

class IFileProcessor(ABC):
    """Interface for file processing"""
    
    @abstractmethod
    async def process_csv(self, file_data: FileData) -> pd.DataFrame:
        """Process CSV file"""
        pass
    
    @abstractmethod
    async def validate_file(self, file_data: FileData) -> bool:
        """Validate file"""
        pass