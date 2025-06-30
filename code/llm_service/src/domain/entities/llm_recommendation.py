from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

class RecommendationType(Enum):
    MAINTENANCE = "maintenance"
    OPTIMIZATION = "optimization"
    ALERT = "alert"
    IMPROVEMENT = "improvement"
    ANOMALY = "anomaly"

@dataclass
class LLMRecommendation:
    """Domain entity for LLM recommendations"""
    analysis_id: str
    timestamp: datetime
    prompt_used: str
    context_data: Dict[str, Any]
    analysis: str
    recommendations: List[Dict[str, Any]]
    metrics_analyzed: Dict[str, float]
    anomalies_detected: List[str]
    priority_actions: List[Dict[str, Any]]
    data_sources: List[str]
    model_used: str
    processing_time: float
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            'analysis_id': self.analysis_id,
            'timestamp': self.timestamp,
            'prompt_used': self.prompt_used,
            'context_data': self.context_data,
            'analysis': self.analysis,
            'recommendations': self.recommendations,
            'metrics_analyzed': self.metrics_analyzed,
            'anomalies_detected': self.anomalies_detected,
            'priority_actions': self.priority_actions,
            'data_sources': self.data_sources,
            'model_used': self.model_used,
            'processing_time': self.processing_time,
            'created_at': self.created_at
        }