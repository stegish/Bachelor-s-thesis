from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..entities import AnalysisRequest, AnalysisResult

class ILLMService(ABC):
    """Interface for LLM service following Interface Segregation Principle"""
    
    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Analyze data with LLM"""
        pass
    
    @abstractmethod
    async def chat(self, message: str, session_id: str) -> str:
        """Chat with context"""
        pass