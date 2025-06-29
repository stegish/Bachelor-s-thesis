from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container
from ....application.use_cases import ExecuteMCPActionUseCase

router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])

class MCPActionRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]

@router.post("/execute")
@inject
async def execute_mcp_action(
    request: MCPActionRequest,
    use_case: ExecuteMCPActionUseCase = Depends(Provide[Container.execute_mcp_action_use_case])
):
    """Execute MCP action"""
    try:
        result = await use_case.execute(request.action, request.parameters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
