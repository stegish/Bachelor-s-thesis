from abc import ABC, abstractmethod
from typing import Dict, Any, List

class IMCPClient(ABC):
    """Interface for MCP client"""
    
    @abstractmethod
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP action"""
        pass
    
    @abstractmethod
    async def query_mongodb(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query MongoDB through MCP"""
        pass
    
    @abstractmethod
    async def read_csv(self, filename: str) -> Dict[str, Any]:
        """Read CSV through MCP"""
        pass
    
    @abstractmethod
    async def write_csv(self, filename: str, data: Dict[str, Any]) -> bool:
        """Write CSV through MCP"""
        pass