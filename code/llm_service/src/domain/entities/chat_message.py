# Se hai già altri file entities, aggiungi questo a un nuovo file:
# File: llm_service/src/domain/entities/chat_message.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class ChatMessage:
    """Chat message entity"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# E poi aggiungi al file __init__.py:
# from .chat_message import ChatMessage