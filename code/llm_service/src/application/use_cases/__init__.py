from .analyze_data import AnalyzeDataUseCase
from .process_csv import ProcessCSVUseCase
from .chat import ChatUseCase
from .execute_mcp_action import ExecuteMCPActionUseCase
from .get_suggestions import GetSuggestionsUseCase
from .generate_recommendation import GenerateRecommendationUseCase  # ADD THIS LINE

__all__ = [
    'AnalyzeDataUseCase', 'ProcessCSVUseCase', 'ChatUseCase',
    'ExecuteMCPActionUseCase', 'GetSuggestionsUseCase',
    'GenerateRecommendationUseCase'  # ADD THIS LINE
]