from typing import Dict, Any, Optional
from ...domain.entities import ChatSession
from collections import defaultdict

class MemoryChatRepository:
    """In-memory chat session repository"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session"""
        return self.sessions.get(session_id)
    
    async def save_session(self, session: ChatSession) -> None:
        """Save chat session"""
        self.sessions[session.session_id] = session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
