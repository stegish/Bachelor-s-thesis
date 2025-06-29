from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class ChatMessage:
    """Chat message entity"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ChatSession:
    """Chat session domain entity"""
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str):
        """Add a message to the session"""
        self.messages.append(ChatMessage(role=role, content=content))
        self.last_activity = datetime.now()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history for LLM context"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]