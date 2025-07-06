import httpx
import logging
from typing import Dict, Any
from ...domain.interfaces import IMCPClient

logger = logging.getLogger(__name__)

class MCPClient(IMCPClient):
    """Client for MCP Server communication"""
    
    def __init__(self, mcp_server_url: str):
        self.base_url = mcp_server_url
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        logger.info(f"MCP Client initialized with URL: {self.base_url}")
    
    async def execute_action(self, action_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action through MCP"""
        try:
            # Log the attempt
            logger.info(f"Attempting to execute MCP action: {action_name} with parameters: {parameters}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Determine the correct endpoint based on action
                endpoint = self._get_endpoint_for_action(action_name)
                
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=parameters
                )
                
                # Check response status
                if response.status_code >= 400:
                    error_detail = response.json() if response.content else {"detail": "Unknown error"}
                    logger.error(f"MCP server returned error {response.status_code}: {error_detail}")
                    return {
                        "success": False,
                        "error": f"MCP server error: {error_detail.get('detail', 'Unknown error')}"
                    }
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"MCP action {action_name} executed successfully")
                return result
                
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to MCP server at {self.base_url}: {str(e)}")
            return {
                "success": False,
                "error": f"Cannot connect to MCP server. Please ensure it's running at {self.base_url}"
            }
        except httpx.TimeoutException as e:
            logger.error(f"Timeout executing MCP action {action_name}: {str(e)}")
            return {
                "success": False,
                "error": "Request timeout - MCP server took too long to respond"
            }
        except Exception as e:
            logger.error(f"Unexpected error executing MCP action {action_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _get_endpoint_for_action(self, action_name: str) -> str:
        """Map action names to MCP endpoints"""
        endpoints = {
            'update_order': '/tools/update_order',
            'update_order_priority': '/tools/update_order_priority',
            'update_machine': '/tools/update_machine',
            'add_order_note': '/tools/add_order_note',
            'reschedule_orders': '/tools/reschedule_orders',
            'add_machine_staff': '/tools/add_machine_staff'
        }
        return endpoints.get(action_name, f'/tools/{action_name}')
