import httpx
import logging
from typing import Dict, Any, List
from ...domain.interfaces import IMCPService

logger = logging.getLogger(__name__)

class MCPClient(IMCPService):
    """Client for MCP Server communication"""
    
    def __init__(self, mcp_server_url: str):
        self.base_url = mcp_server_url
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        logger.info(f"MCP Client initialized with URL: {self.base_url}")
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action through MCP"""
        try:
            logger.info(f"Attempting to execute MCP action: {action} with parameters: {parameters}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                endpoint = self._get_endpoint_for_action(action)
                
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=parameters  # Send parameters directly, not wrapped
                )
                
                if response.status_code >= 400:
                    error_detail = response.json() if response.content else {"detail": "Unknown error"}
                    logger.error(f"MCP server returned error {response.status_code}: {error_detail}")
                    return {
                        "success": False,
                        "error": f"MCP server error: {error_detail.get('detail', 'Unknown error')}"
                    }
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"MCP action {action} executed successfully")
                return result
                
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to MCP server at {self.base_url}: {str(e)}")
            return {
                "success": False,
                "error": f"Cannot connect to MCP server: {str(e)}"
            }
        except httpx.TimeoutException as e:
            logger.error(f"MCP server timeout: {str(e)}")
            return {
                "success": False, 
                "error": f"MCP server timeout: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error executing MCP action: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def query_mongodb(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query MongoDB through MCP"""
        result = await self.execute_action("query_database", {
            "collection": collection,
            "query": query
        })
        
        if result.get("success", False):
            return result.get("data", [])
        else:
            logger.error(f"Failed to query MongoDB: {result.get('error')}")
            return []
    
    async def read_csv(self, filename: str) -> Dict[str, Any]:
        """Read CSV through MCP"""
        result = await self.execute_action("read_csv", {
            "filename": filename
        })
        
        return result
    
    async def write_csv(self, filename: str, data: Dict[str, Any]) -> bool:
        """Write CSV through MCP"""
        result = await self.execute_action("write_csv", {
            "filename": filename,
            "data": data
        })
        
        return result.get("success", False)
    
    def _get_endpoint_for_action(self, action: str) -> str:
        """Map action names to MCP endpoints"""
        endpoints = {
            "query_database": "/tools/query_database",
            "read_csv": "/tools/read_csv",
            "write_csv": "/tools/write_csv",
            "get_insights": "/tools/get_insights",
            "trigger_action": "/tools/trigger_action",
            "update_order": "/tools/update_order",
            "update_order_priority": "/tools/update_order_priority",
            "update_machine": "/tools/update_machine",
            "add_order_note": "/tools/add_order_note",
            "reschedule_orders": "/tools/reschedule_orders",
            "add_machine_staff": "/tools/add_machine_staff"
        }
        
        return endpoints.get(action, f"/tools/{action}")