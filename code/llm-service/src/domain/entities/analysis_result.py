
# src/domain/entities/analysis_result.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class AnalysisResult:
    """Domain entity for analysis results"""
    question: str
    answer: str
    model_used: str
    context_included: bool
    session_id: Optional[str]
    timestamp: datetime
    data_provided: bool = False
    files_processed: Optional[List[str]] = None
    token_count: Optional[int] = None
    processing_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'question': self.question,
            'answer': self.answer,
            'model_used': self.model_used,
            'context_included': self.context_included,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'data_provided': self.data_provided,
            'files_processed': self.files_processed,
            'token_count': self.token_count,
            'processing_time': self.processing_time
        }