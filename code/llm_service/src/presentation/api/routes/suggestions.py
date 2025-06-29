from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container
from ....application.use_cases import GetSuggestionsUseCase
from ....application.dto import SuggestionsResponseDTO
from datetime import datetime

router = APIRouter(prefix="/api/v1/suggestions", tags=["suggestions"])

class SuggestionsRequest(BaseModel):
    metrics: Dict[str, Any]

@router.post("/", response_model=SuggestionsResponseDTO)
@inject
async def get_suggestions(
    request: SuggestionsRequest,
    use_case: GetSuggestionsUseCase = Depends(Provide[Container.get_suggestions_use_case])
):
    """Get improvement suggestions based on metrics"""
    try:
        suggestions = await use_case.execute(request.metrics)
        
        return SuggestionsResponseDTO(
            suggestions=suggestions,
            metrics_analyzed=request.metrics,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))