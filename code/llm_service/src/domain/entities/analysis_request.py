from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass
class AnalysisRequest:
    """Domain entity for analysis requests"""
    question: str
    context_data: Optional[Dict[str, Any]] = None
    files: Optional[List['FileData']] = None
    include_db_context: bool = True
    session_id: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()