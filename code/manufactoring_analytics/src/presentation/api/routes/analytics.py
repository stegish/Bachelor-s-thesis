from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
from ....infrastructure.config import Container
from ....application.dto import GenerateAnalyticsRequest, GenerateAnalyticsResponse
from ....application.use_cases import GenerateAnalyticsUseCase
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/run")
@inject
async def generate_analytics(
    background_tasks: BackgroundTasks,
    force: bool = False,
    use_case: GenerateAnalyticsUseCase = Depends(Provide[Container.generate_analytics_use_case])
) -> GenerateAnalyticsResponse:
    """Generate manufacturing analytics"""
    try:
        request = GenerateAnalyticsRequest(
            output_directory="./analytics_output",
            force_regenerate=force
        )
        
        # Run analytics generation
        result = await use_case.execute(request.output_directory)
        
        return GenerateAnalyticsResponse(
            status="success",
            message="Analytics generation completed",
            timestamp=datetime.now(),
            files_generated=result['files_generated'],
            summary=result['summary']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
@inject
async def get_analytics_status(
    use_case = Depends(Provide[Container.get_analytics_status_use_case])
) -> Dict[str, Any]:
    """Get current analytics generation status"""
    from ....application.dto import GetAnalyticsStatusRequest
    
    request = GetAnalyticsStatusRequest(include_history=True, limit=10)
    result = await use_case.execute(request)
    
    return result.dict()

@router.get("/summary")
@inject
async def get_analytics_summary(
    analytics_repo = Depends(Provide[Container.analytics_repository])
) -> Dict[str, Any]:
    """Get latest analytics summary"""
    latest = await analytics_repo.get_latest_result()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No analytics results found")
    
    return latest.to_dict()