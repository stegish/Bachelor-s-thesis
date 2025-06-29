from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnalysisRequestDTO(BaseModel):
    """DTO for analysis requests"""
    question: str = Field(..., min_length=1, max_length=5000)
    context_data: Optional[Dict[str, Any]] = None
    include_db_context: bool = True
    session_id: Optional[str] = None
    
    def to_domain(self) -> 'AnalysisRequest':
        """Convert to domain entity"""
        from ...domain.entities import AnalysisRequest
        return AnalysisRequest(
            question=self.question,
            context_data=self.context_data,
            include_db_context=self.include_db_context,
            session_id=self.session_id
        )

class CSVAnalysisRequestDTO(BaseModel):
    """DTO for CSV analysis requests"""
    question: str = Field(..., min_length=1, max_length=5000)
    include_context: bool = True