class DomainException(Exception):
    """Base domain exception"""
    pass

class InvalidFileException(DomainException):
    """Raised when file is invalid"""
    def __init__(self, filename: str, reason: str):
        super().__init__(f"Invalid file {filename}: {reason}")
        self.filename = filename
        self.reason = reason

class AnalysisException(DomainException):
    """Raised when analysis fails"""
    def __init__(self, message: str):
        super().__init__(f"Analysis failed: {message}")

class ContextNotFoundException(DomainException):
    """Raised when context is not found"""
    def __init__(self, context_type: str):
        super().__init__(f"Context not found: {context_type}")
        self.context_type = context_type

class SessionNotFoundException(DomainException):
    """Raised when session is not found"""
    def __init__(self, session_id: str):
        super().__init__(f"Session not found: {session_id}")
        self.session_id = session_id