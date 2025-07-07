from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from typing import Any, Dict
from ....infrastructure.config import Container
from ....application.use_cases import ExecuteMCPActionUseCase

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])

class MCPActionRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]

class MCPActionResponse(BaseModel):
    success: bool
    message: str
    result: Any = None
    error: str = None

@router.post("/execute", response_model=MCPActionResponse)
@inject
async def execute_mcp_action(
    request: MCPActionRequest,
    use_case: ExecuteMCPActionUseCase = Depends(Provide[Container.execute_mcp_action_use_case])
):
    """Execute an MCP action"""
    try:
        result = await use_case.execute(
            action=request.action,  # CHANGED: action instead of action_name
            parameters=request.parameters
        )
        
        # Check if the result indicates an error
        if isinstance(result, dict) and result.get('error'):
            # Return error response with proper status code
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail={
                    "success": False,
                    "message": "Failed to execute MCP action",
                    "error": result.get('error', 'Unknown error occurred')
                }
            )
        
        return MCPActionResponse(
            success=True,
            message=f"Successfully executed {request.action}",
            result=result
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error executing MCP action {request.action}: {str(e)}")
        
        # Return proper error response
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "message": f"Failed to execute {request.action}",
                "error": str(e)
            }
        )