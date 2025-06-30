from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..entities.llm_recommendation import LLMRecommendation

class IRecommendationRepository(ABC):
    """Repository interface for LLM recommendations"""
    
    @abstractmethod
    async def save_recommendation(self, recommendation: LLMRecommendation) -> str:
        """Save recommendation and return ID"""
        pass
    
    @abstractmethod
    async def get_latest_recommendation(self) -> Optional[LLMRecommendation]:
        """Get the most recent recommendation"""
        pass
    
    @abstractmethod
    async def get_recommendations_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[LLMRecommendation]:
        """Get recommendations within date range"""
        pass
    
    @abstractmethod
    async def get_recommendation_by_id(self, analysis_id: str) -> Optional[LLMRecommendation]:
        """Get specific recommendation by ID"""
        pass