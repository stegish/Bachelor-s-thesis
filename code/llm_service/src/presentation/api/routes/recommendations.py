from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from ....infrastructure.config import Container
from ....application.use_cases import GenerateRecommendationUseCase
from ....domain.entities.llm_recommendation import LLMRecommendation

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])

class GenerateRecommendationRequest(BaseModel):
    """Request model for generating recommendations"""
    custom_prompt: Optional[str] = None

class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    analysis_id: str
    timestamp: str
    analysis: str
    recommendations: List[dict]
    anomalies_detected: List[str]
    priority_actions: List[dict]
    metrics_analyzed: dict
    processing_time: float
    
    model_config = {
        'protected_namespaces': ()
    }

@router.post("/generate", response_model=RecommendationResponse)
@inject
async def generate_recommendation(
    request: GenerateRecommendationRequest = GenerateRecommendationRequest(),
    use_case: GenerateRecommendationUseCase = Depends(Provide[Container.generate_recommendation_use_case])
):
    """
    Generate a new recommendation by analyzing latest CSV data and MongoDB context.
    This will automatically:
    1. Fetch latest CSV data from manufacturing analytics service
    2. Get current MongoDB context
    3. Analyze with LLM
    4. Save to MongoDB Atlas AI-manager.LLM-recommendations collection
    """
    try:
        recommendation = await use_case.execute(request.custom_prompt)
        
        return RecommendationResponse(
            analysis_id=recommendation.analysis_id,
            timestamp=recommendation.timestamp.isoformat(),
            analysis=recommendation.analysis,
            recommendations=recommendation.recommendations,
            anomalies_detected=recommendation.anomalies_detected,
            priority_actions=recommendation.priority_actions,
            metrics_analyzed=recommendation.metrics_analyzed,
            processing_time=recommendation.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=RecommendationResponse)
@inject
async def get_latest_recommendation(
    recommendation_repo = Depends(Provide[Container.recommendation_repository])
):
    """Get the most recent recommendation"""
    recommendation = await recommendation_repo.get_latest_recommendation()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="No recommendations found")
    
    return RecommendationResponse(
        analysis_id=recommendation.analysis_id,
        timestamp=recommendation.timestamp.isoformat(),
        analysis=recommendation.analysis,
        recommendations=recommendation.recommendations,
        anomalies_detected=recommendation.anomalies_detected,
        priority_actions=recommendation.priority_actions,
        metrics_analyzed=recommendation.metrics_analyzed,
        processing_time=recommendation.processing_time
    )

@router.get("/history")
@inject
async def get_recommendation_history(
    days: int = Query(default=7, ge=1, le=30, description="Number of days to look back"),
    recommendation_repo = Depends(Provide[Container.recommendation_repository])
):
    """Get recommendation history for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    recommendations = await recommendation_repo.get_recommendations_by_date_range(
        start_date, end_date
    )
    
    return {
        "count": len(recommendations),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "recommendations": [
            {
                "analysis_id": r.analysis_id,
                "timestamp": r.timestamp.isoformat(),
                "anomalies_count": len(r.anomalies_detected),
                "recommendations_count": len(r.recommendations),
                "priority_actions_count": len(r.priority_actions),
                "metrics": r.metrics_analyzed
            }
            for r in recommendations
        ]
    }

@router.get("/{analysis_id}", response_model=RecommendationResponse)
@inject
async def get_recommendation_by_id(
    analysis_id: str,
    recommendation_repo = Depends(Provide[Container.recommendation_repository])
):
    """Get a specific recommendation by ID"""
    recommendation = await recommendation_repo.get_recommendation_by_id(analysis_id)
    
    if not recommendation:
        raise HTTPException(status_code=404, detail=f"Recommendation {analysis_id} not found")
    
    return RecommendationResponse(
        analysis_id=recommendation.analysis_id,
        timestamp=recommendation.timestamp.isoformat(),
        analysis=recommendation.analysis,
        recommendations=recommendation.recommendations,
        anomalies_detected=recommendation.anomalies_detected,
        priority_actions=recommendation.priority_actions,
        metrics_analyzed=recommendation.metrics_analyzed,
        processing_time=recommendation.processing_time
    )

@router.post("/generate-and-notify")
@inject
async def generate_and_notify(
    request: GenerateRecommendationRequest = GenerateRecommendationRequest(),
    use_case: GenerateRecommendationUseCase = Depends(Provide[Container.generate_recommendation_use_case])
):
    """
    Generate recommendation and return a summary suitable for notifications.
    This endpoint is useful for scheduled jobs or alerts.
    """
    try:
        recommendation = await use_case.execute(request.custom_prompt)
        
        # Create notification-friendly summary
        summary = {
            "analysis_id": recommendation.analysis_id,
            "timestamp": recommendation.timestamp.isoformat(),
            "critical_findings": {
                "anomalies_detected": len(recommendation.anomalies_detected),
                "priority_actions_required": len(recommendation.priority_actions),
                "recommendations_count": len(recommendation.recommendations)
            },
            "top_issues": recommendation.anomalies_detected[:3],
            "immediate_actions": [
                action['description'] 
                for action in recommendation.priority_actions 
                if action.get('urgency') == 'critical'
            ][:3],
            "metrics_summary": {
                "machine_utilization": recommendation.metrics_analyzed.get('avg_machine_utilization', 'N/A'),
                "on_time_delivery": recommendation.metrics_analyzed.get('on_time_delivery_rate', 'N/A'),
                "completion_rate": recommendation.metrics_analyzed.get('order_completion_rate', 'N/A')
            },
            "saved_to_database": True,
            "database": "AI-manager",
            "collection": "LLM-recommendations"
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))