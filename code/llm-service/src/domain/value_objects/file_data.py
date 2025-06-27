# src/domain/value_objects/file_data.py
from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass(frozen=True)
class FileData:
    """Value object for file data"""
    filename: str
    content: bytes
    content_type: str
    size: int
    dataframe: Optional[pd.DataFrame] = None
    
    def __post_init__(self):
        if self.size > 50 * 1024 * 1024:  # 50MB limit
            raise ValueError(f"File {self.filename} exceeds 50MB limit")