from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class MCPAction:
    """MCP Action domain entity"""
    action_type: str
    parameters: Dict[str, Any]
    target: str  # 'mongodb' or 'csv'
    executed_at: datetime = None
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.executed_at is None:
            self.executed_at = datetime.now()