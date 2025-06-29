import aiohttp
from typing import Dict, Any, List
from ...domain.interfaces import IMCPService
import logging

logger = logging.getLogger(__name__)

class MCPClient(IMCPService):
    """MCP client implementation"""
    
    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP action"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.mcp_server_url}/execute",
                    json={"action": action, "parameters": parameters}
                ) as response:
                    return await response.json()
            except Exception as e:
                logger.error(f"Error executing MCP action: {str(e)}")
                return {"error": str(e)}
    
    async def query_mongodb(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query MongoDB through MCP"""
        result = await self.execute_action("mongodb_query", {
            "collection": collection,
            "query": query
        })
        return result.get("data", [])
    
    async def read_csv(self, filename: str) -> Dict[str, Any]:
        """Read CSV through MCP"""
        return await self.execute_action("read_csv", {"filename": filename})
    
    async def write_csv(self, filename: str, data: Dict[str, Any]) -> bool:
        """Write CSV through MCP"""
        result = await self.execute_action("write_csv", {
            "filename": filename,
            "data": data
        })
        return result.get("success", False)
