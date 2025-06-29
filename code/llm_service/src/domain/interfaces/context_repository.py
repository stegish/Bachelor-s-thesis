# src/domain/interfaces/context_repository.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..entities import AnalysisRequest, AnalysisResult

class IContextRepository(ABC):
    """Repository interface for context management"""
    
    @abstractmethod
    async def get_context(self, question: str) -> Dict[str, Any]:
        """Retrieve relevant context based on question"""
        pass
    
    @abstractmethod
    async def save_history(self, request: AnalysisRequest, result: AnalysisResult) -> None:
        """Save analysis history"""
        pass
    
    @abstractmethod
    async def get_orders_context(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent orders for context"""
        pass
    
    @abstractmethod
    async def get_machines_context(self) -> List[Dict[str, Any]]:
        """Get machines information"""
        pass