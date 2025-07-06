# File: llm_service/src/domain/interfaces/__init__.py

from .llm_service import ILLMService
from .context_repository import IContextRepository
from .file_processor import IFileProcessor
from .mcp_service import IMCPService
from .recommendation_repository import IRecommendationRepository

# Se ci sono altre interfacce, includile qui
# Per esempio:
# from .chat_repository import IChatRepository

__all__ = [
    'ILLMService', 
    'IContextRepository', 
    'IFileProcessor', 
    'IMCPService', 
    'IRecommendationRepository'
]