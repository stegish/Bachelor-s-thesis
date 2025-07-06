# File: llm_service/src/domain/entities/__init__.py

from .analysis_request import AnalysisRequest
from .analysis_result import AnalysisResult
from .orders import Order
from .phase import Phase
from .chat_session import ChatSession, ChatMessage  # IMPORTANTE: Importa anche ChatMessage
from .manufacturing_context import ManufacturingContext
from .mcp_action import MCPAction
from .llm_recommendation import LLMRecommendation

__all__ = [
    'AnalysisRequest', 
    'AnalysisResult', 
    'Order', 
    'Phase',
    'ChatSession', 
    'ChatMessage',  # IMPORTANTE: Esporta anche ChatMessage
    'ManufacturingContext', 
    'MCPAction',
    'LLMRecommendation'
]