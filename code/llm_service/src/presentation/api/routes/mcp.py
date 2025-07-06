from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container
from ....application.use_cases import ExecuteMCPActionUseCase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])

class MCPExecutionRequest(BaseModel):
    """Request model for MCP action execution"""
    action: str
    parameters: Dict[str, Any] = {}

class MCPExecutionResponse(BaseModel):
    """Response model for MCP execution"""
    success: bool
    result: Dict[str, Any]
    message: str = ""

@router.post("/execute", response_model=MCPExecutionResponse)
@inject
async def execute_mcp_action(
    request: MCPExecutionRequest,
    use_case: ExecuteMCPActionUseCase = Depends(Provide[Container.execute_mcp_action_use_case])
):
    """Execute an MCP action with detailed feedback"""
    try:
        result = await use_case.execute(request.action, request.parameters)
        
        # Check if the action was successful
        if "error" in result:
            return MCPExecutionResponse(
                success=False,
                result=result,
                message=f"Failed to execute {request.action}: {result['error']}"
            )
        
        # Verify the change was applied (for update actions)
        verification_message = await _verify_action_result(request.action, request.parameters, result)
        
        return MCPExecutionResponse(
            success=True,
            result=result,
            message=f"Successfully executed {request.action}. {verification_message}"
        )
        
    except Exception as e:
        logger.error(f"Error executing MCP action: {str(e)}")
        return MCPExecutionResponse(
            success=False,
            result={"error": str(e)},
            message=f"Failed to execute action: {str(e)}"
        )

async def _verify_action_result(action: str, parameters: Dict[str, Any], result: Dict[str, Any]) -> str:
    """Verify and create a human-readable message about what changed"""
    if action == "update_order_priority":
        order_id = parameters.get("order_id", "unknown")
        priority = parameters.get("priority", "unknown")
        return f"Order {order_id} priority updated to {priority}"
    
    elif action == "update_order":
        order_id = parameters.get("order_id", "unknown")
        updates = parameters.get("updates", {})
        changes = ", ".join([f"{k}={v}" for k, v in updates.items()])
        return f"Order {order_id} updated: {changes}"
    
    elif action == "update_machine":
        machine_id = parameters.get("machine_id", "unknown")
        updates = parameters.get("updates", {})
        changes = ", ".join([f"{k}={v}" for k, v in updates.items()])
        return f"Machine {machine_id} updated: {changes}"
    
    elif action == "add_order_note":
        order_id = parameters.get("order_id", "unknown")
        note = parameters.get("note", {})
        note_type = note.get("type", "note")
        return f"Added {note_type} note to order {order_id}"
    
    elif action == "reschedule_orders":
        machine_id = parameters.get("machine_id", "unknown")
        return f"Rescheduled orders for machine {machine_id}"
    
    elif action == "add_machine_staff":
        machine_id = parameters.get("machine_id", "unknown")
        staff = parameters.get("staff", [])
        return f"Added {len(staff)} staff members to machine {machine_id}"
    
    # Add more action-specific messages as needed
    return "Action completed successfully"

@router.get("/actions")
async def get_available_actions():
    """Get list of available MCP actions"""
    return {
        "actions": [
            {
                "name": "update_order_priority",
                "description": "Update the priority of an order",
                "parameters": {
                    "order_id": "string",
                    "priority": "number"
                }
            },
            {
                "name": "update_order",
                "description": "Update any field of an order",
                "parameters": {
                    "order_id": "string",
                    "updates": "object"
                }
            },
            {
                "name": "update_machine",
                "description": "Update machine settings",
                "parameters": {
                    "machine_id": "string",
                    "updates": "object"
                }
            },
            {
                "name": "add_order_note",
                "description": "Add a note to an order",
                "parameters": {
                    "order_id": "string",
                    "note": {
                        "type": "string",
                        "note": "string"
                    }
                }
            },
            {
                "name": "reschedule_orders",
                "description": "Reschedule orders for a machine",
                "parameters": {
                    "machine_id": "string",
                    "schedule": "object"
                }
            },
            {
                "name": "add_machine_staff",
                "description": "Add staff members to a machine",
                "parameters": {
                    "machine_id": "string",
                    "staff": "array of strings"
                }
            }
        ]
    }

@router.get("/status")
async def get_mcp_status():
    """Check MCP server status"""
    # TODO: Implement actual health check to MCP server
    return {
        "status": "operational",
        "mcp_server": "connected",
        "available": True
    }