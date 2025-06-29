from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class SessionId:
    """Session ID value object"""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Session ID cannot be empty")
    
    @classmethod
    def generate(cls) -> 'SessionId':
        """Generate new session ID"""
        return cls(str(uuid.uuid4()))
