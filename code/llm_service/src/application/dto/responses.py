from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from ...domain.entities import AnalysisResult

class AnalysisResponseDTO(BaseModel):
    """DTO for analysis responses"""
    question: str
    answer: str
    model_used: str
    context_included: bool
    session_id: Optional[str]
    timestamp: str
    data_provided: bool = False
    files_processed: Optional[List[str]] = None
    token_count: Optional[int] = None
    processing_time: Optional[float] = None
    
    model_config = {
        'protected_namespaces': ()  # This fixes the warning about model_used
    }
    
    @classmethod
    def from_domain(cls, result: AnalysisResult) -> 'AnalysisResponseDTO':
        """Convert from domain entity"""
        return cls(
            question=result.question,
            answer=result.answer,
            model_used=result.model_used,
            context_included=result.context_included,
            session_id=result.session_id,
            timestamp=result.timestamp.isoformat(),
            data_provided=result.data_provided,
            files_processed=result.files_processed,
            token_count=result.token_count,
            processing_time=result.processing_time
        )

class ChatResponseDTO(BaseModel):
    """DTO for chat responses"""
    message: str
    session_id: str
    timestamp: str

class SuggestionsResponseDTO(BaseModel):
    """DTO for suggestions responses"""
    suggestions: List[str]
    metrics_analyzed: Dict[str, Any]
    timestamp: str