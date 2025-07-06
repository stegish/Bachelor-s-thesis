# File: llm_service/src/domain/interfaces/chat_repository.py

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities import ChatSession, ChatMessage

class IChatRepository(ABC):
    """Interface for chat repository"""
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        pass
    
    @abstractmethod
    async def save_session(self, session: ChatSession) -> None:
        """Save chat session"""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete chat session"""
        pass
    
    @abstractmethod
    async def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages from a session"""
        pass