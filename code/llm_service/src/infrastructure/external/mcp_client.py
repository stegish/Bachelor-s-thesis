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
        """Execute MCP action by mapping to the correct endpoint"""
        async with aiohttp.ClientSession() as session:
            try:
                # Map action names to MCP server endpoints
                endpoint_map = {
                    'schedule_order': '/tools/schedule_order',
                    'add_machine_staff': '/tools/add_machine_staff',
                    'reschedule_orders': '/tools/reschedule_machine_orders',
                    'update_order': '/tools/update_order',
                    'update_order_priority': '/tools/update_order',
                    'update_phase': '/tools/update_phase',
                    'add_order_note': '/tools/add_order_note',
                    'update_machine': '/tools/update_machine',
                    'update_shift': '/tools/update_shift',
                    'query_database': '/tools/query_database',
                    'read_csv': '/tools/read_csv_file',
                    'get_production_status': '/tools/get_production_status'
                }
                
                endpoint = endpoint_map.get(action)
                if not endpoint:
                    logger.error(f"Unknown MCP action: {action}")
                    return {"error": f"Unknown action: {action}"}

                # Parameter adaptation for backward-compatible commands
                if action == 'update_order_priority':
                    # allow simpler payloads like {"order_id": "ID", "priority": 1}
                    priority = parameters.get('priority')
                    if priority is not None:
                        parameters = {
                            'order_id': parameters.get('order_id'),
                            'updates': {'priority': priority}
                        }

                # Make the request to the MCP server
                async with session.post(
                    f"{self.mcp_server_url}{endpoint}",
                    json=parameters,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()
                    
                    if response.status != 200:
                        logger.error(f"MCP server returned error: {result}")
                        return {"error": result.get("detail", "Unknown error")}
                    
                    return result
                    
            except aiohttp.ClientError as e:
                logger.error(f"Network error executing MCP action: {str(e)}")
                return {"error": f"Network error: {str(e)}"}
            except Exception as e:
                logger.error(f"Error executing MCP action: {str(e)}")
                return {"error": str(e)}
    
    async def query_mongodb(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query MongoDB through MCP"""
        result = await self.execute_action("query_database", {
            "collection": collection,
            "filter": query,
            "limit": 100
        })
        return result.get("data", [])
    
    async def read_csv(self, filename: str) -> Dict[str, Any]:
        """Read CSV through MCP"""
        return await self.execute_action("read_csv", {"filename": filename})
    
    async def write_csv(self, filename: str, data: Dict[str, Any]) -> bool:
        """Write CSV through MCP"""
        # This endpoint might not exist in the current MCP server
        result = await self.execute_action("write_csv", {
            "filename": filename,
            "data": data
        })
        return result.get("success", False)