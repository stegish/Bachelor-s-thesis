from typing import Dict, Any
from ...domain.interfaces import ILLMService, IContextRepository

class ChatUseCase:
    """Use case for chat functionality"""
    
    def __init__(self, llm_service: ILLMService, context_repository: IContextRepository):
        self.llm_service = llm_service
        self.context_repository = context_repository
    
    async def execute(self, message: str, session_id: str) -> str:
        """Execute chat use case"""
        # Get context for the session
        context = await self.context_repository.get_context(message)
        
        # Call LLM service with context
        response = await self.llm_service.chat(message, session_id)
        
        return response